"""
File for assorted utils to create metrics from processed tracking data
"""
from typing import Optional

import numpy as np
from pydantic import BaseModel
from tqdm import tqdm

from project.utils.data_science.pitch_control import decompress_gzip_pitch_control_field


def mark_passing_opportunities(player_frames, time_threshold, frame_rate):
    passing_opportunities = []
    proximity_start = None  # Index of when the player first got close to the ball

    for index, frame in enumerate(player_frames):
        if frame["distance_from_ball"] <= 1:  # Check if within one meter
            if proximity_start is None:
                proximity_start = index  # Mark the start of proximity
            proximity_duration = (index - proximity_start + 1) / frame_rate
            if proximity_duration >= time_threshold:
                passing_opportunities.append(index)
        else:
            proximity_start = None  # Reset when the player moves away

    return passing_opportunities


def _update_proximity_info(player_info, frame_data, distance_threshold, frame_rate):
    """
    TODO[**] Document this function
    :param player_info:
    :param frame_data:
    :param distance_threshold:
    :param frame_rate:
    :return:
    """
    distance_to_ball = frame_data["players"][player_info["id"]]["distance_to_ball"]

    if distance_to_ball <= distance_threshold and (
        (
            frame_data["players"][player_info["id"]]["team"] == "TEAM_A"
            and frame_data["possession_phase"] == "FIFATMA"
        )
        or (
            (
                frame_data["players"][player_info["id"]]["team"] == "TEAM_B"
                and frame_data["possession_phase"] == "FIFATMB"
            )
        )
    ):

        if player_info["proximity_start"] is None:
            player_info["proximity_start"] = frame_data["frame"]
        player_info["proximity_duration"] += 1 / frame_rate
    else:
        player_info["proximity_start"] = None
        player_info["proximity_duration"] = 0

    return player_info


def annotate_passing_opportunities(
    frames, distance_threshold, time_threshold, frame_rate
):
    """
    TODO[***] Document this function
    :param frames:
    :param distance_threshold:
    :param time_threshold:
    :param frame_rate:
    :return:
    """
    players_info = {
        player_id: {"id": player_id, "proximity_start": None, "proximity_duration": 0}
        for player_id in frames[0]["players"].keys()
    }

    frame_passing_opportunities = {frame["frame"]: [] for frame in frames}

    for frame_index, frame in tqdm(enumerate(frames)):
        # Skip if no ball position
        if frame["ball_position"]["x"] is None:
            continue
        for player_id, player_info in players_info.items():
            players_info[player_id] = _update_proximity_info(
                player_info, frame, distance_threshold, frame_rate
            )
            new_player_info = players_info[player_id]
            # Check if the time threshold is reached
            if new_player_info["proximity_duration"] >= time_threshold:
                # Mark all frames from proximity_start to the current frame as passing opportunities
                start_index = new_player_info["proximity_start"]
                # TODO[**] This range doesn't really match the actual frame index possibilities
                for index in range(start_index, frame["frame"] + 1):

                    if (
                        index in frame_passing_opportunities
                        and player_id not in frame_passing_opportunities[index]
                    ):
                        frame_passing_opportunities[index].append(player_id)

    return frame_passing_opportunities


class DefensiveBlockData(BaseModel):
    left: int
    right: int
    top: int
    bottom: int


def get_defensive_block_boundaries(frame_data) -> Optional[DefensiveBlockData]:
    """

    :return:
    """
    if frame_data["possession_phase"] == "neutral":
        return None

    # TODO[*] Can get away with it with this data, but both of these criteria filters are hacky
    out_of_possession_team = (
        "TEAM_B" if frame_data["possession_phase"] == "FIFATMA" else "TEAM_A"
    )
    outfielder_positions = [
        (player_data["adj_x"], player_data["adj_y"])
        for player_id, player_data in frame_data["players"].items()
        if player_data["team"] == out_of_possession_team
        and player_id not in ["0", "11"]
    ]

    # TODO[*] It doesn't matter practically, but would be nice to account for which way team is defending

    # Sort positions
    sorted_by_x = sorted(
        outfielder_positions, key=lambda x: x[0]
    )  # Sort by x coordinate
    sorted_by_y = sorted(
        outfielder_positions, key=lambda x: x[1]
    )  # Sort by y coordinate

    # Get 2nd furthest in each direction, convert to integers for indexing
    left = int(sorted_by_x[1][0])
    right = int(sorted_by_x[-2][0])
    top = int(sorted_by_y[1][1])
    bottom = int(sorted_by_y[-2][1])

    return DefensiveBlockData(left=left, right=right, top=top, bottom=bottom)


def search_area_for_value(
    frame_data, defensive_block_data: DefensiveBlockData, target_avg
):
    """
    Search for areas within the pitch control array that have an average value of target_avg.
    pitch_control is a 105x68 2D array.
    """
    matching_areas = []

    if (
        frame_data["possession_phase"] == "neutral"
        or not frame_data["passing_opportunity"]
        or frame_data["ball_position"]["x"] is None
    ):
        return matching_areas

    # Adjusted to ensure we stay within the bounds of the defensive block rectangle
    for x in range(defensive_block_data.left, defensive_block_data.right - 2):
        for y in range(defensive_block_data.top, defensive_block_data.bottom - 2):
            distance_to_ball = np.sqrt(
                (x - frame_data["ball_position"]["adj_x"]) ** 2
                + (y - frame_data["ball_position"]["adj_y"]) ** 2
            )
            target_range = max(2, int(np.sqrt(distance_to_ball)))

            # Get the area
            area = decompress_gzip_pitch_control_field(
                frame_data["pitch_control_field"]
            )[y : y + target_range, x : x + target_range]

            # Check if the area is fully within bounds and calculate its average
            if (
                area.shape == (target_range, target_range)
                and (
                    np.mean(area) >= target_avg
                    if frame_data["possession_phase"] == "FIFATMB"
                    else np.mean(area) <= target_avg - 0.5
                )
                # We want to rule out players who are on the ball as being classed as opportunities
                and distance_to_ball >= 3
            ):
                matching_areas.append((x, y, x + target_range, y + target_range))

    return matching_areas
