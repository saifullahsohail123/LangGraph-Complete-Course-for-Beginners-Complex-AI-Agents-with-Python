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
    instructions = """You are a mathematical AI assistant. You have access to tools for math.
    
    CRITICAL RULES:
    1. NEVER call multiple tools at the same time if one tool depends on the result of another. 
    2. Think step-by-step. If you need to add and then multiply, FIRST call the add tool, WAIT for the observation/result, and THEN call the multiply tool.
    3. NEVER hallucinate or guess variables like 'result' for tool arguments. Only use concrete numbers.
    4. If you are asked to tell a joke, do it after all calculations are complete.
    5. Only Call the tool if needed
    """

    
    # Same thing as above in comments
    response = model.invoke([SystemMessage(instructions)] + state["messages"])
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


inputs = {"messages": [("user", "Add 40 and 12 multiply it with 10, Also tell me a joke")]}
print_stream(app.stream(inputs, stream_mode="values"))






# Reasons for tool calling without needing it


# You are running head-first into the classic quirks of smaller parameter models (like Llama 3.2 1B or 3B). Your prompt is logically perfect for a human or a massive model like GPT-4, but for a smaller local model, it triggered a few well-known failure modes.

# Here is exactly why it ignored your rules, hallucinated variables, and inexplicably called the subtract tool:

# 1. "Tool Greed" and Pattern Completion
# The model sees a list of available tools: [add, multiply, subtract]. Because it is a smaller model, its attention mechanism heavily weights the tools provided in the context. It recognized it needed add and multiply. But once it started generating those tool calls, it fell into a pattern-matching loop.

# It saw subtract sitting there unused and essentially thought: "I should probably use this one too to finish the job." Notice how it used it: subtract(a: result..., b: 0). It literally invented a math operation that does nothing (subtracting zero) just to satisfy its urge to use the remaining tool!