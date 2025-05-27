from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def guess_number():
    """
    Number guessing game where the user has to choose a number between 1 and 50.
    The game tries to guess what the number is based on user feedback.
    """
    min_val = 1
    max_val = 50
    history = []

    try:
        while min_val <= max_val:
            mid = (min_val + max_val) // 2
            user_response = interrupt(f"Is your number {mid}? (yes/no)")

            # Add to history
            history.append(f"Asked: Is your number {mid}? User: {user_response}")

            if user_response.lower() == "yes":
                result = f"Great! I guessed your number: {mid}"
                return result

            user_response = interrupt(f"Is your number higher or lower than {mid}? (higher/lower)")

            # Add to history
            history.append(f"Asked: Higher or lower than {mid}? User: {user_response}")

            if user_response.lower() == "higher":
                min_val = mid + 1
            elif user_response.lower() == "lower":
                max_val = mid - 1
            else:
                # Handle invalid input
                interrupt("Please respond with 'higher' or 'lower'. Let's try again.")
                continue

        result = "Something went wrong. Please make sure you chose a number between 1 and 50."
        return result
    except Exception as e:
        error_msg = f"Error in number game: {str(e)}"
        return error_msg