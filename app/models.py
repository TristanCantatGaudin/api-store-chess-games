from pydantic import BaseModel, Field
from datetime import datetime




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