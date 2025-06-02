"""
Complete Streamlit UI for LangGraph Game Hub
Updated version with interrupt handling and resume functionality
"""
import streamlit as st
import requests
import json
from typing import Dict, Any, Optional
import time
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page config
st.set_page_config(
    page_title="🎮 LangGraph Game Hub",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .game-container {
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .game-title {
        color: #2c3e50;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        background-color: white;
        margin: 15px 0;
    }
    
    .chat-message {
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 4px solid;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border-left-color: #3498db;
        margin-left: 20%;
        color: #ecf0f1;
    }
    
    .agent-message {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border-left-color: #9c27b0;
        margin-right: 20%;
        color: #ecf0f1;
    }
    
    .system-message {
        background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
        border-left-color: #ff9800;
        text-align: center;
        font-style: italic;
        color: #ffffff;
    }
    
    .error-message {
        background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
        border-left-color: #f44336;
        color: #ffffff;
    }
    
    .success-message {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border-left-color: #4caf50;
        color: #2e7d32;
    }
    
    .interrupt-message {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left-color: #ff9800;
        color: #e65100;
        font-weight: bold;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 5px 0 0 0;
    }
    
    .game-selector {
        background: #2c3e50;
        color: white;
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .game-selector h3 {
        color: #3498db;
        margin-top: 0;
    }
    
    .game-selector ul {
        color: #bdc3c7;
    }
    
    .game-selector code {
        background: #34495e;
        color: #2ecc71;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active { background-color: #4caf50; }
    .status-inactive { background-color: #f44336; }
    .status-waiting { background-color: #ff9800; }
    .status-interrupted { background-color: #ff5722; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    default_values = {
        'current_game': None,
        'game_active': False,
        'conversation_history': [],
        'game_stats': {'number_games': 0, 'word_games': 0, 'total_games': 0},
        'current_state': {},
        'waiting_for_input': False,
        'interrupted': False,
        'interrupt_message': None,
        'last_response': None,
        'session_id': str(uuid.uuid4()),
        'game_data': {},
        'error_message': None
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# API Helper Functions
def make_api_request(endpoint: str, data: Dict = None, timeout: int = 10) -> Optional[Dict]:
    """Make API request with comprehensive error handling"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"

        with st.spinner(f"🔄 Processing..."):
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()

    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. The game might be waiting for input or stuck. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. Please check if the API server is running.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"🚨 HTTP Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def add_message_to_history(message_type: str, content: str, game_type: str = None):
    """Add a message to the conversation history"""
    st.session_state.conversation_history.append({
        'type': message_type,
        'content': content,
        'timestamp': time.time(),
        'game': game_type or st.session_state.current_game
    })

def start_game_session(game_type: str, initial_message: str = None):
    """Start a new game session"""
    # Reset session for new game - CLEAR EVERYTHING
    st.session_state.current_game = game_type
    st.session_state.game_active = True
    st.session_state.waiting_for_input = False
    st.session_state.interrupted = False
    st.session_state.interrupt_message = None
    st.session_state.conversation_history = []
    st.session_state.current_state = {
        'route_to': game_type,
        'number_game_count': st.session_state.game_stats.get('number_games', 0),
        'word_game_count': st.session_state.game_stats.get('word_games', 0),
        'messages': [{'role': 'user', 'content': f'I want to play the {game_type.replace("_", " ")}'}],
        'session_id': str(uuid.uuid4())
    }

    print(f"DEBUG: Starting {game_type} with NEW session and CLEARED history")
    print(f"DEBUG: New session ID: {st.session_state.current_state['session_id']}")

    # Simple endpoint call
    endpoint = f"{game_type}/play"
    print(f"DEBUG: Trying endpoint: {endpoint}")
    response = make_api_request(endpoint, st.session_state.current_state)

    if response:
        print(f"DEBUG: Got response: {response}")
        st.session_state.last_response = response

        with st.expander("🔍 Debug - API Response", expanded=False):
            st.json(response)

        process_game_response(response)
        return True
    else:
        print(f"DEBUG: No response from {endpoint}")
        st.session_state.game_active = False
        st.session_state.current_game = None
        return False


def process_game_response(response: Dict):
    """Process the response from the game API"""
    try:
        print(f"DEBUG: Processing response: {response}")

        st.session_state.current_state.update(response)

        # Check if game is completed
        if response.get("game_completed"):
            print("DEBUG: Game completed!")
            st.session_state.interrupted = False
            st.session_state.waiting_for_input = False
            st.session_state.game_active = False

            if 'messages' in response and response['messages']:
                for msg in response['messages']:
                    if isinstance(msg, dict) and msg.get('role') == 'assistant':
                        content = msg.get('content', '')
                        if content and ('correctly' in content or 'win' in content or 'playing' in content):
                            add_message_to_history('success', content)

            complete_game()
            return

        # FIXED: Handle interrupt responses - check for __interrupt__ field from LangGraph
        if "__interrupt__" in response and response["__interrupt__"]:
            print("DEBUG: Detected LangGraph interrupt response")
            st.session_state.interrupted = True
            st.session_state.waiting_for_input = True

            # Extract the interrupt message from the LangGraph interrupt structure
            interrupt_data = response["__interrupt__"]
            if isinstance(interrupt_data, list) and len(interrupt_data) > 0:
                interrupt_obj = interrupt_data[0]
                if hasattr(interrupt_obj, 'value'):
                    interrupt_msg = interrupt_obj.value
                elif isinstance(interrupt_obj, dict) and 'value' in interrupt_obj:
                    interrupt_msg = interrupt_obj['value']
                else:
                    interrupt_msg = str(interrupt_obj)
            else:
                interrupt_msg = str(interrupt_data)

            st.session_state.interrupt_message = interrupt_msg
            add_message_to_history('interrupt', interrupt_msg)
            print(f"DEBUG: Added LangGraph interrupt message to history: {interrupt_msg}")
            return

        # Handle legacy interrupt format (for backward compatibility)
        if response.get("type") == "interrupt":
            print("DEBUG: Detected legacy interrupt response")
            st.session_state.interrupted = True
            st.session_state.waiting_for_input = True
            interrupt_msg = response.get("message", "Game interrupted - please provide input")
            st.session_state.interrupt_message = interrupt_msg
            add_message_to_history('interrupt', interrupt_msg)
            print(f"DEBUG: Added legacy interrupt message to history: {interrupt_msg}")
            return

        # Reset interrupt state if we get a normal response
        if response.get("type") != "interrupt" and "__interrupt__" not in response:
            st.session_state.interrupted = False
            st.session_state.interrupt_message = None

        # Handle different response formats
        content = ""

        if 'messages' in response and response['messages']:
            for msg in reversed(response['messages']):
                if isinstance(msg, dict):
                    if msg.get('role') == 'assistant' and msg.get('content'):
                        content = msg['content']
                        break
                    elif msg.get('content'):
                        content = msg['content']
                        break
            print(f"DEBUG: Found content in messages: {content}")

        elif 'content' in response and response['content']:
            content = response['content']
            print(f"DEBUG: Found direct content: {content}")

        elif 'message' in response and response['message'] and not response.get("type") == "interrupt":
            content = response['message']
            print(f"DEBUG: Found message field: {content}")

        if content and content.strip() and content != "None":
            add_message_to_history('agent', content)
            st.session_state.waiting_for_input = True
        else:
            print("DEBUG: No meaningful content found in response")

        if 'error' in response:
            add_message_to_history('error', f"Error: {response['error']}")
            st.session_state.game_active = False

    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        add_message_to_history('error', f"Failed to process response: {str(e)}")
        print(f"DEBUG: Exception in process_game_response: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")


def send_user_input(user_input: str):
    """Send user input to the current game"""
    if not st.session_state.game_active or not st.session_state.current_game:
        st.error("No active game session")
        return False

    print(f"DEBUG: Sending user input: {user_input}")
    print(f"DEBUG: Interrupted state: {st.session_state.interrupted}")

    add_message_to_history('user', user_input)

    # IMPROVED: Check if we're responding to an interrupt by looking at the LAST agent message
    is_interrupt_response = False

    # Check if the last agent message contains interrupt indicators
    if st.session_state.conversation_history:
        # Look at the very last agent/interrupt message
        last_agent_message = None
        for msg in reversed(st.session_state.conversation_history):
            if msg['type'] in ['agent', 'interrupt']:
                last_agent_message = msg['content'].lower()
                break

        print(f"DEBUG: Last agent message: {last_agent_message}")

        if last_agent_message:
            # Check for word game interrupt patterns
            if ("🎮 welcome to the word guessing game" in last_agent_message and
                    "say 'ready'" in last_agent_message):
                is_interrupt_response = True
                print("DEBUG: Detected word game welcome interrupt - USING RESUME")
            # Check for number game interrupt patterns
            elif ("think of a number" in last_agent_message and
                  ("ready" in last_agent_message or "prepared" in last_agent_message)):
                is_interrupt_response = True
                print("DEBUG: Detected number game ready interrupt - USING RESUME")
            # Check for any question that needs resumption (contains specific question patterns)
            elif user_input.lower() == "ready" and ("choose" in last_agent_message or "word" in last_agent_message):
                is_interrupt_response = True
                print("DEBUG: User said 'ready' in response to word selection - USING RESUME")

    # ALSO: Check if st.session_state.interrupted is True (backup detection)
    if st.session_state.interrupted:
        is_interrupt_response = True
        print("DEBUG: Session state shows interrupted=True - USING RESUME")

    if is_interrupt_response:
        print("DEBUG: Using resume endpoint for interrupt response")
        return resume_game(user_input)

    print("DEBUG: Using regular play endpoint")

    # Regular game flow
    current_messages = st.session_state.current_state.get('messages', [])
    updated_state = {
        **st.session_state.current_state,
        'user_input': user_input,
        'messages': current_messages + [{'role': 'user', 'content': user_input}]
    }

    print(f"DEBUG: Sending state: {updated_state}")

    endpoint = f"{st.session_state.current_game}/play"
    print(f"DEBUG: Trying endpoint: {endpoint}")
    response = make_api_request(endpoint, updated_state)

    if response:
        print(f"DEBUG: Got response from {endpoint}: {response}")
        with st.expander("🔍 Debug - API Response", expanded=False):
            st.json(response)
        process_game_response(response)
        return True

    print("DEBUG: Endpoint failed")
    add_message_to_history('error', "Failed to send message")
    return False


def resume_game(user_input: str):
    """Resume an interrupted game with user input"""
    print(f"DEBUG: Resuming game with input: {user_input}")

    # CRITICAL: Use the session_id from the current_state, not from st.session_state.session_id
    # because the API creates its own unique session_id
    actual_session_id = st.session_state.current_state.get('session_id')
    if not actual_session_id:
        print("DEBUG: No session_id found in current_state")
        add_message_to_history('error', "Session error - no session ID found")
        return False

    print(f"DEBUG: Using actual session_id: {actual_session_id}")

    # FIXED: Simplified resume data - just pass the essentials
    resume_data = {
        'user_input': user_input,
        'session_id': actual_session_id,
    }

    print(f"DEBUG: Resume data: {resume_data}")

    response = make_api_request(f"{st.session_state.current_game}/resume", resume_data)

    if response:
        print(f"DEBUG: Resume response: {response}")
        with st.expander("🔍 Debug - Resume Response", expanded=False):
            st.json(response)

        # Update the current state with the response
        st.session_state.current_state.update(response)
        st.session_state.interrupted = False
        st.session_state.interrupt_message = None

        process_game_response(response)
        return True
    else:
        print("DEBUG: Resume failed")
        add_message_to_history('error', "Failed to resume game")
        return False

def complete_game():
    """Complete the current game and update stats"""
    if st.session_state.current_game:
        if st.session_state.current_game == 'number_game':
            st.session_state.game_stats['number_games'] += 1
        elif st.session_state.current_game == 'word_game':
            st.session_state.game_stats['word_games'] += 1

        st.session_state.game_stats['total_games'] = (
            st.session_state.game_stats['number_games'] +
            st.session_state.game_stats['word_games']
        )

        print(f"DEBUG: Game completed, updated stats: {st.session_state.game_stats}")

    st.session_state.game_active = False
    st.session_state.waiting_for_input = False
    st.session_state.interrupted = False
    st.session_state.interrupt_message = None

def end_current_game():
    """End the current game session"""
    if st.session_state.game_active:
        add_message_to_history('system', f"Game ended by user")
        complete_game()

    st.session_state.current_game = None

# UI Components
def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎮 LangGraph Game Hub</h1>
        <p>Experience Multi-Agent Gaming with Human-in-the-Loop Interaction</p>
    </div>
    """, unsafe_allow_html=True)

def render_stats_sidebar():
    """Render the statistics sidebar"""
    with st.sidebar:
        st.header("📊 Game Statistics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{st.session_state.game_stats['number_games']}</div>
                <div class="stats-label">Number Games</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{st.session_state.game_stats['word_games']}</div>
                <div class="stats-label">Word Games</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{st.session_state.game_stats['total_games']}</div>
            <div class="stats-label">Total Games Played</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.subheader("🎯 Current Status")

        if st.session_state.game_active:
            if st.session_state.interrupted:
                status_color = "status-interrupted"
                status_text = "Interrupted - Waiting for Input"
            elif st.session_state.waiting_for_input:
                status_color = "status-waiting"
                status_text = "Waiting for Input"
            else:
                status_color = "status-active"
                status_text = "Playing"

            game_name = st.session_state.current_game.replace('_', ' ').title()

            st.markdown(f"""
            <p><span class="status-indicator {status_color}"></span><strong>{game_name}</strong></p>
            <p style="margin-left: 20px; color: #666;">Status: {status_text}</p>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <p><span class="status-indicator status-inactive"></span><strong>No Active Game</strong></p>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.subheader("🎮 Game Controls")

        if st.session_state.game_active:
            if st.button("🛑 End Current Game", key="end_game", use_container_width=True):
                end_current_game()
                st.rerun()

        if st.button("🗑️ Clear History", key="clear_history", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()

        if st.button("🔄 Reset All Stats", key="reset_stats", use_container_width=True):
            st.session_state.game_stats = {'number_games': 0, 'word_games': 0, 'total_games': 0}
            st.success("Stats reset!")
            st.rerun()

def render_game_selection():
    """Render game selection interface"""
    st.markdown("""
    <div class="game-container">
        <div class="game-title">🌟 Choose Your Adventure</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="game-selector">
            <h3>🔢 Number Guessing Game</h3>
            <p>Think of a number between 1-50, and I'll try to guess it using smart questioning!</p>
            <ul style="font-size: 0.9rem;">
                <li>AI-powered binary search algorithm</li>
                <li>Interactive yes/no questioning</li>
                <li>Maximum 6 questions to guess</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Start Number Game", key="start_number", use_container_width=True):
            print("DEBUG: Starting new number game - clearing previous history")
            if start_game_session('number_game', '🔢 Starting Number Guessing Game...'):
                st.success("Number game started!")
                st.rerun()

    with col2:
        st.markdown("""
        <div class="game-selector">
            <h3>🔤 Word Guessing Game</h3>
            <p>Choose a word from the available list, and I'll guess it through 5 strategic questions!</p>
            <p><strong>Available words:</strong><br>
            <code>apple, kiwi, desk, chair, car, pen</code></p>
            <ul style="font-size: 0.9rem;">
                <li>LLM-generated intelligent questions</li>
                <li>Interactive yes/no/maybe questioning</li>
                <li>Exactly 5 questions before final guess</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Start Word Game", key="start_word", use_container_width=True):
            print("DEBUG: Starting new word game - clearing previous history")
            if start_game_session('word_game', '🔤 Starting Word Guessing Game...'):
                st.success("Word game started!")
                st.rerun()

def render_conversation():
    """Render the conversation interface"""
    st.markdown(f"""
    <div class="game-container">
        <div class="game-title">💬 {st.session_state.current_game.replace('_', ' ').title()}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.interrupted:
        st.warning("🔄 **Game Interrupted**: The AI is waiting for your response to continue.")

    if st.session_state.conversation_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for message in st.session_state.conversation_history:
            if message['type'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)

            elif message['type'] == 'agent':
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>🤖 Agent:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)

            elif message['type'] == 'system':
                st.markdown(f"""
                <div class="chat-message system-message">
                    <strong>🔧 System:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)

            elif message['type'] == 'error':
                st.markdown(f"""
                <div class="chat-message error-message">
                    <strong>❌ Error:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)

            elif message['type'] == 'success':
                st.markdown(f"""
                <div class="chat-message success-message">
                    <strong>✅ Success:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)

            elif message['type'] == 'interrupt':
                st.markdown(f"""
                <div class="chat-message interrupt-message">
                    <strong>⚡ AI Question:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if st.session_state.game_active and not st.session_state.interrupted:
            st.info("🤖 Starting game... Please wait for the first question.")

    if st.session_state.waiting_for_input:
        st.markdown("---")
        st.subheader("💭 Your Response")

        with st.expander("🔍 Debug Info", expanded=False):
            st.write(f"Interrupted: {st.session_state.interrupted}")
            st.write(f"Waiting for input: {st.session_state.waiting_for_input}")
            st.write(f"Interrupt message: {st.session_state.interrupt_message}")
            st.write(f"Last few messages: {st.session_state.conversation_history[-3:] if st.session_state.conversation_history else 'None'}")
            st.write(f"Current state keys: {list(st.session_state.current_state.keys()) if st.session_state.current_state else 'None'}")
            st.write(f"Last API response: {st.session_state.last_response}")

        last_message = ""
        question_to_show = ""

        if st.session_state.interrupted and st.session_state.interrupt_message:
            last_message = st.session_state.interrupt_message.lower()
            question_to_show = st.session_state.interrupt_message
        else:
            for msg in reversed(st.session_state.conversation_history):
                if msg['type'] in ['agent', 'interrupt']:
                    last_message = msg['content'].lower()
                    question_to_show = msg['content']
                    break

        if question_to_show:
            st.info(f"🎯 **Question:** {question_to_show}")
        else:
            st.warning("⚠️ No question found - this might be a backend issue. Check the debug info above.")

        response_choice = None

        if st.session_state.current_game == 'number_game':
            question_lower = question_to_show.lower() if question_to_show else last_message

            if 'ready' in question_lower and 'prepared' in question_lower:
                response_choice = st.selectbox(
                    "Select your answer:",
                    options=["", "ready"],
                    key="ready_select"
                )
            elif 'higher or lower' in question_lower or 'higher or lower than' in question_lower:
                response_choice = st.selectbox(
                    "Select your answer:",
                    options=["", "higher", "lower"],
                    key="higher_lower_select"
                )
            elif 'is your number' in question_lower and '?' in question_lower:
                response_choice = st.selectbox(
                    "Select your answer:",
                    options=["", "yes", "no"],
                    key="yes_no_select"
                )
            else:
                st.write("💡 **Tip:** Choose 'ready' if asked to get ready, 'yes/no' for number guesses, 'higher/lower' for comparisons.")
                response_choice = st.selectbox(
                    "Select your answer:",
                    options=["", "ready", "yes", "no", "higher", "lower"],
                    key="number_general_select"
                )

        elif st.session_state.current_game == 'word_game':
            question_lower = question_to_show.lower() if question_to_show else last_message

            if ('choose' in question_lower and 'words' in question_lower) or ('ready' in question_lower and 'chosen' in question_lower):
                response_choice = st.selectbox(
                    "Select your answer:",
                    options=["", "ready"],
                    key="word_ready_select"
                )
            elif 'is your word' in question_lower and 'correct' in question_lower:
                response_choice = st.selectbox(
                    "Select your answer:",
                    options=["", "yes", "no"],
                    key="word_final_select"
                )
            elif '?' in question_lower and ('is' in question_lower or 'does' in question_lower or 'can' in question_lower):
                response_choice = st.selectbox(
                    "Select your answer:",
                    options=["", "yes", "no", "maybe"],
                    key="word_game_select"
                )
            else:
                if 'word game started' in question_lower or 'choose' in question_lower:
                    st.write("💡 **Tip:** Say 'ready' when you've chosen your word!")
                    response_choice = st.selectbox(
                        "Select your answer:",
                        options=["", "ready"],
                        key="word_general_ready_select"
                    )
                else:
                    st.write("💡 **Tip:** Choose 'ready' to start, 'yes/no/maybe' for questions, 'yes/no' for final guesses.")
                    response_choice = st.selectbox(
                        "Select your answer:",
                        options=["", "ready", "yes", "no", "maybe"],
                        key="word_general_select"
                    )

        if response_choice and response_choice != "":
            if st.button("📤 Send Response", key="send_dropdown_response"):
                print(f"DEBUG: Button clicked with response: {response_choice}")
                success = send_user_input(response_choice)
                if success:
                    print("DEBUG: Response sent successfully, rerunning...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Failed to send response. Please try again.")

        else:
            st.info("🤖 AI is thinking... Please wait for the question.")

    elif not st.session_state.game_active:
        st.info("🎉 Game completed! Select a new game to continue playing.")

# Main App
def main():
    """Main application function"""
    render_header()
    render_stats_sidebar()

    # Main content area
    if not st.session_state.game_active:
        render_game_selection()

        # Show recent conversation if exists
        if st.session_state.conversation_history:
            st.markdown("---")
            st.subheader("📜 Recent Activity")

            # Show last few messages
            recent_messages = st.session_state.conversation_history[-5:]
            for message in recent_messages:
                message_class = f"{message['type']}-message"
                st.markdown(f"""
                <div class="chat-message {message_class}">
                    <small><strong>{message['type'].title()}:</strong> {message['content']}</small>
                </div>
                """, unsafe_allow_html=True)

    else:
        render_conversation()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>🚀 <strong>Powered by LangGraph</strong> • 🤖 <strong>Multi-Agent Architecture</strong> • 🔄 <strong>Human-in-the-Loop</strong></p>
        <p style="font-size: 0.8rem;">Built with FastAPI, Streamlit, and LangGraph for seamless AI gaming experiences</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()