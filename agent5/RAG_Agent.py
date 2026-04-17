from typing import Annotated, Sequence, TypedDict
import os
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage # The foundational class for all message types in Langraph
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content  and the tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM
from langchain_core.messages import HumanMessage # Message for defining HumanMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from langgraph.prebuilt import ToolNode


load_dotenv()

llm = ChatOllama(model="llama3.2:latest", temperature=0)


# Our Embedding Model - has to be compatible with LLM used
embeddings = OllamaEmbeddings(model="nomic-embed-text")


pdf_path = os.path.join(os.path.dirname(__file__), "Annual-Report-2025.pdf")

# safety mesaure
if not os.path.exists(pdf_path):
    raise FileNotFoundError("File does not exsists")

pdf_loader = PyPDFLoader(pdf_path)

try:
    pages = pdf_loader.load()
    print(f"Successfully loaded {len(pages)} pages from the PDF.")
except:
    print("Failed to load PDF. Please check the file path and ensure the file is not corrupted.")
    raise

# Chunking process
text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)

pages_split = text_splitter.split_documents(pages) # We now apply to our pages. above we defined the splitter

persistent_directory = os.path.join(os.path.dirname(__file__), "chroma_db")
collection_name = "stock_market"

# If our collection does not exsist in the directory, we create using the os command
if not os.path.exists(persistent_directory):
    os.makedirs(persistent_directory)


try:
    # Here we actually create the vectors, using chroma and the embeddings we defined above. We also specify where to persist the data and the name of the collection
    vectorstore = Chroma.from_documents(documents=pages_split, embedding=embeddings, 
                                        persist_directory= persistent_directory, collection_name=collection_name)
    print("Successfully created Chroma vector store and persisted it to disk.")
except Exception as e:
    print(f"Error setting up ChromDB: {str(e)}")
    raise

class AgentState(TypedDict):
    messages:  Annotated[Sequence[BaseMessage], add_messages] # It says to use Annotaed Sequence of Base Messages that have a reducer add_message


# No we create our retriever that will retrieve the chunks
retriever = vectorstore.as_retriever(
    search_type = 'similarity',
    search_kwargs = {"k":5} # k is the amount of chunks to return
)

@tool

def retriever_tool(query: str) -> str:
    """
    This tool searches and returns information from the Stock Market Performance 2025, document.
    """
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information found in the document."
    
    results = []
    for i,doc in enumerate(docs):
        results.append(f"Documents {i+1}:\n {doc.page_content}")

    return "\n\n".join(results)


tools = [retriever_tool]

llm = llm.bind_tools(tools)


def should_continue(state: AgentState):
    """Check if the last message contain tool calls."""
    result = state["messages"][-1]
    return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0


system_prompt = """
You are an intelligent AI assistant who answers questions about Stock Market Performance in 2025 based on the PDF document loaded into your knowledge base.
Use the retriever tool available to answer questions about the stock market performance data. You can make multiple calls if needed.
If you need to look up some information before asking a follow up question, you are allowed to do that!
Please always cite the specific parts of the documents you use in your answers.
"""

tools_dict = {our_tool.name: our_tool for our_tool in tools} # Creating a dictionary of our tools

# LLM Agent
def call_llm(state: AgentState) -> AgentState:
    """Function to call the LLM with the current state"""
    messages = list(state["messages"])
    messages =  [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)
    return {'messages': [message]}



# Retriever Agent
def take_action(state: AgentState):
    """Execute tool calls from the LLM's response."""

    tool_calls = state['messages'][-1].tool_calls
    results = []
    
    for t in tool_calls:
        print(f"Calling Tool: {t['name']} with query: {t['args'].get('query', 'No query provided')}")

        if not t['name'] in tools_dict:  # Checks if a valid tool is present
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
        
        else:
            result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            print(f"Result length: {len(str(result))}")

        # Appends the Tool Message
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools Execution Complete. Back to the model!")
    return {'messages': results}


graph = StateGraph(AgentState)
graph.add_node("llm",call_llm)
graph.add_node("retriever_agent",take_action)
# graph.add_node("retriever_agent", ToolNode(tools))



graph.add_conditional_edges("llm", should_continue,{
                            True:"retriever_agent",
                            False: END})

graph.add_edge("retriever_agent","llm")
graph.set_entry_point("llm")

rag_agent = graph.compile()


def running_agent():
    print ("\n RAG Agent")
    while True:
        user_input = input("\n What is your question: ")
        if user_input.lower() in ['exit','quit']:
            break
        messages = [HumanMessage(content=user_input)]

        result = rag_agent.invoke({"messages": messages})

        print("\n=== ANSWER ===")
        print(result['messages'][-1].content)


running_agent()