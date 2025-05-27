from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langgraph.types import interrupt
from ..utils.model import model

# Available words for the game
WORDS = ["apple", "kiwi", "desk", "chair", "car", "pen"]


@tool
def play_word_game():
    """
    Word guessing game where the user has to choose a word from: apple, kiwi, desk, chair, car, pen.
    The game tries to guess what the word is by asking 5 strategic yes/no/maybe questions.
    """
    print("🔤 DEBUG: play_word_game tool called - STARTING EXECUTION")

    word_list = ", ".join(WORDS)

    try:
        # Step 1: Welcome and get ready
        print("🔤 DEBUG: Step 1 - Welcome phase")
        welcome_message = f"""🎮 Welcome to the Word Guessing Game!

Choose one word from: {word_list}

Say 'ready' when you've chosen your word!"""

        print("🔤 DEBUG: About to call interrupt with welcome message")
        user_response = interrupt(welcome_message)
        print(f"🔤 DEBUG: Got user response: {user_response}")

        # Keep asking until user is ready
        while "ready" not in user_response.lower():
            print("🔤 DEBUG: User not ready, asking again")
            retry_message = f"Please choose a word from: {word_list} and say 'ready'!"
            user_response = interrupt(retry_message)
            print(f"🔤 DEBUG: Got retry response: {user_response}")

        print("🔤 DEBUG: User is ready, proceeding to questions")

        # Step 2: Generate 5 questions
        print("🔤 DEBUG: Step 2 - Generating questions")
        questions = generate_questions()
        print(f"🔤 DEBUG: Generated {len(questions)} questions")

        # Step 3: Ask all 5 questions and collect answers
        print("🔤 DEBUG: Step 3 - Asking questions")
        qa_pairs = []

        for i, question in enumerate(questions, 1):
            print(f"🔤 DEBUG: Asking question {i}: {question}")
            question_prompt = f"Question {i}/5: {question}\n\nPlease answer: yes, no, or maybe"
            user_answer = interrupt(question_prompt)
            print(f"🔤 DEBUG: Got answer {i}: {user_answer}")

            # Store the Q&A pair
            qa_pairs.append((question, user_answer.lower().strip()))

        print(f"🔤 DEBUG: Completed all questions, got {len(qa_pairs)} Q&A pairs")

        # Step 4: Make final guess based on all Q&A pairs
        print("🔤 DEBUG: Step 4 - Making final guess")
        final_guess = make_final_guess(qa_pairs)
        print(f"🔤 DEBUG: Generated guess: {final_guess}")

        # Step 5: Get verification
        print("🔤 DEBUG: Step 5 - Getting verification")
        verification_prompt = f"{final_guess}\n\nIs this correct? (yes/no)"
        final_response = interrupt(verification_prompt)
        print(f"🔤 DEBUG: Got verification: {final_response}")

        # Step 6: Return final result
        print("🔤 DEBUG: Step 6 - Returning final result")
        if final_response.lower().strip() == "yes":
            result = "🎉 Excellent! I guessed your word correctly! Thanks for playing!"
        else:
            result = "🎮 I didn't get it this time! You win! Thanks for playing!"

        print(f"🔤 DEBUG: Tool execution complete, returning: {result}")
        return result

    except Exception as e:
        print(f"🔤 DEBUG: Exception in play_word_game tool: {e}")
        import traceback
        print(f"🔤 DEBUG: Tool traceback: {traceback.format_exc()}")
        error_msg = f"Error in word game: {str(e)}"
        return error_msg


def generate_questions():
    """Generate 5 strategic questions for the word game"""
    word_list = ", ".join(WORDS)

    prompt = PromptTemplate.from_template(
        """Generate 5 strategic yes/no/maybe questions for a word guessing game.

AVAILABLE WORDS: {words}

Generate 5 different strategic questions about properties, uses, or characteristics.
Do NOT guess words directly - ask about attributes that help narrow down choices.

Examples:
- "Is it something you can eat?"
- "Is it found indoors?"
- "Is it made of wood?"
- "Can you hold it in your hand?"
- "Is it used for writing?"

Return exactly 5 questions, one per line, numbered 1-5."""
    )

    formatted_prompt = prompt.format(words=word_list)
    response = model.invoke(formatted_prompt).content.strip()

    # Parse questions
    lines = response.split('\n')
    questions = []
    for line in lines:
        line = line.strip()
        if line and ('?' in line):
            if line[0].isdigit():
                line = line.split('.', 1)[1].strip() if '.' in line else line
            questions.append(line)

    questions = questions[:5]
    while len(questions) < 5:
        questions.append("Is it something commonly found at home?")

    return questions


def make_final_guess(qa_pairs):
    """Make final guess based on Q&A pairs"""
    word_list = ", ".join(WORDS)

    qa_text = ""
    for i, (question, answer) in enumerate(qa_pairs, 1):
        qa_text += f"Q{i}: {question}\nA{i}: {answer}\n\n"

    guess_prompt = PromptTemplate.from_template(
        """Based on the following Q&A pairs, guess the word from the available options.

AVAILABLE WORDS: {words}

QUESTIONS AND ANSWERS:
{qa_pairs}

Analyze the answers carefully and choose the most likely word.
Format: "Based on your answers, I think your word is [WORD]"
"""
    )

    formatted_guess = guess_prompt.format(
        qa_pairs=qa_text,
        words=word_list
    )

    return model.invoke(formatted_guess).content.strip()