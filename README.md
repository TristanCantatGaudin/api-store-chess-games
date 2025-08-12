This API has the following routes and methods:

### POST on `manual_add_game`

Add a game, with data given as parameters in the URL, e.g.:

    curl -X 'POST' \
      'http://127.0.0.1:8000/manual_add_game?PGN=aaaa&lichessId=zzzz' 

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

## Usage

Start with: `uv run uvicorn main:app --reload`

Verify it is running at http://127.0.0.1:8000/

Documentation at http://127.0.0.1:8000/redoc

Swagger UI at http://127.0.0.1:8000/docs
