from typing import TypedDict
from langgraph.graph import StateGraph, START, END # This is another way to start and end the graph


class AgentState(TypedDict):
    num1: int
    num2: int
    operation: str
    final: int


def adder(mystate: AgentState) -> AgentState:
    """ This node adds the two numbers """

    mystate['final'] = mystate['num1'] + mystate['num2']

    return mystate


def subtractor(mystate: AgentState) -> AgentState:
    """ This node subtracts the two numbers """

    mystate['final'] = mystate['num1'] - mystate['num2']

    return mystate


def decide_next_node(mystate: AgentState) -> AgentState:
    """This node will select the next node of the graph"""

    if mystate['operation'] == "+":
        return "addition_operation"
    elif mystate['operation'] == "-":
        return "subtraction_operation"
    

# Define graph, nodes, and overall workflow

graph = StateGraph(AgentState)

graph.add_node("add_node",adder)
graph.add_node("subtract_node",subtractor)

# graph.add_node("router",decide_next_node())   # error as decide_next_node returns a string which is the name of the next node, but it should return a state, we will fix this in the next step

graph.add_node("router", lambda state: decide_next_node(state)) # we set is_router to True to indicate that this node will return the name of the next node to execute


graph.add_edge(START, "router")

graph.add_conditional_edges("router", decide_next_node,
                            {
                                # Edge: Node
                                "addition_operation": "add_node",
                                "subtraction_operation": "subtract_node"
                            }) # This will automatically add edges from the router node to the addition_operation and subtraction_operation nodes based on the return value of decide_next_node function



graph.add_edge("add_node", END)
graph.add_edge("subtract_node", END)

app = graph.compile()



# This below code is for plot only


# This import is only for plotting graph, can be ignored if no plot required
import matplotlib.pyplot as plt
from PIL import Image as PILImage
import io




# This is only for plotting graph, can be commmented out if no plot required

# Convert PNG bytes to PIL Image for matplotlib
png_data = app.get_graph().draw_mermaid_png()
img = PILImage.open(io.BytesIO(png_data))

plt.imshow(img)
plt.axis('off') # hide axes
plt.show() # display the graph structure as an image