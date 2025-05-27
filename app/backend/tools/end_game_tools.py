from langchain_core.tools import tool

@tool
def end_game(state: dict) -> str:
    """Ends the game and shows the user how many times they played each game."""
    number_count = state.get("number_game_count", 0)
    word_count = state.get("word_game_count", 0)

    return (
        f"Thanks for playing!\n\n"
        f"You played the Number Guessing Game {number_count} time(s).\n"
        f"You played the Word Guessing Game {word_count} time(s).\n"
        f"Hope you had fun!"
    )