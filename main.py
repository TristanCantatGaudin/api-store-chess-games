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


app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

# Appending (regardless of whether the item already exists) is a POST request.
@app.post("/games", response_model=list[GameItem])
def add_game_nonpersist(item: GameItem) -> list[GameItem]:
    """
    For testing. Adds games to a temporary list. Storage does not persist over restarts.
    The input has to be passed as a JSON payload.
    Returns the full list (including the last game added).
    """
    all_games.append(item)
    return all_games