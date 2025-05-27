from langchain_core.messages import BaseMessage

from app.backend.agents.number_game_agent import number_game_agent


def number_game_node(state):
    try:
        print(f"DEBUG: number_game_node called with state: {state}")

        # Invoke the react agent which will use the tool
        result = number_game_agent.invoke(state)
        print(f"DEBUG: Agent result: {result}")

        # Handle interrupt results from the tool
        if isinstance(result, dict) and result.get("type") == "interrupt":
            print(f"DEBUG: Tool returned interrupt: {result}")
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
        updated_count = state.get('number_game_count', 0) + 1
        return {
            **state,
            **result,
            'number_game_count': updated_count
        }

    except Exception as e:
        print(f"DEBUG: Exception in number_game_node: {e}")
        return {
            **state,
            "error": str(e),
            "messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]
        }