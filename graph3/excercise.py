from typing import TypedDict # Imports all the data types we need
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    name: str
    age: str
    final: str
    skills: str


def user_name(mystate: AgentState) -> AgentState:
    """This is the first node of our sequence"""

    mystate["final"] = f"{mystate['name']}, welcome to the system!"
    return mystate

def user_age(mystate: AgentState) -> AgentState:
    """This is the second node of our sequence"""

    mystate['final'] = mystate["final"] + f" You are {mystate['age']} years old!"
    return mystate


def user_skills(mystate: AgentState) -> AgentState:
    """This is the third node of our sequence"""

    
    if len(skills_list) == 1:
        formatted_skills = skills_list[0]
    elif len(skills_list) == 2:
        formatted_skills = f"{skills_list[0]} and {skills_list[1]}"
    else:
        formatted_skills = ", ".join(skills_list[:-1]) + f" and {skills_list[-1]}"
    
    mystate['final'] = mystate["final"] + f" You have skills in: {formatted_skills}."
    return mystate


graph = StateGraph(AgentState)
graph.add_node("first_node",user_name)
graph.add_node("second_node",user_age)
graph.add_node("third_node",user_skills)


graph.set_entry_point("first_node")
graph.add_edge("first_node", "second_node") # we add an edge from the first node to the second node, creating a sequence
graph.add_edge("second_node", "third_node") # we add an edge from the second node to the third node, creating a sequence
graph.set_finish_point("third_node")
app = graph.compile()

print("\n")


skills = input('Enter skills seprated by commas')

# convert skills variable to following format -> "Python, Machine Learning, LangGraph" for any number of skills entered seprated by commas
skills_list = [skill.strip() for skill in skills.split(',')]
# This lines converts the skills str into a clean list of strings


# result = app.invoke({"name": "Linda", "age": "31","skills": "Python, Machien Learning and LangGraph"})

result = app.invoke({"name": "Linda", "age": "31", "skills": ', '.join(skills_list)})

print("# This only prints the final result, or final key in the state")
print(result["final"])

print("\n")

print("# This prints the whole state")
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