from typing import TypedDict, Literal, List, Dict, Any, Optional

class GameState(TypedDict, total=False):
    # Core routing and game state
    route_to: Literal["number_game", "word_game", "end_game", "game_orchestrator"]
    number_game_count: int
    word_game_count: int

    # Messages for conversation flow
    messages: List[Dict[str, Any]]

    # Additional fields for enhanced functionality
    current_game: Optional[str]
    session_id: Optional[str]
    user_input: Optional[str]
    game_status: Optional[str]
    type: Optional[str]  # For interrupt handling
    message: Optional[str]  # For interrupt messages

    # Number game specific fields
    min_val: Optional[int]
    max_val: Optional[int]
    guess_history: Optional[List[str]]

    # Word game specific fields
    current_question_number: Optional[int]
    asked_questions: Optional[List[str]]
    qa_pairs: Optional[List[tuple]]
    chosen_word: Optional[str]