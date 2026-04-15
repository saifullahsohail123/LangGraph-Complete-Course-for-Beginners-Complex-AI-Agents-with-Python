from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage
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