from langchain_core.messages import BaseMessage
from app.backend.agents.word_game_agent import word_game_agent


def word_game_node(state):
    try:
        print(f"🔤 DEBUG: word_game_node called with state: {state}")

        # Invoke the react agent which will use the tool
        print(f"🔤 DEBUG: About to invoke word_game_agent")
        result = word_game_agent.invoke(state)
        print(f"🔤 DEBUG: Agent result: {result}")
        print(f"🔤 DEBUG: Agent result type: {type(result)}")

        # Check if result contains messages to see what the agent did
        if "messages" in result:
            print(f"🔤 DEBUG: Agent generated {len(result['messages'])} messages")
            for i, msg in enumerate(result['messages']):
                if isinstance(msg, BaseMessage):
                    print(f"🔤 DEBUG: Message {i}: {msg.__class__.__name__} - {msg.content[:100]}...")
                else:
                    print(f"🔤 DEBUG: Message {i}: {msg}")

        # Handle interrupt results from the tool
        if isinstance(result, dict) and result.get("type") == "interrupt":
            print(f"🔤 DEBUG: Tool returned interrupt: {result}")
            return result

        # Convert LangChain messages to dicts
        if "messages" in result:
            converted_messages = []
            for msg in result["messages"]:
                if isinstance(msg, BaseMessage):
                    converted_messages.append({
                        "role": "assistant" if msg.__class__.__name__ == "AIMessage" else "user",
                        "content": msg.content
                    })
                else:
                    converted_messages.append(msg)
            result["messages"] = converted_messages

        # Return updated state
        updated_count = state.get('word_game_count', 0) + 1
        final_result = {
            **state,
            **result,
            'word_game_count': updated_count
        }

        print(f"🔤 DEBUG: Returning final result with {len(final_result)} keys")
        return final_result

    except Exception as e:
        print(f"🔤 DEBUG: Exception in word_game_node: {e}")
        import traceback
        print(f"🔤 DEBUG: Traceback: {traceback.format_exc()}")
        return {
            **state,
            "error": str(e),
            "messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]
        }