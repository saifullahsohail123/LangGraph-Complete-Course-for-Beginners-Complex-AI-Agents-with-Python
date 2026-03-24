from typing import Dict,  TypedDict
from langgraph.graph import StateGraph # framework that helpsy you deisgn and manage the flow of tasks in your
# application, it provides a structured way to define and execute tasks, making it easier to build complex applications.



# We now create an AgentState - shared data structure that keeps track of information as your application runs

class AgentState(TypedDict):     # Our state shcema
    message: str


def greeting_node(mystate: AgentState) -> AgentState:
    """Simple node that addds a greeting message to the state"""
    
    mystate['message'] = f"{mystate["message"]} you're doing an amazing job!" # we update the state with a greeting message
    return mystate

graph = StateGraph(AgentState) 


graph.add_node("greeter" , greeting_node) # we add the node to the graph

graph.set_entry_point("greeter") # we set the entry point of the graph to our greeter node

graph.set_finish_point("greeter") # we set the finish point of the graph to our greeter node

app = graph.compile() # we compile the graph into an executable application


import matplotlib.pyplot as plt
from PIL import Image as PILImage
import io

# Convert PNG bytes to PIL Image for matplotlib
png_data = app.get_graph().draw_mermaid_png()
img = PILImage.open(io.BytesIO(png_data))

plt.imshow(img)
plt.axis('off') # hide axes
plt.show() # display the graph structure as an image



result = app.invoke({"message": "Alice"}) # we invoke the application with an initial state containing a message with the name "Alice"

print(result["message"]) # we print the message in the result state