"""
Pitch for non-pitch control post-processing tasks

- Defensive block
- Passing opportunity
- Incisive passing opportunity
"""
import math
import time

import pandas as pd
from shapely import box, unary_union, Point, Polygon, MultiPolygon
from tqdm import tqdm

from project.utils.data_science.metrics import (
    annotate_passing_opportunities,
    get_defensive_block_boundaries,
    search_area_for_value,
)
from project.utils.mongo_setup import get_database
from project.visualisation.utils import SoccerAnimation


db = get_database("metrica_tracking")
collection = db["processed_frames_pitch_control"]

pre_cursor_time = time.perf_counter()
cursor = collection.find({})
cursor_data = list(cursor)
post_cursor_time = time.perf_counter()
passing_opportunities = annotate_passing_opportunities(
    frames=cursor_data, distance_threshold=1.5, time_threshold=1, frame_rate=25 / 12
)
post_passing_opportunities_time = time.perf_counter()
for frame in tqdm(cursor_data):
    frame["passing_opportunity"] = len(passing_opportunities[frame["frame"]]) > 0

    defensive_block_boundaries = get_defensive_block_boundaries(frame)
    frame["defensive_block_boundaries"] = (
        None
        if defensive_block_boundaries is None
        else defensive_block_boundaries.dict()
    )

    # TODO[***] Need to remove opportunity if it's taken up by the player on the ball. Maybe min threshold for
    #  opportunity distance from ball would do it?
    in_block_opportunities = search_area_for_value(
        frame_data=frame,
        defensive_block_data=defensive_block_boundaries,
        target_avg=0.75,
    )
    merged_opportunities = unary_union(
        [box(*option) for option in in_block_opportunities]
    )
    if isinstance(merged_opportunities, Polygon):
        merged_opportunities = MultiPolygon([merged_opportunities])

    frame["in_block_receiver_opportunities"] = len(merged_opportunities.geoms)
    frame["in_block_receiver_opportunities_coords"] = [
        list(polygon.exterior.coords) for polygon in merged_opportunities.geoms
    ]

    for player_id, player_data in frame["players"].items():
        player_data["passing_opportunity"] = (
            player_id in passing_opportunities[frame["frame"]]
        )
        player_loc = Point(player_data["adj_x"], player_data["adj_y"])
        player_data["in_block_receiver_opportunity"] = False
        for polygon in merged_opportunities.geoms:
            if player_loc.within(polygon):
                player_data["in_block_receiver_opportunity"] = True

final_time = time.perf_counter()
print(f"total time: {final_time - pre_cursor_time}")
new_collection = db["processed_frames_stage_three"]
# Delete pre-existing data to upload afresh
new_collection.delete_many(filter={})

num_chunks = math.ceil(len(cursor_data) / 5000)
for i in tqdm(range(num_chunks)):
    start = i * 5000
    end = start + 5000
    chunk = cursor_data[start:end]
    new_collection.insert_many(chunk)

# example_frame = cursor_data[5485]


db = get_database("metrica_tracking")
collection = db["processed_frames_stage_three"]
cursor = collection.find({})
cursor_data = list(cursor)

soccer_anim = SoccerAnimation(num_players=22)
soccer_anim.plot_animation(cursor_data[5485:5590])

clip_frames = cursor_data[5485:5590]
clip_df_records = [
    {
        "frame": frame["frame"],
        "possession_phase": frame["possession_phase"],
        "passing_opportunity": frame["passing_opportunity"],
        "in_block_receiver_opportunities": frame["in_block_receiver_opportunities"],
    }
    for frame in clip_frames
]
clip_df = pd.DataFrame(clip_df_records)
grouped_clip_df = clip_df.groupby("possession_phase").agg(
    {
        "frame": "count",
        "passing_opportunity": "sum",
        "in_block_receiver_opportunities": lambda x: (x > 0).sum(),
    }
)
