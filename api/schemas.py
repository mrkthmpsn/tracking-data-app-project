"""
File for schemas used in API validation & organisation
"""

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
    area: float


class FramePlayer(Coordinate):
    team: str
    shirt_number: int
    closest_opponent: float
    within_opp_block: bool


class APIFrame(BaseModel):
    """
    Schema for a frame of data to be returned in the `frames` API endpoint
    """

    frame_idx: int
    period: int
    match_second: Optional[float]
    phase_second: float
    ball_position: Optional[Coordinate]
    possession_phase: PossessionPhase
    passing_opportunity: bool
    players: List[FramePlayer]
    defensive_block: Optional[DefensiveBlock]
    closest_opponent_to_ball: Optional[float]
    a_target_goal: Optional[list]
    b_target_goal: Optional[list]
    possession_target_end: Optional[int]  # # Either 0 or 105
    distance_from_target_goal: Optional[float]
    in_block_opportunities: list
    pitch_control_field: Optional[bytes]
