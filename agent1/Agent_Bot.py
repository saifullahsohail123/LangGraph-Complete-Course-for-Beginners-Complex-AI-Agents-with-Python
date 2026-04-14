from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv


load_dotenv()


class AgentState(TypedDict):
    message: List[HumanMessage] # list of human messages


llm = ChatOllama(model="llama3.2:latest")

def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["message"])
    print(f"Agent Response: {response.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()


user_input = input("Enter: ")
while user_input != "exit":
    result = agent.invoke({"message": [HumanMessage(content=user_input)]})
    user_input = input("Enter: ")