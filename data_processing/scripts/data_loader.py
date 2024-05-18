"""
File for loading data from file to MongoDB database collection
"""
from tqdm import tqdm

from data_processing.utils.mongo_setup import get_collection


def parse_line(line):
    # The third thing is an unexplained NaN (will be explained in docs that I haven't read yet)
    frame_number, player_data, ball_data = line.split(":")
    player_positions = player_data.split(";")
    player_positions = [
        # Keeping the index is useful for use with the metadata
        {"x": pos.split(",")[0], "y": pos.split(",")[1], "idx": idx}
        for idx, pos in enumerate(player_positions)
    ]
    return {
        "frame": int(frame_number),
        "positions": player_positions,
        "ball_position": {"x": ball_data.split(",")[0], "y": ball_data.split(",")[1]},
    }


# Takes ~50-60 minutes
file_path = "data/Sample_Game_3_tracking.txt"

collection = get_collection(collection_name="frames")
collection.delete_many({})

with open(file_path, "r") as f:
    num_lines = sum(1 for line in f)

with open(file_path, "r") as file:
    for line in tqdm(file, total=num_lines):
        frame_data = parse_line(line)
        collection.insert_one(frame_data)

print("Data loading complete!")
