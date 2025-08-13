from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel, Field
import httpx

all_games = []

# Use a pydantic object instead of a basic Python dictionary.
# User-facing input model: this is what can be sent to the API.
class GameItemInput(BaseModel):
    lichessId: str = None
    PGN: str
    White: str = None
    Black: str = None
    WhiteElo: int = None
    BlackElo: int = None
    Opening: str = None

# Internal/output model: this is what is stored and returned.
class GameItem(GameItemInput):
    date_added: datetime = Field(default_factory=datetime.utcnow)
# Note: some static typecheckers like mypy would prefer us to import Optional:
#   from typing import Optional
# and write optional arguments as:
#   lichessId: Optional[str] = None


app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

# Appending (regardless of whether the item already exists) is a POST request.
@app.post("/manual_add_game")
def add_game_manually_nonpersist(PGN: str, lichessId: str = None):
    """
    For testing. Adds games to a temporary list. Storage does not persist over restarts.
    Parameters can be parsed in URL, e.g.:
    `curl -X 'POST' 'http://127.0.0.1:8000/manual_add_game?PGN=1.%20e4%20e5&lichessId=abc123'`
    Games are stored as a two-key dictionary.
    Returns the full list (including the last game added).
    """
    all_games.append({"PGN":PGN, "lichessId":lichessId})
    return all_games

@app.post("/add_game", response_model=list[GameItem])
def add_game_nonpersist(item: GameItemInput) -> list[GameItem]:
    """
    For testing. Adds games to a temporary list. Storage does not persist over restarts.
    The input has to be passed as a JSON payload.
    Games are stored and returned as pydantic objects.
    Returns the full list (including the last game added).
    """
    all_games.append(item)
    return all_games

@app.post("/add_game_from_lichess", response_model=list[GameItem])
async def add_game_from_lichess(lichessId: str):
    """
    Fetch a game from the Lichess API using the lichessId (e.g. q7ZvsdUF).
    Parses the returned data into a GameItem and appends it to the in-memory list.
    Returns the full list of games.
    """
    lichess_api_url = f"https://lichess.org/game/export/{lichessId}"

    async with httpx.AsyncClient() as client:
        response = await client.get(lichess_api_url, params={"tags": True, "clocks": False, "evals": False, "pgnInJson": True}, headers={"Accept": "application/json"})
        if response.status_code != 200:
            return {"error": f"Failed to fetch game from Lichess. Status code: {response.status_code}"}

        game_data = response.json()

        try:
            game_item = GameItem(
                lichessId=lichessId,
                PGN=game_data.get("pgn").split("\n\n")[1],
                White=game_data.get("players", {}).get("white", {}).get("user", {}).get("name"),
                Black=game_data.get("players", {}).get("black", {}).get("user", {}).get("name"),
                WhiteElo=game_data.get("players", {}).get("white", {}).get("rating"),
                BlackElo=game_data.get("players", {}).get("black", {}).get("rating"),
                Opening=game_data.get("opening", {}).get("name")
            )
        except Exception as e:
            return {"error": f"Failed to parse game data: {str(e)}"}

        all_games.append(game_item)
        return all_games