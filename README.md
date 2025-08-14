This API has the following routes and methods:

### POST on `manual_add_game`

Add a game, with data given as parameters in the URL, e.g.:

    curl -X 'POST' \
      'http://127.0.0.1:8000/manual_add_game?PGN=aaaa&lichessId=zzzz' 

In this example implementation the games are only stored as a two-key dictionary.

### POST on `add_game`

Add a game, with data passed as a JSON payload:

    curl -X 'POST' \
      'http://127.0.0.1:8000/add_game' \
      -H 'accept: application/json' \
      -d '{
      "lichessId": "string",
      "PGN": "string",
      "White": "string",
      "Black": "string",
      "WhiteElo": 0,
      "BlackElo": 0,
      "Opening": "string"
    }'

This one uses pydantic, with all arguments optional except the PGN string. 
Internally, a `date_added` field is then automatically added, but can't be set manually.

### POST on `add_game_from_lichess`

One single argument, fetches a game from lichess and parses it into our pydantic model.

## Usage

Start with: `uv run uvicorn app.main:app --reload`

Verify it is running at http://127.0.0.1:8000/

Documentation at http://127.0.0.1:8000/redoc

Swagger UI at http://127.0.0.1:8000/docs
