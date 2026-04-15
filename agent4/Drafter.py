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


# ============================================================================
# POTENTIAL ENHANCEMENTS & INTEGRATIONS
# ============================================================================

# 1. ELEVEN LABS INTEGRATION (Text-to-Speech)
# ============================================================================
# Use case: Read the generated email or document content aloud
#
# Implementation:
#   from elevenlabs import ElevenLabs, VoiceSettings
#   
#   def read_document_aloud():
#       client = ElevenLabs(api_key="YOUR_API_KEY")
#       audio = client.text_to_speech.convert(
#           text=document_content,
#           voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
#           model_id="eleven_monolingual_v1"
#       )
#       # Save to file or stream
#       with open("output_audio.mp3", "wb") as f:
#           for chunk in audio:
#               f.write(chunk)
#
# Add a new tool:
#   @tool
#   def read_aloud() -> str:
#       """Read the current document content aloud using Eleven Labs"""
#       # Implementation here
#       return "Document read aloud successfully"


# 2. VOICE INPUT INTEGRATION (Speech-to-Text)
# ============================================================================
# Use case: User speaks commands instead of typing
#
# Implementation options:
#   a) Using OpenAI Whisper:
#       import speech_recognition as sr
#       from openai import OpenAI
#       
#       def get_voice_input():
#           recognizer = sr.Recognizer()
#           with sr.Microphone() as source:
#               print("Listening...")
#               audio = recognizer.listen(source)
#           client = OpenAI()
#           transcript = client.audio.transcriptions.create(
#               model="whisper-1",
#               file=audio
#           )
#           return transcript.text
#
#   b) Using Google Speech Recognition (free):
#       audio_text = recognizer.recognize_google(audio)
#
# Modify our_agent to support voice:
#   def our_agent(state: AgentState) -> AgentState:
#       # ... existing code ...
#       if use_voice_input:
#           user_input = get_voice_input()
#       else:
#           user_input = input("What would you like to do with the document? ")


# 3. KNOWLEDGE BASE INTEGRATION
# ============================================================================
# Use case: Allow the agent to access company documents, policies, FAQs
#
# Implementation with RAG (Retrieval-Augmented Generation):
#   from langchain.vectorstores import FAISS
#   from langchain.embeddings import OpenAIEmbeddings
#   from langchain.document_loaders import DirectoryLoader
#
#   # Load and embed your knowledge base
#   loader = DirectoryLoader("./knowledge_base/")
#   docs = loader.load()
#   embeddings = OpenAIEmbeddings()
#   knowledge_base = FAISS.from_documents(docs, embeddings)
#
#   # Add a retrieval tool
#   @tool
#   def search_knowledge_base(query: str) -> str:
#       """Search the company knowledge base for relevant information"""
#       results = knowledge_base.similarity_search(query, k=3)
#       return "\\n".join([doc.page_content for doc in results])
#
#   tools = [update, save, search_knowledge_base]
#
#   # Update system prompt to mention the knowledge base
#   system_prompt = "You have access to a knowledge base about company policies..."


# 4. INTEGRATION WITH EMAIL SERVICES
# ============================================================================
# Use case: Send the drafted email directly via Gmail/Outlook
#
# Implementation:
#   import smtplib
#   from email.mime.text import MIMEText
#
#   @tool
#   def send_email(recipient: str, subject: str) -> str:
#       """Send the drafted document as an email"""
#       global document_content
#       
#       msg = MIMEText(document_content)
#       msg['Subject'] = subject
#       msg['From'] = "sender@example.com"
#       msg['To'] = recipient
#
#       with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#           server.login("YOUR_EMAIL", "YOUR_PASSWORD")
#           server.send_message(msg)
#       
#       return f"Email sent to {recipient}"


# 5. DOCUMENT FORMAT EXPORTS
# ============================================================================
# Use case: Export to PDF, DOCX, Markdown, etc.
#
# Implementation:
#   from docx import Document
#   from pypdf import PdfWriter
#   import markdown
#
#   @tool
#   def export_to_format(format: str, filename: str) -> str:
#       """Export document to different formats: pdf, docx, md, html"""
#       global document_content
#       
#       if format.lower() == "docx":
#           doc = Document()
#           doc.add_paragraph(document_content)
#           doc.save(filename)
#       elif format.lower() == "md":
#           with open(filename, 'w') as f:
#               f.write(document_content)
#       # ... handle other formats
#       
#       return f"Document exported to {format}"


# 6. MULTI-DOCUMENT MANAGEMENT
# ============================================================================
# Use case: Work with multiple documents simultaneously
#
# Implementation:
#   documents = {}  # Global dict to store multiple documents
#
#   @tool
#   def create_document(doc_name: str) -> str:
#       """Create a new document"""
#       global documents
#       documents[doc_name] = ""
#       return f"Document '{doc_name}' created"
#
#   @tool
#   def switch_document(doc_name: str) -> str:
#       """Switch between open documents"""
#       global document_content, documents
#       if doc_name in documents:
#           document_content = documents[doc_name]
#           return f"Switched to document '{doc_name}'"
#       return f"Document '{doc_name}' not found"


# 7. COLLABORATIVE EDITING WITH DATABASE
# ============================================================================
# Use case: Multiple users editing the same document with version control
#
# Implementation:
#   from sqlalchemy import create_engine
#   from datetime import datetime
#
#   @tool
#   def save_version(version_name: str) -> str:
#       """Save current content as a named version in database"""
#       # Store in database with timestamp and version_name
#       # Can later restore to any version
#
#   @tool
#   def list_versions() -> str:
#       """List all saved versions of the document"""
#       # Query database and return versions


# 8. INTERNET SEARCH INTEGRATION
# ============================================================================
# Use case: Allow agent to search the web for information
#
# Implementation:
#   from langchain.tools import DuckDuckGoSearchRun
#
#   search = DuckDuckGoSearchRun()
#
#   @tool
#   def search_web(query: str) -> str:
#       """Search the internet for information"""
#       return search.run(query)
#
#   tools = [update, save, search_web]


# 9. CUSTOM MODEL FINE-TUNING
# ============================================================================
# Use case: Fine-tune the model on your specific writing style/domain
#
# Implementation:
#   # Collect training data of good documents
#   # Fine-tune using OpenAI's fine-tuning API or use LoRA with local models
#   # Replace: model = ChatOllama(model="base-model")
#   # With: model = ChatOllama(model="fine-tuned-model")


# 10. REAL-TIME COLLABORATION & STREAMING
# ============================================================================
# Use case: Show AI responses as they're being generated (streaming)
#
# Implementation:
#   def our_agent_streaming(state: AgentState) -> AgentState:
#       # Use response = model.stream(...) instead of model.invoke(...)
#       # Print tokens as they arrive in real-time
#       for chunk in response:
#           print(chunk.content, end="", flush=True)