from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Coordinate(BaseModel):
    x: float
    y: float


class PossessionPhase(Enum):
    HOME = "FIFATMA"
    AWAY = "FIFATMB"
    NEUTRAL = "neutral"


class InBlockOpportunity(BaseModel):
    points: List[Coordinate]


class DefensiveBlock(BaseModel):
    top: float
    bottom: float
    left: float
    right: float


class FramePlayer(Coordinate):
    team: str
    shirt_number: int


class APIFrame(BaseModel):
    """
    What does this need...

    Ball position
    Possession phase
    Team - players - do you even need this if you have the player team info in the players data?
    Player info - position
    In-block opportunities
    Defensive block
    Pitch control
    """

    frame_idx: int
    ball_position: Optional[Coordinate]
    possession_phase: PossessionPhase
    players: List[FramePlayer]
    defensive_block: Optional[DefensiveBlock]
    in_block_opportunities: list
    pitch_control_field: Optional[bytes]
