from typing import  TypedDict, List
from langgraph.graph import StateGraph

# Multiple inputs example
class AgentState(TypedDict):     # Our state shcema
    values: List[int]
    name: str
    result: str

def process_values(mystate: AgentState) -> AgentState:
    """ This function handles multiple different inputs """

    print('\n')

    print(mystate)

    mystate["result"] = f"Hi there {mystate["name"]}! Your sum  = {sum(mystate["values"])}"

    print(mystate)   # mystate["result"]  also gets displayed
    print('\n above two print statments are in the funciton \n ')
    return mystate

# Defining the Graph

graph = StateGraph(AgentState)


graph.add_node("processor", process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile() # Compiling the graph


answers = app.invoke({"name": "Alice", "values": [1, 2, 3]}) # Invoking the graph with multiple inputs

# print(answers) # Printing the entire state after processing
print(answers["result"]) # Printing the result only