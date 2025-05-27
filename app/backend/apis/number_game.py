from fastapi import APIRouter, Request
import uuid
import traceback

router = APIRouter()

game_sessions = {}


@router.post("/number_game/play")
async def play_number_game(request: Request):
    try:
        print("🎮 Number game play endpoint called")
        body = await request.json()
        print(f"DEBUG: Received: {body}")

        session_id = body.get("session_id", str(uuid.uuid4()))

        # Initialize game session
        if session_id not in game_sessions:
            game_sessions[session_id] = {
                "min_val": 1,
                "max_val": 50,
                "guess_count": 0,
                "game_started": False
            }

        game_state = game_sessions[session_id]

        # Start the game
        if not game_state["game_started"]:
            game_state["game_started"] = True
            return {
                "route_to": "number_game",
                "number_game_count": 1,
                "word_game_count": 0,
                "type": "interrupt",
                "message": "Great! Think of a number between 1 and 50, then say 'ready' when you're prepared!",
                "session_id": session_id,
                "min_val": 1,
                "max_val": 50,
                "guess_count": 0,
                "messages": body.get("messages", [])
            }

        mid = (game_state["min_val"] + game_state["max_val"]) // 2
        game_state["guess_count"] += 1

        return {
            "route_to": "number_game",
            "number_game_count": 1,
            "word_game_count": 0,
            "type": "interrupt",
            "message": f"Is your number {mid}?",
            "session_id": session_id,
            "min_val": game_state["min_val"],
            "max_val": game_state["max_val"],
            "guess_count": game_state["guess_count"],
            "messages": body.get("messages", [])
        }

    except Exception as e:
        print(f"API Exception: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "message": "Failed to play number game",
            "messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]
        }


@router.post("/number_game/resume")
async def resume_number_game(request: Request):
    try:
        body = await request.json()

        user_input = body.get("user_input", "").lower().strip()
        session_id = body.get("session_id")

        if not user_input:
            return {"error": "Missing user input to resume game"}

        if not session_id or session_id not in game_sessions:
            game_sessions[session_id] = {
                "min_val": 1,
                "max_val": 50,
                "guess_count": 0,
                "game_started": True,
                "waiting_for": "ready"
            }

        game_state = game_sessions[session_id]

        waiting_for = game_state.get("waiting_for", "ready")

        if waiting_for == "ready" and user_input == "ready":
            mid = (game_state["min_val"] + game_state["max_val"]) // 2
            game_state["guess_count"] += 1
            game_state["waiting_for"] = "yes_no"

            return {
                **body,
                "type": "interrupt",
                "message": f"Is your number {mid}?",
                "min_val": game_state["min_val"],
                "max_val": game_state["max_val"],
                "guess_count": game_state["guess_count"],
                "waiting_for": "yes_no"
            }

        elif waiting_for == "yes_no" and user_input == "yes":
            mid = (game_state["min_val"] + game_state["max_val"]) // 2
            del game_sessions[session_id]

            return {
                **body,
                "messages": body.get("messages", []) + [
                    {"role": "user", "content": user_input},
                    {"role": "assistant",
                     "content": f"Excellent! I guessed your number ({mid}) correctly! 🎉 Thanks for playing!"}
                ],
                "game_completed": True,
                "type": None,
                "message": None
            }

        elif waiting_for == "yes_no" and user_input == "no":
            mid = (game_state["min_val"] + game_state["max_val"]) // 2
            game_state["waiting_for"] = "higher_lower"

            return {
                **body,
                "type": "interrupt",
                "message": f"Is your number higher or lower than {mid}?",
                "min_val": game_state["min_val"],
                "max_val": game_state["max_val"],
                "guess_count": game_state["guess_count"],
                "waiting_for": "higher_lower"
            }

        elif waiting_for == "higher_lower" and user_input == "higher":
            mid = (game_state["min_val"] + game_state["max_val"]) // 2
            game_state["min_val"] = mid + 1

            if game_state["min_val"] > game_state["max_val"]:
                del game_sessions[session_id]
                return {
                    **body,
                    "messages": body.get("messages", []) + [
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": "Something went wrong with the range. Let's start over!"}
                    ],
                    "error": "Invalid range",
                    "type": None,
                    "message": None
                }

            next_mid = (game_state["min_val"] + game_state["max_val"]) // 2
            game_state["guess_count"] += 1
            game_state["waiting_for"] = "yes_no"

            return {
                **body,
                "type": "interrupt",
                "message": f"Is your number {next_mid}?",
                "min_val": game_state["min_val"],
                "max_val": game_state["max_val"],
                "guess_count": game_state["guess_count"],
                "waiting_for": "yes_no"
            }

        elif waiting_for == "higher_lower" and user_input == "lower":
            # Number is lower, adjust range
            mid = (game_state["min_val"] + game_state["max_val"]) // 2
            game_state["max_val"] = mid - 1

            if game_state["min_val"] > game_state["max_val"]:
                del game_sessions[session_id]
                return {
                    **body,
                    "messages": body.get("messages", []) + [
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": "Something went wrong with the range. Let's start over!"}
                    ],
                    "error": "Invalid range",
                    "type": None,
                    "message": None
                }

            next_mid = (game_state["min_val"] + game_state["max_val"]) // 2
            game_state["guess_count"] += 1
            game_state["waiting_for"] = "yes_no"

            return {
                **body,
                "type": "interrupt",
                "message": f"Is your number {next_mid}?",
                "min_val": game_state["min_val"],
                "max_val": game_state["max_val"],
                "guess_count": game_state["guess_count"],
                "waiting_for": "yes_no"
            }

        else:
            expected = "ready" if waiting_for == "ready" else (
                "yes or no" if waiting_for == "yes_no" else "higher or lower")
            return {
                **body,
                "type": "interrupt",
                "message": f"I didn't understand '{user_input}'. Please respond with: {expected}",
                "min_val": game_state["min_val"],
                "max_val": game_state["max_val"],
                "guess_count": game_state["guess_count"],
                "waiting_for": waiting_for
            }

    except Exception as e:
        print(f"Resume Exception: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "error": str(e),
            "message": "Failed to resume number game",
            "messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]
        }
