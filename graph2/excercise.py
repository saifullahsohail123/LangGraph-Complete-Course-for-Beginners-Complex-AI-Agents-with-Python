from typing import  TypedDict, List
from langgraph.graph import StateGraph

# Multiple inputs example
class AgentState(TypedDict):     # Our state shcema
    values: List[int]
    name: str
    result: str
    operation: str

def process_values(mystate: AgentState) -> AgentState:
    """ This function handles multiple different inputs """

    if mystate["operation"] == '+':

        print('\n')

        print(mystate)

        mystate["result"] = f"Hi there {mystate["name"]}! Your sum  = {sum(mystate["values"])}"

        print(mystate)   # mystate["result"]  also gets displayed
        print('\n above two print statments are in the funciton \n ')

    
    # multiplication
    elif mystate["operation"] == '*':
         
        print('\n')

        print(mystate)

        product = 1
        for value in mystate["values"]:
            product *= value

        mystate["result"] = f"Hi there {mystate["name"]}! Your product  = {product}"

        print(mystate)   # mystate["result"]  also gets displayed
        print('\n above two print statments are in the funciton \n ')

    else: 

            print('\n')
    
            print(mystate)
    
            mystate["result"] = f"Hi there {mystate["name"]}! Your operation '{mystate["operation"]}'  is not supported."
    
            print(mystate)   # mystate["result"]  also gets displayed
            print('\n above two print statments are in the funciton \n ')


    return mystate

# Defining the Graph

graph = StateGraph(AgentState)


graph.add_node("processor", process_values)
graph.set_entry_point("processor")
graph.set_finish_point("processor")

app = graph.compile() # Compiling the graph

operation = input('Enter the operation you want to perform')


answers = app.invoke({"name": "Alice", "values": [5, 5, 5], "operation": operation}) # Invoking the graph with multiple inputs

# print(answers) # Printing the entire state after processing
print(answers["result"]) # Printing the result only