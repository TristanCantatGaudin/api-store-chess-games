from fastapi.testclient import TestClient
from app.main import app
from app.models import GameItemInput

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_manual_add_game():
    response = client.post("/manual_add_game?PGN=1. e4 e5&lichessId=abc123")
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    assert json_data[-1] == {"PGN": "1. e4 e5", "lichessId": "abc123"}


def test_add_game():
    game_data = {
        "PGN": "1. d4 d5",
        "lichessId": "xyz789",
        "White": "Alice",
        "Black": "Bob",
        "WhiteElo": 1500,
        "BlackElo": 1400,
        "Opening": "Queen's Gambit",
    }

    response = client.post("/add_game", json=game_data)
    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    assert json_data[-1]["PGN"] == "1. d4 d5"
    assert json_data[-1]["White"] == "Alice"


# Testing the method that makes a live call to the lichess API is also possible.
# We could mock the response (to allow offline testing) with respx.get(...).mock(...)
# or handle the case where the issue comes from lichess and not from our code.