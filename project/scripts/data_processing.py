"""
TODO[**]: File string

"""
import math

import numpy as np
import pandas as pd
from tqdm import tqdm

from project.utils.event_data.events_processing import (
    create_possession_changes_from_events,
)
from project.utils.tracking_processing import (
    convert_to_meters,
    smooth_coordinates,
    calculate_speed,
)
from project.utils.mongo_setup import get_database

db = get_database("metrica_tracking")
collection = db["frames"]

# Fetch every fifth frame
cursor = collection.find(
    {"frame": {"$mod": [12, 0]}, "ball_position": {"$exists": True}}
)
cursor_data = list(cursor)

# TODO[*]: Make this a util rather than a basic script?
all_players = []
ball_position = []
for record in tqdm(cursor_data):
    frame_id = record["frame"]

    ball_data = record["ball_position"]
    ball_data["frame"] = frame_id
    ball_position.append(ball_data)

    for player in record["positions"]:
        player["frame"] = frame_id
        all_players.append(player)

# Process ball data
ball_df = pd.DataFrame(ball_position)
ball_df["x"] = ball_df["x"].astype(float)
ball_df["y"] = ball_df["y"].astype(float)
ball_df[["adj_x", "adj_y"]] = ball_df.apply(
    lambda row: convert_to_meters(row["x"], row["y"]), axis=1
)
ball_df = smooth_coordinates(ball_df)
ball_df = calculate_speed(ball_df, sample_frame_rate=(25 / 12))
ball_df = ball_df.replace({np.nan: None})

ball_on_screen_frames = list(ball_df[~(ball_df["x"].isna())]["frame"])

# Process player data
player_df = pd.DataFrame(all_players)
player_df["x"] = pd.to_numeric(player_df["x"])
player_df["y"] = pd.to_numeric(player_df["y"])

player_df[["adj_x", "adj_y"]] = player_df.apply(
    lambda row: convert_to_meters(row["x"], row["y"]), axis=1
)

grouped_data = player_df.groupby("idx")

processed_data = pd.DataFrame()
for player_id, grouped_df in tqdm(grouped_data):
    grouped_df = smooth_coordinates(grouped_df)
    grouped_df = calculate_speed(grouped_df, sample_frame_rate=(25 / 12))

    # Data doesn't really supply team info properly, but this is presumably right
    grouped_df["team"] = np.where(player_id <= 10, "TEAM_A", "TEAM_B")

    # TODO[*] This wouldn't work if the player's frames didn't match the ball's
    # Check for null values in either the ball or player positions
    null_mask = pd.isnull(ball_df["adj_x"])

    grouped_df["distance_to_ball"] = np.where(
        null_mask,
        np.nan,  # Assign np.nan for rows with null values
        np.sqrt(
            (
                ball_df["adj_x"].astype(float)
                - grouped_df["adj_x"].reset_index(drop=True)
            )
            ** 2
            + (
                ball_df["adj_y"].astype(float)
                - grouped_df["adj_y"].reset_index(drop=True)
            )
            ** 2
        ),
    )

    # Append the processed group to the overall DataFrame
    processed_data = pd.concat([processed_data, grouped_df])

processed_data = processed_data.replace({np.nan: None})

# Get the possession phase for each frame in the sample
# TODO[*]: Would like to check that the two dfs have the same frame indexes explicitly
frames_list = player_df["frame"].unique()

possession_phase_df = create_possession_changes_from_events(
    "./data/Sample_Game_3_events.json"
)
frames_df = pd.DataFrame(frames_list, columns=["frame"])
frame_possession_phase_df = pd.merge_asof(
    frames_df.astype(float),
    possession_phase_df.fillna(0),
    left_on="frame",
    right_on="start_frame",
)
frame_possession_phase_df["frame"] = frame_possession_phase_df["frame"].astype(int)
frame_possession_phase_data = (
    frame_possession_phase_df[["frame", "possession_phase"]]
    .set_index("frame")
    .to_dict(orient="index")
)


# Iterate over the unique frames
structured_data = []

for frame in tqdm(frames_list):
    # Initialize a dictionary for this frame - convert to int for serializing
    frame_data = {"frame": int(frame)}

    # Extract ball position for this frame
    ball_data = ball_df[ball_df["frame"] == frame]
    frame_data["ball_position"] = ball_data.to_dict(orient="records")[0]

    # Extract player data for this frame
    player_data = processed_data[processed_data["frame"] == frame].set_index(
        "idx", drop=False
    )
    player_data.index = player_data.index.map(str)

    frame_data["players"] = player_data.to_dict(orient="index")

    frame_data["possession_phase"] = frame_possession_phase_data[frame][
        "possession_phase"
    ]

    # Append this frame's data to the list
    structured_data.append(frame_data)


# ----------------------------------------------------------------

new_collection = db["processed_frames_stage_one"]
# Delete pre-existing data to upload afresh
new_collection.delete_many(filter={})

num_chunks = math.ceil(len(structured_data) / 5000)
for i in tqdm(range(num_chunks)):
    start = i * 5000
    end = start + 5000
    chunk = structured_data[start:end]
    new_collection.insert_many(chunk)
