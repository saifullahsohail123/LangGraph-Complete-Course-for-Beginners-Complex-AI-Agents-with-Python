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

def adder_next(mystate: AgentState) -> AgentState:
    """ This node adds the two numbers """

    mystate['final'] = mystate['final'] + mystate['num1'] + mystate['num2']

    return mystate


def subtractor(mystate: AgentState) -> AgentState:
    """ This node subtracts the two numbers """

    mystate['final'] = mystate['num1'] - mystate['num2']

    return mystate


def subtractor_next(mystate: AgentState) -> AgentState:
    """ This node subtracts the two numbers """

    mystate['final'] = mystate['final'] - mystate['num1'] - mystate['num2']

    return mystate


def decide_next_node(mystate: AgentState) -> str:
    """This node will select the next node of the graph"""

    if mystate['operation'] == "+":
        return "addition_operation"
    elif mystate['operation'] == "-":
        return "subtraction_operation"
    



def decide_final(mystate: AgentState) -> str:
    """This node will select the next node of the graph"""

    if mystate['operation'] == "+":
        return "addition_operation2"
    elif mystate['operation'] == "-":
        return "subtraction_operation2"
    

# Define graph, nodes, and overall workflow

graph = StateGraph(AgentState)

graph.add_node("add_node",adder)
graph.add_node("subtract_node",subtractor)

# graph.add_node("router",decide_next_node())   # error as decide_next_node returns a string which is the name of the next node, but it should return a state, we will fix this in the next step

#error
# graph.add_node("router",decide_next_node)    
# Reason
#When you simplified to graph.add_node("router", decide_next_node), LangGraph now properly processes the return value 
#— and chokes on the string. That is it processes the state and expects to receives a state while it receives a str
# and this is the reason it lands an error

# ✅ Router node — just passes state through, does nothing  # lambda state : state is a passthrough
graph.add_node("router", lambda state: state)

# ✅ Router node — just passes state through, does nothing  # lambda state : state is a passthrough
graph.add_node("router2", lambda state: state)

graph.add_node("add_node2",adder_next)
graph.add_node("subtract_node2",subtractor_next)


graph.add_edge(START, "router")

# ✅ Conditional edges — THIS is where decide_next_node actually runs
graph.add_conditional_edges("router", decide_next_node, {
    "addition_operation": "add_node",
    "subtraction_operation": "subtract_node"
})

graph.add_edge("add_node", "router2")
graph.add_edge("subtract_node", "router2")

# ✅ Conditional edges — THIS is where decide_next_node actually runs
graph.add_conditional_edges("router2", decide_final, {
    "addition_operation2": "add_node2",
    "subtraction_operation2": "subtract_node2"
})


graph.add_edge("add_node2", END)
graph.add_edge("subtract_node2", END)

app = graph.compile()

result = app.invoke({"num1": 10, "num2": 5, "operation": "+"})


print('result', result["final"])




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