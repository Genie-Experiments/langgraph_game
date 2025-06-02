def word_game_node(state):
    print(f"DEBUG: word_game_node called - calling agent which will use the tool")

    # Call the word game agent, which should use the play_word_game tool
    from app.backend.agents.word_game_agent import word_game_agent

    # The agent will handle the tool orchestration
    result = word_game_agent.invoke({"messages": state.get("messages", [])})

    print(f"DEBUG: Agent completed: {result}")

    # Agent completed without interruption - game is finished  
    return {
        **state,
        'word_game_count': state.get('word_game_count', 0) + 1,
        'messages': state.get('messages', []) + result.get('messages', [])
    }

    # DO NOT CATCH GraphInterrupt - let it bubble up!
    # GraphInterrupt should be handled by LangGraph automatically