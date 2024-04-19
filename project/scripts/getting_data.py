import gzip
import io
import time

import numpy as np

from project.utils.mongo_setup import get_database

db = get_database("metrica_tracking")
collection = db["processed_frames_stage_three"]

cursor = collection.find({})
cursor_data = list(cursor)

clip_frames = cursor_data[5485:5490]

players_data = [
    {
        "id": int(player_idx),
        "shirtNumber": int(player_idx),
        "positions": [
            {
                "x": frame["players"][str(player_idx)]["adj_x"],
                "y": frame["players"][str(player_idx)]["adj_y"],
            }
            for frame in clip_frames
        ],
    }
    for player_idx in range(11)
]
defensive_block_data = [frame["defensive_block_boundaries"] for frame in clip_frames]

# frame_list = []
# for frame in clip_frames:
decompressed_data = gzip.decompress(cursor_data[5489]["pitch_control_field"])
# Reconstruct the BytesIO object
buffer = io.BytesIO(decompressed_data)
# Load the NumPy array
reconstructed_pitch_control_field = np.load(buffer)
unit_list = []
# TODO[***] Try something here where data is grouped by 3x2 for visualisation purposes
for i in range(len(reconstructed_pitch_control_field)):
    for j in range(105):
        temp_var = {
            "x": j,
            "y": i,
            "i": j,
            "j": i,
            "height": 1,
            "width": 1,
            "value": reconstructed_pitch_control_field[i][j],
        }
        unit_list.append(temp_var)

# frame_list.append(unit_list)


def aggregate_grid(data, new_width=35, new_height=34):
    # Assuming data is a NumPy array of shape (68, 105)
    old_height, old_width = data.shape
    grouped_data = np.zeros((new_height, new_width))

    # Factor by which the original dimensions are reduced
    width_factor = old_width // new_width
    height_factor = old_height // new_height

    for i in range(new_height):
        for j in range(new_width):
            # Calculate the start and end indices of the original grid
            start_i = i * height_factor
            end_i = start_i + height_factor
            start_j = j * width_factor
            end_j = start_j + width_factor

            # Extract the subgrid and calculate the mean
            subgrid = data[start_i:end_i, start_j:end_j]
            grouped_data[i, j] = np.mean(subgrid)

    return grouped_data


decompressed_data = gzip.decompress(cursor_data[5489]["pitch_control_field"])
# Reconstruct the BytesIO object
buffer = io.BytesIO(decompressed_data)
# Load the NumPy array
reconstructed_pitch_control_field = np.load(buffer)
reduced_grid = aggregate_grid(reconstructed_pitch_control_field)
unit_list = []
# TODO[***] Try something here where data is grouped by 3x2 for visualisation purposes
for i in range(len(reduced_grid)):
    for j in range(len(reduced_grid[0])):
        temp_var = {
            "x": j * 3,
            "y": i * 2,
            "i": j,
            "j": i,
            "height": 2,
            "width": 3,
            "value": reduced_grid[i][j],
        }
        unit_list.append(temp_var)
