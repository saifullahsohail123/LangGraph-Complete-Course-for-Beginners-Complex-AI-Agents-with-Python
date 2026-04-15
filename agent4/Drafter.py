from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage # The foundational class for all message types in Langraph
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content  and the tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM
from langchain_core.messages import HumanMessage # Message for defining HumanMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode


load_dotenv()

#  This is the global variable to store document content
document_content = ""

#correct way to pass state to tool is injected state, we wont be using that. so instead 
# we globally pass the document content instead of injected state

# our tools, whatever update is made, will update the global variable

# save tool will then save contents in a text file


class AgentState(TypedDict):
    messages:  Annotated[Sequence[BaseMessage], add_messages] # It says to use Annotaed Sequence of Base Messages that have a reducer add_message


@tool
def update(content: str) ->str:
    """Updates the document with the provided content. Always pass plain text, not JSON or dicts."""
    global document_content
    # Convert to string if it's a dict or other type
    if isinstance(content, dict):
        content = str(content)
    document_content = str(content)
    return f"Document has been updated with content: {document_content}"

@tool
def save(filename: str) -> str:
    """Save the current document content to a text file and finish the process
    
    Args:
        filename: Name for the  text file
    """

    global document_content

    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"  

    # to make code for robust


    try:
        with open(filename, 'w') as file:
            file.write(document_content)
        print(f"Document content has been saved to {filename}")
        return f"Document content has been saved to {filename}"
    except Exception as e:
        return f"Error saving document: {str(e)}"
    

tools = [update, save]

model = ChatOllama(model="gpt-oss:20b").bind_tools(tools)



def our_agent(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
                                  
    - If the user wants to update or modify content, use the 'update' tool with the COMPLETE updated content as plain text (NOT JSON or dicts).
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to always show the current document state after modification
                                  
    The current document content is: {document_content}

""")

    if not state['messages']:
        user_input = "I'm ready to help you update a document. What would you like to create."
        user_message = HumanMessage(content=user_input)
    else:
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"\n USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"] + [user_message])

    response = model.invoke(all_messages)

    return {"messages": list(state["messages"] + [user_message, response])}


def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation"""
    messages = state["messages"]

    if not messages:
        return "continue"
    
    # Check for exit command
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage) and "exit" in last_message.content.lower():
        return "end"
    
    # This looks for the most recent tool message...
    for message in reversed(messages):
        # Check if the ToolMessage resulting from save
        if (isinstance(message, ToolMessage) and
        "saved" in message.content.lower() and
        "document" in message.content.lower()):
            return "end" # end the program
        
    return "continue"

def print_messages(messages):
    """Function I made to print the messages in a more readable format"""
    if not messages:
        return
    # Only print the very last message to avoid duplication
    message = messages[-1]
    if isinstance(message, ToolMessage):
        print(f"\n🔧 TOOL RESULT: {message.content}")
    elif isinstance(message, HumanMessage):
        print(f"\n👤 USER: {message.content}")
    else:
        # AIMessage
        if message.content:
            print(f"\n🤖 AI: {message.content}")
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_names = [tc['name'] for tc in message.tool_calls]
            print(f"   📞 Calling tools: {tool_names}")


graph = StateGraph(AgentState)
graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")

graph.add_edge("agent", "tools")

graph.add_conditional_edges("tools", should_continue,{
    "continue": "agent",
    "end": END
})


app = graph.compile()


# To invoke the graph

def run_document_agent():
    print("\n === DRAFTER ===")
    state = {"messages":[]}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])

    print("\n ==== DRAFTER FINISHED ====")



if __name__ == "__main__":
    run_document_agent()