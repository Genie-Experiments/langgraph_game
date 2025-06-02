from langgraph.prebuilt import create_react_agent
from ..utils.model import model
from ..tools.word_game_tools import play_word_game

word_game_agent = create_react_agent(
    model=model,
    tools=[play_word_game],
    name="word_game_agent",
    prompt="You are a word guessing game agent responsible for guessing a word by asking 5 questions. "
           "Your ONLY job is to call the play_word_game tool immediately when asked to start a word game. "
           "DO NOT ask questions directly - you MUST use the play_word_game tool to handle all game logic. "
           "When the user wants to play a word game, immediately call the play_word_game tool. "
           "The tool will handle all interactions with the user including asking questions and getting responses.",
    verbose=True
)