"""
File to add 'data science' features to the tracking data

Want to add pitch control field to each frame
"""
import gzip
import io
import json
import math

import numpy as np
from tqdm import tqdm

from project.utils.mongo_setup import get_database
from project.utils.data_science.pitch_control import create_frame_pitch_control_field

db = get_database("metrica_tracking")
collection = db["processed_frames_stage_one"]

cursor = collection.find({})
cursor_data = list(cursor)


for frame in tqdm(cursor_data):
    frame["pitch_control_field"] = None
    if frame["ball_position"]["x"] is not None:
        pitch_control_field = create_frame_pitch_control_field(frame)
        # buffer = io.BytesIO()
        # np.save(buffer, pitch_control_field)
        # compressed_data = gzip.compress(buffer.getvalue())
        compressed_data = gzip.compress(
            json.dumps(pitch_control_field.tolist()).encode("utf-8")
        )

        frame["pitch_control_field"] = compressed_data


new_collection = db["processed_frames_pitch_control"]
# Delete pre-existing data to create space and upload afresh
new_collection.delete_many({})

num_chunks = math.ceil(len(cursor_data) / 5000)
for i in tqdm(range(num_chunks)):
    start = i * 5000
    end = start + 5000
    chunk = cursor_data[start:end]
    new_collection.insert_many(chunk)


# ----------------------------------------------------------------
