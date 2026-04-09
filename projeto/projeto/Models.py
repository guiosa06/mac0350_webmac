from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship 

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
    game_color: str

    games: List["Game"] = Relationship(back_populates="player")

    
class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    score: int
    
    player: Player = Relationship(back_populates="games")
    player_id: int = Field(foreign_key="player.id")