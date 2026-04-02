from typing import TypedDict # Imports all the data types we need
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    name: str
    age: str
    final: str


def first_node(mystate: AgentState) -> AgentState:
    """This is the first node of our sequence"""

    mystate["final"] = f"Hi {mystate['name']}"
    return mystate

def second_node(mystate: AgentState) -> AgentState:
    """This is the second node of our sequence"""



    # mystate['final'] = f"You are {mystate['age']} years old!" # Logical error, 
    # as this completely replaces the state,below one is the correct one

    mystate['final'] = mystate["final"] + f"You are {mystate['age']} years old!"
    return mystate



graph = StateGraph(AgentState)
graph.add_node("first_node",first_node)
graph.add_node("second_node",second_node)

graph.set_entry_point("first_node")
graph.add_edge("first_node", "second_node") # we add an edge from the first node to the second node, creating a sequence
graph.set_finish_point("second_node")
app = graph.compile()


