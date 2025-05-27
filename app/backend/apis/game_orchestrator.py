from fastapi import APIRouter, Request
from app.backend.graph.graph import compiled_graph
from app.backend.schemas.game_state import GameState

router = APIRouter()

@router.post("/route")
async def orchestrate_game(request: Request):
    print("Received request to orchestrate game")
    body = await request.json()
    state: GameState = body
    result = compiled_graph.invoke(state)
    print("Game orchestrated successfully, returning result")
    return result
