from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv


load_dotenv()


class AgentState(TypedDict):
    message: List[Union[HumanMessage, AIMessage]] # alternate to seprately storing human and ai message

llm = ChatOllama(model="llama3.2:latest")

def process(state: AgentState) -> AgentState:
    """This node will solve the request you input"""
    response = llm.invoke(state["message"])

    state["message"].append(AIMessage(content=response.content))
    print(f"Agent Response: {response.content}")

    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()


conversation_history = []
user_input = input("Enter: ")
while user_input!= "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"message": conversation_history})

    conversation_history = result["message"]

    user_input = input("Enter: ")