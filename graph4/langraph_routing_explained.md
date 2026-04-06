# LangGraph Routing & Conditional Branching — Explained Simply

## What This Code Does

This builds a mini calculator using **LangGraph** — a library for building AI agent workflows as graphs (think flowcharts).

The graph flow:
```
START → router → (add_node OR subtract_node) → END
```

---

## Why Not Just Use If/Else?

For a simple calculator, plain Python if/else is overkill. But LangGraph is designed for **AI agent pipelines** where you want:

- A **visual flowchart** of your logic
- **Modular nodes** you can swap, log, or monitor individually
- Complex multi-step agents where routing gets complicated

Think of this as the *pattern*, not the *use case*.

---

## The Router Node

```python
graph.add_node("router", decide_next_node)
```

This registers a node named `"router"` in the graph. When LangGraph sees this node has `add_conditional_edges` attached to it, it **hijacks the normal flow**:

```
receives state → BUT its return value is used for routing, not state update
```

LangGraph internally does this:

1. Calls `decide_next_node(state)`
2. Gets back `"addition_operation"`
3. Does **NOT** update the state with this string
4. Instead uses the string to look up the next node in your dictionary
5. Jumps to `"add_node"` with the **original state still intact**

The string **never touches the state**. LangGraph intercepts it before that happens.

---

## Conditional Edges

```python
graph.add_conditional_edges("router", decide_next_node, {
    "addition_operation": "add_node",
    "subtraction_operation": "subtract_node"
})
```

| Part | Meaning |
|---|---|
| `"router"` | After leaving this node... |
| `decide_next_node` | ...call this function to decide where to go |
| `{"addition_operation": "add_node", ...}` | ...use this map to translate the string into an actual node name |

The dictionary is a **translation map** between what your function returns and the actual node names in the graph.

---

## What Each Node Receives

### Regular Nodes (`add_node`, `subtract_node`)
These follow the normal rule:
```
receives state → does work → returns state
```
```python
def adder(mystate: AgentState) -> AgentState:
    mystate['final'] = mystate['num1'] + mystate['num2']
    return mystate  # ✅ returns state
```

### Router Node — The Exception
Returns a string for routing purposes only. The string is consumed by the graph's navigation mechanism and discarded. It is **never passed as input to the next node**.

---

## Do `add_node` / `subtract_node` Take a String as Input?

**No.** Even though `decide_next_node` returns a string, that string is never passed as an argument to the next node.

LangGraph uses the string only to decide *which* node to jump to. Once that decision is made, it passes the **original AgentState** to the next node — the string is thrown away.

```python
# ✅ Correct — always takes AgentState, never str
def adder(mystate: AgentState) -> AgentState:
    mystate['final'] = mystate['num1'] + mystate['num2']
    return mystate
```

> **Analogy:** Think of it like a traffic cop. The cop (router) points you to lane A or lane B. But you (the state) still arrive at lane A as yourself — the cop's gesture isn't handed to you as a package.

---

## The Honest Type Hint for the Router

The original code had a misleading type hint:

```python
def decide_next_node(mystate: AgentState) -> AgentState:  # ❌ lies — returns a string
    return "addition_operation"
```

The correct, honest version:

```python
def decide_next_node(mystate: AgentState) -> str:  # ✅ honest
    if mystate['operation'] == "+":
        return "addition_operation"
    elif mystate['operation'] == "-":
        return "subtraction_operation"
```

LangGraph doesn't enforce type hints — it just looks at how `add_conditional_edges` is wired and knows the return value is a routing instruction, not a state update.

---

## Mental Model Summary

| Node Type | Return Value Used For | State Passed to Next Node |
|---|---|---|
| Regular node | Updating state | The returned state |
| Router node (with conditional edges) | Picking next node | The **incoming** state, unchanged |

---

## State Flow Visualization

```
AgentState { num1: 5, num2: 3, operation: "+", final: 0 }
        |
        ▼
   [ router node ]
   decide_next_node() returns "addition_operation"
   LangGraph reads the dictionary → jumps to "add_node"
   State is passed on UNCHANGED
        |
        ▼
   [ add_node ]
   receives AgentState (not a string!)
   sets final = 5 + 3 = 8
   returns AgentState { num1: 5, num2: 3, operation: "+", final: 8 }
        |
        ▼
       END
```

The string `"addition_operation"` is used purely as a **signpost** — it never becomes part of the data flowing through the graph.