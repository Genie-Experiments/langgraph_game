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
        print("🔤 Word game play endpoint called")
        body = await request.json()
        print(f"DEBUG: Received: {body}")

        unique_session_id = f"word_game_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        state: GameState = {
            "route_to": "word_game",
            "number_game_count": 0,
            "word_game_count": 0,
            "messages": [{"role": "user", "content": "Let's play the word game"}],
            "session_id": unique_session_id
        }

        print(f"DEBUG: Created FRESH state with unique session: {unique_session_id}")

        config = {"configurable": {"thread_id": unique_session_id}}
        print(f"DEBUG: Config with unique thread_id: {config}")

        # Invoke the graph with fresh config
        print("DEBUG: Invoking compiled_graph with FRESH session...")
        result = compiled_graph.invoke(state, config)
        print(f"DEBUG: Graph result: {result}")

        return result

    except Exception as e:
        print(f"❌ Word Game API Exception: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
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
        print(f"DEBUG: Resume body: {body}")

        # Get user response
        user_input = body.get("user_input")
        if not user_input:
            return {"error": "Missing user input to resume word game"}

        print(f"DEBUG: User input: {user_input}")

        # Extract the session ID - CRITICAL for proper resumption
        session_id = body.get("session_id")
        if not session_id:
            print("DEBUG: No session_id found in resume request")
            return {"error": "Missing session_id for resume"}

        print(f"DEBUG: Resuming with session_id: {session_id}")

        # CRITICAL: Create a minimal state that just provides the user input
        # Do NOT reconstruct the entire state - let LangGraph handle the continuation
        resume_state = {
            "user_input": user_input,  # This is what the interrupted tool is waiting for
            "route_to": "word_game"
        }

        print(f"DEBUG: Minimal resume state: {resume_state}")

        # CRITICAL: Use the EXACT same thread_id that was used in the original call
        config = {"configurable": {"thread_id": session_id}}
        print(f"DEBUG: Using config: {config}")

        # CRITICAL: Call invoke() NOT stream() - this resumes the interrupted execution
        print("DEBUG: Calling compiled_graph.invoke() to resume...")
        result = compiled_graph.invoke(resume_state, config)
        print(f"DEBUG: Resume result: {result}")

        return result

    except Exception as e:
        print(f"❌ Word Game Resume Exception: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "message": "Failed to resume word game",
            "messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]
        }