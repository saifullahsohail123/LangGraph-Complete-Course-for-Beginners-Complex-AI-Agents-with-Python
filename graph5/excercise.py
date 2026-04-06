from typing import TypedDict, Dict, List
from langgraph.graph import StateGraph, START, END
import random


class GameState(TypedDict):
    player_name: str
    target_number: int
    guesses: List[int]
    attempts: int # attempt note
    lower_bound: int
    upper_bound: int
    hint: str



def setup(mystate: GameState) -> GameState:
    """Greeting Node which says hi to the person"""
    mystate["player_name"] = f"Hi there, {mystate['player_name']}"
    mystate["target_number"] = random.randint(mystate["lower_bound"], mystate["upper_bound"])
    mystate["counter"] = 0
    mystate["lower_bound"] = mystate["lower_bound"]
    mystate["upper_bound"] = mystate["upper_bound"]
    mystate["attempts"] = mystate["attempts"]
    print(f"{mystate['player_name']} The game has begun. I'm thinking of a number between 1 and 20.")
    return mystate


def guess_node(state: GameState) -> GameState:
    """Generate a smarter guess based on previous hints"""
    possible_guesses = [i for i in range(state["lower_bound"],state["upper_bound"] + 1) if i not in state["guesses"]]
    if possible_guesses:
        guess = random.choice(possible_guesses)
    else:
        guess = random.randint(state["lower_bound"], state["upper_bound"])

    state["guesses"].append(guess)
    state["attempts"] += 1
    print(f"Attempt {state['attempts']}: Guessing {guess} (Current range: {state['lower_bound']}-{state['upper_bound']})")
    return state

# Alternate to the loop used in guess_node

# Using a regular for loop (easier to understand)
# possible_guesses = []
# for i in range(state["lower_bound"], state["upper_bound"] + 1):
#     if i not in state["guesses"]:
#         possible_guesses.append(i)



def hint_node(state: GameState) -> GameState:
    """Here we provide a hint based on the last guess and update the bounds"""
    latest_guess = state["guesses"][-1]
    target = state["target_number"]
    
    if latest_guess < target:
        state["hint"] = f"The number {latest_guess} is too low. Try higher!"
        
        state["lower_bound"] = max(state["lower_bound"], latest_guess + 1)
        print(f"Hint: {state['hint']}")
        
    elif latest_guess > target:
        state["hint"] = f"The number {latest_guess} is too high. Try lower!"
      
        state["upper_bound"] = min(state["upper_bound"], latest_guess - 1)
        print(f"Hint: {state['hint']}")
    else:
        state["hint"] = f"Correct! You found the number {target} in {state['attempts']} attempts."
        print(f"Success! {state['hint']}")
    
    return state
    


def should_continue(state: GameState) -> str:
    """Determine if we should continue guessing or end the game"""
    
    # There are 2 end conditions - either 7 is reached or the correct number is guessed
    
    latest_guess = state["guesses"][-1]
    if latest_guess == state["target_number"]:
        print(f"GAME OVER: Number found!")
        return "end"
    elif state["attempts"] >= 7:
        print(f"GAME OVER: Maximum attempts reached! The number was {state['target_number']}")
        return "end"
    else:
        print(f"CONTINUING: {state['attempts']}/7 attempts used")
        return "continue"
    


graph = StateGraph(GameState)
graph.add_node("setup", setup)

graph.add_node("guess", guess_node)

graph.add_node("hint_node", hint_node)

graph.add_edge("setup", "guess")

graph.add_edge("guess", "hint_node")  

graph.add_conditional_edges("hint_node", should_continue,{      # source node , Action
    "continue": "guess", # Self-loop back to same node
    "end": END # End the graph
})

# graph.set_entry_point("greeting")
graph.add_edge(START, "setup")

app = graph.compile()


result = app.invoke({"player_name": "Student", "guesses": [], "attempts": 0, "lower_bound": 1, "upper_bound": 20})
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