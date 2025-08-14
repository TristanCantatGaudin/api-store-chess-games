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


# This part is needed to interface the API with a database:
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# --- SQLAlchemy model (DB) ---
class GameItemDB(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    lichessId = Column(String, unique=True, index=True, nullable=True)
    PGN = Column(String, nullable=False)
    White = Column(String, nullable=True)
    Black = Column(String, nullable=True)
    WhiteElo = Column(Integer, nullable=True)
    BlackElo = Column(Integer, nullable=True)
    Opening = Column(String, nullable=True)
    date_added = Column(DateTime, default=datetime.utcnow)