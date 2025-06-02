from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langgraph.types import interrupt
from langgraph.errors import GraphInterrupt
from ..utils.model import model

# Available words for the game
WORDS = ["apple", "kiwi", "desk", "chair", "car", "pen"]


@tool
def play_word_game(game_state=None):
    """
    Complete word guessing game orchestrator. Handles the entire game flow:
    1. Accept READY input from user to begin
    2. Get questions from LLM and responses from user through interrupts
    3. Pass Q&A pairs to LLM to receive the guessed word
    """
    print("🔤 DEBUG: play_word_game tool called - FULL ORCHESTRATOR MODE")

    # Initialize or load game state
    if game_state is None:
        game_state = {
            "stage": "welcome",
            "questions_asked": 0,
            "qa_pairs": [],
            "generated_questions": []
        }

    print(f"🔤 DEBUG: Current game state: {game_state}")
    word_list = ", ".join(WORDS)

    try:
        # Stage 1: Accept READY input from user to begin
        if game_state["stage"] == "welcome":
            print("🔤 DEBUG: Stage 1 - Welcome phase - waiting for READY")
            welcome_message = f"""🎮 Welcome to the Word Guessing Game!

Choose one word from: {word_list}

Say 'ready' when you've chosen your word!"""

            user_response = interrupt(welcome_message)
            print(f"🔤 DEBUG: Got user response: {user_response}")

            # Keep asking until user says ready
            while "ready" not in user_response.lower():
                print("🔤 DEBUG: User not ready, asking again")
                retry_message = f"Please choose a word from: {word_list} and say 'ready'!"
                user_response = interrupt(retry_message)
                print(f"🔤 DEBUG: Got retry response: {user_response}")

            print("🔤 DEBUG: User said READY - generating questions from LLM")
            # Generate questions from LLM
            game_state["generated_questions"] = generate_questions()
            game_state["stage"] = "questions"
            print(f"🔤 DEBUG: Generated {len(game_state['generated_questions'])} questions from LLM")

        # Stage 2: Get responses to questions from user through interrupts
        if game_state["stage"] == "questions":
            print(f"🔤 DEBUG: Stage 2 - Getting question responses, progress: {game_state['questions_asked']}/5")

            # Ask each question and collect responses
            while game_state["questions_asked"] < 5:
                question_num = game_state["questions_asked"]
                current_question = game_state["generated_questions"][question_num]

                print(f"🔤 DEBUG: Asking question {question_num + 1} via interrupt: {current_question}")
                question_prompt = f"Question {question_num + 1}/5: {current_question}\n\nPlease answer: yes, no, or maybe"

                # Get response from user through interrupt
                user_answer = interrupt(question_prompt)
                print(f"🔤 DEBUG: Got user answer {question_num + 1}: {user_answer}")

                # Store the Q&A pair
                game_state["qa_pairs"].append((current_question, user_answer.lower().strip()))
                game_state["questions_asked"] += 1

                print(f"🔤 DEBUG: Stored Q&A pair, total collected: {game_state['questions_asked']}")

            # Move to final guess stage
            game_state["stage"] = "final_guess"
            print("🔤 DEBUG: All 5 Q&A pairs collected, moving to final guess")

        # Stage 3: Pass Q&A pairs to LLM and receive the guessed word
        if game_state["stage"] == "final_guess":
            print("🔤 DEBUG: Stage 3 - Passing Q&A pairs to LLM for final guess")

            # Pass the zip of questions and answers to LLM
            final_guess = make_final_guess_from_qa_pairs(game_state["qa_pairs"])
            print(f"🔤 DEBUG: LLM generated final guess: {final_guess}")

            # Present the guess to user for verification
            verification_prompt = f"{final_guess}\n\nIs this correct? (yes/no)"
            final_response = interrupt(verification_prompt)
            print(f"🔤 DEBUG: Got verification response: {final_response}")

            # Return final result
            if final_response.lower().strip() == "yes":
                result = "🎉 Excellent! I guessed your word correctly! Thanks for playing!"
            else:
                result = "🎮 I didn't get it this time! You win! Thanks for playing!"

            print(f"🔤 DEBUG: Game complete, returning final result")
            return result

    except GraphInterrupt:
        print("🔤 DEBUG: GraphInterrupt detected - preserving state and re-raising")
        raise

    except Exception as e:
        print(f"🔤 DEBUG: Exception in play_word_game: {e}")
        import traceback
        print(f"🔤 DEBUG: Traceback: {traceback.format_exc()}")
        return f"Error in word game: {str(e)}"


def generate_questions():
    """Generate 5 strategic questions using LLM"""
    print("🔤 DEBUG: Calling LLM to generate questions")
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
    print(f"🔤 DEBUG: LLM generated questions response: {response}")

    # Parse questions from LLM response
    lines = response.split('\n')
    questions = []
    for line in lines:
        line = line.strip()
        if line and ('?' in line):
            # Remove numbering if present
            if line[0].isdigit():
                line = line.split('.', 1)[1].strip() if '.' in line else line
            questions.append(line)

    # Ensure we have exactly 5 questions
    questions = questions[:5]
    while len(questions) < 5:
        questions.append("Is it something commonly found at home?")

    print(f"🔤 DEBUG: Parsed {len(questions)} questions from LLM")
    return questions


def make_final_guess_from_qa_pairs(qa_pairs):
    """Pass Q&A pairs to LLM to receive the guessed word"""
    print("🔤 DEBUG: Passing Q&A pairs to LLM for final guess")
    word_list = ", ".join(WORDS)

    # Format the Q&A pairs for the LLM
    qa_text = ""
    for i, (question, answer) in enumerate(qa_pairs, 1):
        qa_text += f"Q{i}: {question}\nA{i}: {answer}\n\n"

    print(f"🔤 DEBUG: Formatted Q&A pairs for LLM: {qa_text}")

    prompt = PromptTemplate.from_template(
        """Based on the following Q&A pairs, guess the word from the available options.

AVAILABLE WORDS: {words}

QUESTIONS AND ANSWERS:
{qa_pairs}

Analyze the answers carefully and choose the most likely word.
Format your response as: "Based on your answers, I think your word is [WORD]"
"""
    )

    formatted_prompt = prompt.format(qa_pairs=qa_text, words=word_list)
    llm_response = model.invoke(formatted_prompt).content.strip()

    print(f"🔤 DEBUG: LLM final guess response: {llm_response}")
    return llm_response