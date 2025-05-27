from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from app.backend.agents.end_game_agent import end_game_agent
from app.backend.agents.game_orchestrator_agent import game_orchestrator
from app.backend.nodes.number_game import number_game_node
from app.backend.nodes.word_game import word_game_node
from app.backend.schemas.game_state import GameState

builder = StateGraph(GameState)

memory = MemorySaver()


def route_from_orchestrator(state):
    print(f"DEBUG: route_from_orchestrator state keys: {list(state.keys())}")

    if "route_to" in state:
        route = state["route_to"]
        print(f"DEBUG: Using route_to field: {route}")

        if route in ["number_game", "word_game", "end_game"]:
            print(f"DEBUG: Valid route_to found, routing to: {route}")
            return route
        else:
            print(f"Warning: Invalid route_to '{route}', will analyze messages instead")

    print("DEBUG: No valid route_to found, analyzing messages...")
    messages = state.get("messages", [])
    route = "number_game"

    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get("content", "").lower()
            print(f"DEBUG: Analyzing message content: '{content}'")

            if any(keyword in content for keyword in ["word game", "word guessing", "word"]):
                route = "word_game"
                print(f"DEBUG: Detected word game from message content")
                break
            elif any(keyword in content for keyword in ["number game", "number guessing", "number", "guess"]):
                route = "number_game"
                print(f"DEBUG: Detected number game from message content")
                break
            elif any(keyword in content for keyword in ["end", "quit", "stop", "exit"]):
                route = "end_game"
                print(f"DEBUG: Detected end game from message content")
                break

    print(f"DEBUG: Final routing decision: {route}")
    return route


# Register nodes
builder.add_node("game_orchestrator", game_orchestrator.compile())
builder.add_node("number_game", number_game_node)
builder.add_node("word_game", word_game_node)
builder.add_node("end_game", end_game_agent)

# Set entry point
builder.set_entry_point("game_orchestrator")

builder.add_conditional_edges(
    "game_orchestrator",
    route_from_orchestrator,
    {
        "number_game": "number_game",
        "word_game": "word_game",
        "end_game": "end_game"
    }
)

# End game always ends the session
builder.add_edge("end_game", "__end__")

# Compile the graph
compiled_graph = builder.compile(checkpointer=memory)

print("Graph compiled successfully with FRESH memory!")
print(f"Graph type: {type(compiled_graph)}")
print(f"Graph has invoke method: {hasattr(compiled_graph, 'invoke')}")