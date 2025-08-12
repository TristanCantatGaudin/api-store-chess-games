from fastapi import FastAPI
from pydantic import BaseModel

all_games = []

# Use a pydantic object instead of a basic Python dictionary.
class GameItem(BaseModel):
    lichessId: str = None # optional
    PGN: str # NOT optional!
    White: str = None
    Black: str = None
    WhiteElo: int = None
    BlackElo: int = None
    Opening: str = None
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
def add_game_nonpersist(item: GameItem) -> list[GameItem]:
    """
    For testing. Adds games to a temporary list. Storage does not persist over restarts.
    The input has to be passed as a JSON payload.
    Games are stored and returned as pydantic objects.
    Returns the full list (including the last game added).
    """
    all_games.append(item)
    return all_games

