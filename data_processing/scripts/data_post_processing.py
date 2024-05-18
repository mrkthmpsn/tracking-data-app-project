"""
Pitch for non-pitch control post-processing tasks

Current processing features:
- Presence of 'passing opportunity' in a frame
- Defensive block boundaries
- Whether attacking players are within defensive block
- Closest opponent to each player
"""
import math


import numpy as np
from tqdm import tqdm

from data_processing.utils.data_science.metrics import (
    annotate_passing_opportunities,
    get_defensive_block_boundaries,
    search_area_for_value,
)
from data_processing.utils.mongo_setup import get_database, get_collection


collection = get_collection(collection_name="processed_frames_stage_one")


cursor = collection.find({})
cursor_data = list(cursor)

passing_opportunities = annotate_passing_opportunities(
    frames=cursor_data, distance_threshold=2, time_threshold=1, frame_rate=25 / 12
)

for frame in tqdm(cursor_data):
    frame["passing_opportunity"] = len(passing_opportunities[frame["frame"]]) > 0

    defensive_block_boundaries = get_defensive_block_boundaries(frame)
    frame["defensive_block_boundaries"] = (
        None
        if defensive_block_boundaries is None
        else defensive_block_boundaries.dict()
    )
    for _player_id, player_data in frame["players"].items():
        opposing_players = [
            alt_player
            for alt_player in frame["players"].values()
            if alt_player["team"] != player_data["team"]
        ]
        opposing_distances = [
            np.sqrt(
                (player_data["adj_x"] - opp_player["adj_x"]) ** 2
                + (player_data["adj_y"] - opp_player["adj_y"]) ** 2
            )
            for opp_player in opposing_players
        ]
        player_data["closest_opponent"] = np.min(opposing_distances)

        player_data["within_opp_block"] = (
            True
            if player_data["team"] == frame["possession_phase"]
            and player_data["adj_x"]
            > frame["defensive_block_boundaries"].get("left", 0)
            and player_data["adj_x"]
            < frame["defensive_block_boundaries"].get("right", 0)
            and player_data["adj_y"]
            < frame["defensive_block_boundaries"].get("bottom", 0)
            and player_data["adj_y"] > frame["defensive_block_boundaries"].get("top", 0)
            else False
        )

    # in_block_opportunities = search_area_for_value(
    #     frame_data=frame,
    #     defensive_block_data=defensive_block_boundaries,
    #     target_avg=0.75,
    # )
    # merged_opportunities = unary_union(
    #     [box(*option) for option in in_block_opportunities]
    # )
    # if isinstance(merged_opportunities, Polygon):
    #     merged_opportunities = MultiPolygon([merged_opportunities])
    #
    # frame["in_block_receiver_opportunities"] = len(merged_opportunities.geoms)
    # frame["in_block_receiver_opportunities_coords"] = [
    #     list(polygon.exterior.coords) for polygon in merged_opportunities.geoms
    # ]
    #
    # for player_id, player_data in frame["players"].items():
    #     player_data["passing_opportunity"] = (
    #         player_id in passing_opportunities[frame["frame"]]
    #     )
    #     player_loc = Point(player_data["adj_x"], player_data["adj_y"])
    #     player_data["in_block_receiver_opportunity"] = False
    #     for polygon in merged_opportunities.geoms:
    #         if player_loc.within(polygon):
    #             player_data["in_block_receiver_opportunity"] = True


db = get_database("metrica_tracking")
new_collection = db["processed_frames_stage_three"]
# Delete pre-existing data to upload afresh
new_collection.delete_many(filter={})

num_chunks = math.ceil(len(cursor_data) / 5000)
for i in tqdm(range(num_chunks)):
    start = i * 5000
    end = start + 5000
    chunk = cursor_data[start:end]
    new_collection.insert_many(chunk)
