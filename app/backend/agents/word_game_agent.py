from langgraph.prebuilt import create_react_agent
from ..utils.model import model
from ..tools.word_game_tools import play_word_game

word_game_agent = create_react_agent(
    model=model,
    tools=[play_word_game],
    name="word_game_agent",
    prompt="You are a word guessing game agent. Your job is to guess the human's chosen word by asking 5 yes/no/maybe questions, then making a final guess. Use the play_word_game tool to play the game."
)