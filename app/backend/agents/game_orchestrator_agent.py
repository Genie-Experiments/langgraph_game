from langgraph_supervisor import create_supervisor

from app.backend.agents.number_game_agent import number_game_agent
from app.backend.agents.word_game_agent import word_game_agent
from app.backend.agents.end_game_agent import end_game_agent
from app.backend.utils.model import model


SUPERVISOR_PROMPT = """You are a game orchestrator supervisor. Based on the user's request and the route_to field, you need to route them to the appropriate agent.

IMPORTANT: If the state has route_to="word_game", you MUST route to word_game_agent.
If the state has route_to="number_game", you MUST route to number_game_agent.

Available agents:
- number_game_agent: For number guessing games (1-50 range)
- word_game_agent: For word guessing games (apple, kiwi, desk, chair, car, pen)
- end_game_agent: For ending the session

Look at both the route_to field AND the user's message:

If route_to="word_game" OR they mention "word game" or word-related content → route to word_game_agent
If route_to="number_game" OR they mention "number game" or number-related content → route to number_game_agent  
If they want to quit, end, or stop → route to end_game_agent

You must respond with a Command to route to the appropriate agent."""



game_orchestrator = create_supervisor(
    [number_game_agent, word_game_agent, end_game_agent],
    model=model,
    prompt=SUPERVISOR_PROMPT,
    supervisor_name="game_orchestrator"
)