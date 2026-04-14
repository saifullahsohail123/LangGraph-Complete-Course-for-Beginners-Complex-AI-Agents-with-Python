import os
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

    # print(f"Current State",state["message"])

    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()


# Read the last logging.txt saved and restore conversation history
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "logging.txt")

conversation_history = []

if os.path.exists(log_file):
    print("Loading conversation history from logging.txt...\n")
    with open(log_file, "r") as file:
        lines = file.readlines()
    
    current_message = ""
    for line in lines:
        line = line.strip()
        if line.startswith("You: "):
            if current_message:
                conversation_history.append(AIMessage(content=current_message))
            current_message = ""
            human_content = line.replace("You: ", "")
            conversation_history.append(HumanMessage(content=human_content))
        elif line.startswith("AI: "):
            current_message = line.replace("AI: ", "")
        elif line and line != "Your Conversation History:" and line != "End of Conversation":
            if current_message:
                current_message += "\n" + line
            elif conversation_history and isinstance(conversation_history[-1], HumanMessage):
                current_message = line
    
    if current_message:
        conversation_history.append(AIMessage(content=current_message))
    
    print(f"Loaded {len(conversation_history)} messages from previous conversation.\n")
else:
    print("No logging.txt file found. Starting fresh conversation.\n")


# Continue the conversation with loaded history
user_input = input("Enter: ")
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"message": conversation_history})

    conversation_history = result["message"]

    user_input = input("Enter: ")


# Save the updated conversation history
with open(log_file, "w") as file:
    file.write("Your Conversation History:\n")
    
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation")

print("Conversation saved to logging.txt")
