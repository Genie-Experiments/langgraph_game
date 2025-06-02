from fastapi import APIRouter, Request
from app.backend.graph.graph import compiled_graph
from app.backend.schemas.game_state import GameState
import uuid
import traceback
import time

router = APIRouter()


@router.post("/word_game/play")
async def play_word_game(request: Request):
    try:
        print("Word game play endpoint called")
        body = await request.json()
        print(f"DEBUG: Received: {body}")

        unique_session_id = f"word_game_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        state: GameState = {
            "route_to": "word_game",
            "number_game_count": 0,
            "word_game_count": 0,
            "messages": [{"role": "user", "content": "Use the play_word_game tool to start the word game"}],
            "session_id": unique_session_id
        }

        print(f"DEBUG: Created FRESH state with unique session: {unique_session_id}")

        config = {"configurable": {"thread_id": unique_session_id}}
        print(f"DEBUG: Config with unique thread_id: {config}")

        print("DEBUG: Invoking compiled_graph with FRESH session...")
        result = compiled_graph.invoke(state, config)
        print(f"DEBUG: Graph result: {result}")

        return result

    except Exception as e:
        print(f"Word Game API Exception: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "message": "Failed to play word game",
            "messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]
        }


@router.post("/word_game/resume")
async def resume_word_game(request: Request):
    try:
        print("Word game resume endpoint called")
        body = await request.json()
        user_input = body.get("user_input")
        session_id = body.get("session_id")

        if not user_input or not session_id:
            return {"error": "Missing user_input or session_id"}

        config = {"configurable": {"thread_id": session_id}}

        # Get current state to see what we're resuming
        current_state = compiled_graph.get_state(config)
        print(f"DEBUG: Current state next: {current_state.next}")

        # Resume by continuing with None and letting the interrupt receive the input
        # The input parameter is how you provide responses to interrupts
        result = None
        for chunk in compiled_graph.stream(None, config):
            print(f"DEBUG: Chunk: {chunk}")
            result = chunk

        # If that didn't work, the interrupt might need the input differently
        if not result or '__interrupt__' in str(result):
            # Try providing input as command
            result = compiled_graph.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config
            )

        return result

    except Exception as e:
        print(f"Resume Exception: {e}")
        return {"error": str(e), "message": "Failed to resume word game"}