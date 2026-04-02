from typing import  TypedDict, List
from langgraph.graph import StateGraph

# Multiple inputs example
class AgentState(TypedDict):     # Our state shcema
    values: List[int]
    name: str
    result: str

def process_values(mystate: AgentState) -> AgentState:
    """ This function handles multiple different inputs """

    mystate["result"] = f"Hi there {mystate["name"]}! Your sum  = {sum(mystate["values"])}"
    return mystate

# 