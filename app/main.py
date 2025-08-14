from fastapi import FastAPI, Depends, HTTPException, status, Query
import httpx
from .models import GameItemInput, GameItem

# For the DB interface:
from sqlalchemy.orm import Session
from .db import SessionLocal, engine
from .models import GameItemDB, Base

# In-memory storage:
games_as_dicts = [] # for our dummy manual_add_game to store dicts
all_game_items: list[GameItem] = [] # for methods storing game items

# Create the table if it doesn't exist:
Base.metadata.create_all(bind=engine)

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
    games_as_dicts.append({"PGN": PGN, "lichessId": lichessId})
    return games_as_dicts


@app.post("/add_game", response_model=list[GameItem])
def add_game_nonpersist(item: GameItemInput) -> list[GameItem]:
    """
    For testing. Adds games to a temporary list. Storage does not persist over restarts.
    The input has to be passed as a JSON payload.
    Games are stored and returned as pydantic objects.
    Returns the full list (including the last game added).
    """
    all_game_items.append(item)
    return all_game_items


@app.post("/add_game_from_lichess", response_model=list[GameItem])
async def add_game_from_lichess(lichessId: str):
    """
    Fetch a game from the Lichess API using the lichessId (e.g. q7ZvsdUF).
    Parses the returned data into a GameItem and appends it to the in-memory list.
    Returns the full list of games.
    """
    lichess_api_url = f"https://lichess.org/game/export/{lichessId}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            lichess_api_url,
            params={"tags": True, "clocks": False, "evals": False, "pgnInJson": True},
            headers={"Accept": "application/json"},
        )
        if response.status_code != 200:
            return {
                "error": f"Failed to fetch game from Lichess. Status code: {response.status_code}"
            }

        game_data = response.json()

        try:
            game_item = GameItem(
                lichessId=lichessId,
                PGN=game_data.get("pgn").split("\n\n")[1],
                White=game_data.get("players", {})
                .get("white", {})
                .get("user", {})
                .get("name"),
                Black=game_data.get("players", {})
                .get("black", {})
                .get("user", {})
                .get("name"),
                WhiteElo=game_data.get("players", {}).get("white", {}).get("rating"),
                BlackElo=game_data.get("players", {}).get("black", {}).get("rating"),
                Opening=game_data.get("opening", {}).get("name"),
            )
        except Exception as e:
            return {"error": f"Failed to parse game data: {str(e)}"}

        all_game_items.append(game_item)
        return all_game_items

# This method stores into the database:
# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/store_game", response_model=GameItem)
def store_game(item: GameItemInput, db: Session = Depends(get_db)):
    """
    Stores a game in the PostgreSQL database.
    """
    # Check if a game with the same lichessId already exists
    existing_game = db.query(GameItemDB).filter(GameItemDB.lichessId == item.lichessId).first()
    if existing_game:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A game with this lichessId already exists."
        )

    db_game = GameItemDB(**item.dict())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

# About error handling: since our model has "unique=True" for the lichessID field in the DB,
# we cannot add the same game twice. So we have to test for this, and decide what do to if it happens.
# We can raise a HTTP error (409 makes sense here), or we can return some JSON message, in which case
# we need to create a Message pydantic item and make the return type of the method:
#     response_model=Union[GameItem, Message]
# because the function is currently not allowed to return anything else.

@app.get("/recently_added_games", response_model=list[GameItem])
def get_recent_games(n: int = Query(3, gt=0), db: Session = Depends(get_db)):
    """
    Retrieve the most recently added N games.
    Defaults to 3.
    """
    recent_games = db.query(GameItemDB).order_by(GameItemDB.date_added.desc()).limit(n).all()
    return recent_games

# For more specific filters, we can have more arguments (with default None values) and chain filters:
#     query = db.query(GameItemDB)
#     if player:
#         query = query.filter(or_(GameItemDB.White == player, GameItemDB.Black == player))
#     if opening:
#         query = query.filter(GameItemDB.Opening == opening)
#     recent_games = query.order_by(GameItemDB.date_added.desc()).limit(n).all()