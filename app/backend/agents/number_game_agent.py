from langgraph.prebuilt import create_react_agent
from ..utils.model import model
from ..tools.number_game_tools import guess_number

number_game_agent = create_react_agent(
    model=model,
    tools=[guess_number],
    name="number_game_agent",
    prompt="You are a number guessing game agent. Your job is to guess the human's number between 1 and 50. Use the guess_number tool to start the guessing game.\n\n"
)