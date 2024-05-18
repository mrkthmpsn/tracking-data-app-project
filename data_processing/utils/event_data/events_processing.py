"""
TODO[**] File string
"""
import json

import numpy as np
import pandas as pd

from data_processing.utils.event_data.event_schemas import MatchEvent


def flatten_event(event: MatchEvent) -> dict:
    """Flatten a preliminary parsed Metrica JSON event"""
    return {
        "index": event.index,
        "team_name": event.team.name,
        "team_id": event.team.id,
        "event_type_name": event.type.name,
        "event_type_id": event.type.id,
        "subtype_ids": [subtype.id for subtype in event.subtypes]
        if isinstance(event.subtypes, list)
        else [getattr(event.subtypes, "id", None)],
        "start_frame": event.start.frame,
        "start_time": event.start.time,
        "start_x": event.start.x,
        "start_y": event.start.y,
        "end_frame": event.end.frame,
        "end_time": event.end.time,
        "end_x": event.end.x,
        "end_y": event.end.y,
        "period": event.period,
        "player_name": event.from_.name,
        "player_id": event.from_.id,
        "receiver_name": getattr(event.to, "name", None),
        "receiver_id": getattr(event.to, "id", None),
    }


# TODO[**] Change this to use path library
def create_possession_changes_from_events(events_file_path: str) -> pd.DataFrame:
    """ """
    with open(events_file_path) as f:
        events_file = json.load(f)

    events_data = [MatchEvent(**event) for event in events_file["data"]]

    match_data_df = pd.DataFrame(
        [flatten_event(event_model) for event_model in events_data]
    )

    match_data_df = match_data_df[
        ~(match_data_df["event_type_name"].isin(["FAULT RECEIVED", "BALL OUT"]))
    ]

    mask = match_data_df["event_type_name"] == "SET PIECE"
    match_data_df.loc[mask, "start_frame"] = match_data_df["end_frame"].shift()
    match_data_df.loc[mask, "start_time"] = match_data_df["end_time"].shift()
    match_data_df.loc[mask, "event_type_name"] = "BREAK IN PLAY"
    match_data_df = match_data_df[
        ~(match_data_df["event_type_name"].isin(["CARD", "CHALLENGE"]))
    ]

    match_data_df["opp_name"] = np.where(
        match_data_df["team_name"] == "Team A", "Team B", "Team A"
    )
    match_data_df["opp_id"] = np.where(
        match_data_df["team_id"] == "FIFATMA", "FIFATMB", "FIFATMA"
    )

    match_data_df["possession_phase"] = np.where(
        match_data_df["event_type_name"].isin(["PASS", "SHOT", "CARRY", "RECOVERY"]),
        match_data_df["team_id"],
        "neutral",
    )
    match_data_df["possession_phase_change"] = np.where(
        match_data_df["possession_phase"] != match_data_df["possession_phase"].shift(),
        1,
        0,
    )

    possession_change_df = match_data_df[match_data_df["possession_phase_change"] == 1][
        ["possession_phase", "start_frame", "start_time", "period"]
    ]

    return possession_change_df


def find_half_start_frames(events_file_path):
    with open(events_file_path) as f:
        events_file = json.load(f)

    events_data = [MatchEvent(**event) for event in events_file["data"]]

    match_data_df = pd.DataFrame(
        [flatten_event(event_model) for event_model in events_data]
    )

    kick_off_records = (
        match_data_df[match_data_df["event_type_name"] == "SET PIECE"]
        .groupby("period")
        .first()
        .reset_index()[["period", "start_frame"]]
        .to_dict(orient="records")
    )

    period_second_mapping = {1: 0, 2: 45 * 60}

    for kick_off in kick_off_records:
        kick_off["start_second"] = period_second_mapping[kick_off["period"]]

    return pd.DataFrame.from_records(kick_off_records)
