from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage # The foundational class for all message types in Langraph
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content  and the tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode


# Annotated - provides additional context without affecting the type itself

# for example we define a email as str, it has a specific format. now if a person writes abc-gmail.com ,  It is not a 
# valid email. That is where Annotated comes in.

email = Annotated[str, "This has to be a valid email format!"]
print(email.__metadata__)


# Sequence - To automatically handle the state updates for sequence such as by adding new messages to chat history

# add_message, It is basically a Reducer Function
# Rule that controls how updates from nodes are combined with the exsisting state.
# Tells us how to merge new data into current state

# Without a reducer, updates would have replaced the exsisting value entirely!


# Example
# without reducer
state = {"message": ["Hi!"]}
update = {"message": ["Nice to meet you!"]}
state = {"message": ["Nice to meet you!"]}

# with reducer
state = {"message": ["Hi!"]}
update = {"message": ["Nice to meet you!"]}
state = {"message": ["Hi!,  Nice to meet you!"]} # add_message


class AgentState(TypedDict):
    messages:  Annotated[Sequence[BaseMessage], add_messages] # It says to use Annotaed Sequence of Base Messages that have a reducer add_message


@tool
def add(a: int, b: int):
    """This is an addition function that adds two numbers together""" # if not added, it will give error. docstring is must for Tool call
    
    return a + b

@tool
def subtract(a: int, b: int):
    """Subtraction function""" # if not added, it will give error. docstring is must for Tool call
    
    return a - b


@tool
def multiply(a: int, b: int):
    """Multiplication function""" # if not added, it will give error. docstring is must for Tool call
    
    return a * b


tools = [add, multiply, subtract]

model = ChatOllama(model="llama3.2:latest").bind_tools(tools)


def model_call(state: AgentState) -> AgentState:
    # system_prompt = SystemMessage(content="You are my AI Assistant, please answer my query to the best of your ability")
    # response = model.invoke(system_prompt + state["messages"])
    
    # Same thing as above in comments
    response = model.invoke(["You are my AI Assistant, please answer my query to the best of your ability"] + state["messages"])
    # print(f"DEBUG - Model response tool calls: {response.tool_calls}")
    return {"messages": [response]}



def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
            return "end"
    else:
         return "continue"
    


graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)


graph.set_entry_point("our_agent")
graph.add_conditional_edges("our_agent", should_continue,{
     "continue": "tools",
     "end": END
})
# go either from agent to tool or agent to END


graph.add_edge("tools", "our_agent") # goes back from tools to agent, make it receursive, look in Graph of ReactAgent


app = graph.compile()





def print_stream(stream): # Just a function to beautifully print the whole process
     for s in stream:
          message = s["messages"][-1]
          if isinstance(message, tuple):
            print(tuple)
          else:
            message.pretty_print()


inputs = {"messages": [("user", "Add 3 and 4. Subtract  5 and 10. Multiplty 5 and 20")]}
print_stream(app.stream(inputs, stream_mode="values"))