from langgraph.prebuilt import create_react_agent
from ..utils.model import model
from ..tools.end_game_tools import end_game

end_game_agent = create_react_agent(
    model=model,
    tools=[end_game],
    name="end_game_agent",
    prompt="You are essentially a game ending agent. If the user decides to quit, "
           "you will show them the number of games they have played."
           "You may use end_game to display the stats.\n\n"

)