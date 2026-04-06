from typing import TypedDict, Dict, List
from langgraph.graph import StateGraph, START, END
import random


class AgentState(TypedDict):
    name: str
    number: List[int]
    counter: int # the counter to stop loop


def greeting_node(mystate: AgentState) -> AgentState:
    """Greeting Node which says hi to the person"""
    mystate["name"] = f"Hi there, {mystate['name']}"
    mystate["counter"] = 0 

    return mystate


def random_node(state: AgentState) -> AgentState:
    """Generates a random node from 0 to 10"""
    state["number"].append(random.randint(0,10))
    state["counter"] +=1

    return state


def should_continue(state: AgentState) -> AgentState:   # even the return with str works, this function only does passthrough
    """Function to decide what to do next"""
    if state["counter"] < 5:
        print("Entering loop", state["counter"])
        return "loop"
    else:
        return "exit" # Exit the loop
    
# Expected result
# greeting > random > random > random > random > random > END

graph = StateGraph(AgentState)
graph.add_node("greeting", greeting_node)

graph.add_node("random", random_node)

graph.add_edge("greeting", "random")


graph.add_conditional_edges("random", should_continue,{
    "loop": "random",
    "exit": END
})

# graph.set_entry_point("greeting")
graph.add_edge(START, "greeting")

app = graph.compile()


result = app.invoke({"name": "Alice", "number": [], "counter": -100})

print(result)


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