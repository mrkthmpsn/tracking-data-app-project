"""
Schemas for Metrica event data representations
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field


class Team(BaseModel):
    name: str
    id: str


class EventType(BaseModel):
    name: str
    id: int


class EventPosition(BaseModel):
    frame: int
    time: float
    x: Optional[float]
    y: Optional[float]


class Player(BaseModel):
    name: str
    id: str


class MatchEvent(BaseModel):
    index: int
    team: Team
    type: EventType
    subtypes: Optional[Union[EventType, List[EventType]]]
    start: EventPosition
    end: EventPosition
    period: int
    from_: Player = Field(..., alias="from")  # 'from' is a reserved keyword in Python
    to: Optional[Player]
