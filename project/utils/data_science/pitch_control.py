"""
File for pitch control utils
"""
import gzip
import io
import time
from typing import List

import numpy as np


# TODO[**] Check this over properly, add type hints, etc
# def vectorized_time_to_reach_grid(
#     current_x,
#     current_y,
#     velocity_x,
#     velocity_y,
#     reaction_time: float = 0.2,
#     acceleration: float = 3,
#     deceleration: float = 3,
#     max_speed=8,
#     pitch_length=105,
#     pitch_width=68,
# ):
#     """
#     Calculate the time for a player to reach every point on a pitch grid.
#
#     :param current_x, current_y: Current position of the player
#     :param velocity_x, velocity_y: Current velocity of the player in x and y directions
#     :param reaction_time: Initial reaction time of the player
#     :param acceleration, deceleration: Player's acceleration and deceleration capacity
#     :param max_speed: Maximum speed of the player
#     :param pitch_length, pitch_width: Dimensions of the pitch
#
#     :return: 2D NumPy array of times to reach each point on the pitch grid
#     """
#     # Create a grid of target points
#     target_x, target_y = np.meshgrid(np.arange(pitch_length), np.arange(pitch_width))
#
#     # Calculate the distance to the target points
#     distances = np.sqrt((target_x - current_x) ** 2 + (target_y - current_y) ** 2)
#
#     # Calculate the current speed
#     current_speed = np.sqrt(velocity_x**2 + velocity_y**2)
#
#     # If already at or above max speed, no acceleration time is needed
#     if current_speed >= max_speed:
#         time_to_reach = distances / current_speed + reaction_time
#         return time_to_reach
#
#     # Time and distance to reach max speed
#     time_to_max_speed = (max_speed - current_speed) / acceleration
#     distance_to_max_speed = (
#         current_speed * time_to_max_speed + 0.5 * acceleration * time_to_max_speed**2
#     )
#
#     # Time to decelerate from max speed to zero
#     time_to_decelerate = max_speed / deceleration
#     distance_to_decelerate = (
#         max_speed * time_to_decelerate - 0.5 * deceleration * time_to_decelerate**2
#     )
#
#     # Total distance covered during acceleration and deceleration
#     total_distance_accel_decel = distance_to_max_speed + distance_to_decelerate
#
#     # Direct deceleration cases
#     direct_decel_cases = distances <= total_distance_accel_decel
#
#     decel_time = np.zeros_like(distances)
#     decel_time[direct_decel_cases] = (
#         np.sqrt(2 * distances[direct_decel_cases] / acceleration) + reaction_time
#     )
#
#     # Cases where max speed is reached
#     full_speed_cases = ~direct_decel_cases
#
#     remaining_distance = np.where(
#         full_speed_cases, distances - total_distance_accel_decel, 0
#     )
#     time_at_max_speed = remaining_distance / max_speed
#
#     # Total time for full speed cases
#     total_time_full_speed = (
#         time_to_max_speed + time_at_max_speed + time_to_decelerate + reaction_time
#     )
#
#     full_speed_time = np.full_like(distances, fill_value=total_time_full_speed)
#
#     total_time = np.where(direct_decel_cases, decel_time, full_speed_time)
#
#     return total_time


def vectorized_time_to_reach_grid(
    current_x,
    current_y,
    velocity_x,
    velocity_y,
    reaction_time=0.2,
    acceleration=3,
    max_speed=8,
    pitch_length=105,
    pitch_width=68,
):
    """
    Calculate the time for a player to reach every point on a pitch grid based on their
    reaction time, acceleration to max speed, and travel at max speed.

    Deceleration is not considered in this model.

    :return: 2D NumPy array of times to reach each point on the pitch grid.
    """
    # Create a grid of target points.
    target_x, target_y = np.meshgrid(
        np.linspace(0, pitch_length, num=pitch_length),
        np.linspace(0, pitch_width, num=pitch_width),
    )

    # Calculate the distance to each target point from the current position.
    distances = np.sqrt((target_x - current_x) ** 2 + (target_y - current_y) ** 2)

    # Calculate the time it takes to reach each point at maximum speed.
    # Time to accelerate to max speed:
    initial_speed = np.sqrt(velocity_x**2 + velocity_y**2)
    time_to_max_speed = np.maximum((max_speed - initial_speed) / acceleration, 0)

    # Distance covered during acceleration to max speed:
    distance_to_max_speed = (
        initial_speed * time_to_max_speed + 0.5 * acceleration * time_to_max_speed**2
    )

    # Points that are reached during the acceleration phase:
    is_acceleration_phase = distances <= distance_to_max_speed

    # Time to reach points that are farther than the acceleration distance:
    time_to_reach = np.where(
        is_acceleration_phase,
        np.sqrt(2 * distances / acceleration),
        time_to_max_speed + (distances - distance_to_max_speed) / max_speed,
    )

    # Adding reaction time to all points:
    time_to_reach += reaction_time

    return time_to_reach


class PitchControlPlayer:
    """Player representation class for a pitch control model"""

    def __init__(
        self, player_id, current_x, current_y, velocity_x, velocity_y, team, is_gk
    ):
        self.player_id = player_id
        self.current_x = current_x
        self.current_y = current_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.team = team
        self.is_gk = is_gk

        # TODO[*] Set all variables on the player, even though many will be defaults
        self.time_distance_field = vectorized_time_to_reach_grid(
            current_x=current_x,
            current_y=current_y,
            velocity_x=velocity_x,
            velocity_y=velocity_y,
        )


def calculate_control_probability_at_point(
    player_time_distance_fields, player_teams, x, y
):
    """
    Calculate control probability at a specific point on the pitch.

    :param player_time_distance_fields: Time-distance fields for players (list of 2D arrays)
    :param x, y: Point coordinates on the pitch
    :param num_closest_players: Number of closest players to consider

    :return: Control probability for one of the teams at the point (x, y)
    """
    # Extract the times for all players to reach the point (x, y)
    times_to_point = player_time_distance_fields[:, y, x]

    # If nobody is close to the point then return neutral & save calculation
    if np.min(times_to_point) > 4.2:
        return 0.5

    # Initialize minimum times for both teams
    team_a_mask = player_teams == "TEAM_A"
    team_b_mask = player_teams == "TEAM_B"
    min_time_team_a = np.min(times_to_point[team_a_mask])
    min_time_team_b = np.min(times_to_point[team_b_mask])

    # Calculate control probability for Team A
    # A simple model: control is inversely proportional to the time difference
    if min_time_team_a == min_time_team_b:
        return 0.5  # Equal control if both teams reach at the same time
    else:
        control_probability = 1 / (1 + np.exp(min_time_team_b - min_time_team_a))
        return control_probability


def calculate_pitch_control_field(players):
    """
    Calculate the pitch control probabilities for each team.

    :return: 2D array representing control probabilities across the pitch
    """
    PITCH_LENGTH, PITCH_WIDTH = 105, 68
    pitch_control = np.zeros((PITCH_WIDTH, PITCH_LENGTH), dtype=np.float16)

    player_time_distance_fields = np.array(
        [player.time_distance_field for player in players], dtype=np.float16
    )
    player_teams = np.array([player.team for player in players])

    for x in range(PITCH_LENGTH):
        for y in range(PITCH_WIDTH):
            pitch_control[y, x] = calculate_control_probability_at_point(
                player_time_distance_fields=player_time_distance_fields,
                player_teams=player_teams,
                x=x,
                y=y,
            )

    return pitch_control


class PitchControlPitchMoment:
    """Pitch representation class for a pitch control model"""

    def __init__(
        self,
        width_m,
        height_m,
        players: List[PitchControlPlayer],
        in_possession_team: str,
    ):
        self.width = width_m
        self.height = height_m
        self.players = players
        self.in_possession_team = in_possession_team
        self.pitch_control_field = calculate_pitch_control_field(self.players)


def create_frame_pitch_control_field(frame_data) -> np.ndarray:
    player_dict = {}

    for idx, player in enumerate(frame_data["players"].values()):
        player_dict[idx] = PitchControlPlayer(
            player_id=player["idx"],
            current_x=player["adj_x"],
            current_y=player["adj_y"],
            velocity_x=player["delta_x"] or 0,
            velocity_y=player["delta_y"] or 0,
            team=player["team"],
            # Assuming that the tracking data is ordered such that 1st and 12th positions are goalkeepers
            is_gk=player["idx"] in [0, 11],
        )

    var2 = PitchControlPitchMoment(
        height_m=105,
        width_m=68,
        players=list(player_dict.values()),
        in_possession_team="TEAM_A",
    )

    return var2.pitch_control_field


def decompress_gzip_pitch_control_field(stored_pitch_control_field):

    # Update the heatmap
    decompressed_data = gzip.decompress(stored_pitch_control_field)
    # Reconstruct the BytesIO object
    buffer = io.BytesIO(decompressed_data)
    # Load the NumPy array
    reconstructed_pitch_control_field = np.load(buffer)

    return reconstructed_pitch_control_field
