# Import FastAPI library
import base64
import json
from typing import Optional

import numpy as np
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from tqdm import tqdm

from api.schemas import APIFrame
from api.utils import reduce_pitch_control_field, unzip_pitch_control_field
from project.utils.mongo_setup import get_database, get_collection

# Create an instance of the FastAPI class
origins = [
    "http://localhost:5173",  # Adjust this to the URL of your frontend
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Define a GET endpoint at the URL path "/frames"
# It expects two query parameters: "item_id" of type int and "name" of type str
@app.get("/matches/")
async def read_item(period_id: int):
    """
    Endpoint to fetch match information

    In reality, a dummy endpoint
    """

    db = get_database("metrica_tracking")
    collection = db["processed_frames_stage_three"]

    if period_id == 0:
        match_frame_count = collection.count_documents({})
        min_frame_idx = 0
    else:
        match_frame_count = collection.count_documents({"period": period_id})
        min_frame_idx = collection.find({"period": period_id}).sort({"frame": 1})[0][
            "frame"
        ]

    return {
        "data": [
            {
                "id": 1,
                "match_frame_count": match_frame_count,
                "min_frame_idx": min_frame_idx,
            }
        ]
    }


# TODO[***] Endpoint to get frames where in-block opps are, filter on that field, to render timeline comp
# In real life this would be off a specific match but we only have one match so it can be general
@app.get("/loose_block/")
async def read_item():
    """
    TODO[**] Docstring
    """

    collection = get_collection(collection_name="processed_frames_stage_three")

    opportunities_frames = collection.find(
        {
            "$expr": {
                "$and": [
                    {"$gt": ["$distance_from_target_goal", 50]},
                    {"$lt": ["$distance_from_target_goal", 80]},
                    {
                        "$gt": [
                            "$distance_from_target_goal",
                            "$defensive_block_boundaries.north",
                        ]
                    },
                    {"$eq": ["$passing_opportunity", True]},
                    {"$gt": ["$phase_second", 3.5]},
                ]
            }
        }
    )

    endpoint_data = [
        {
            "frame": frame["frame"],
            "period": frame["period"],
            "possession_phase": frame["possession_phase"],
            "nearest_opponent": frame["closest_opponent_to_ball"],
        }
        for frame in opportunities_frames
    ]

    return endpoint_data


@app.get("/frames/")
async def read_item(start_frame: int, end_frame: int):
    """
    This endpoint responds to GET requests at "/items/".
    It requires two parameters:
    - item_id: an integer identifying the item.
    - name: a string representing the name of the item.

    Args:
    item_id (int): The ID of the item.
    name (str): The name of the item.

    Returns:
    dict: A dictionary containing the item_id and name.
    """
    # TODO[***] Use sequential IDs on the frames and filter by those on the API call
    db = get_database("metrica_tracking")
    collection = db["processed_frames_stage_three"]

    cursor = collection.find(
        {"frame": {"$gte": start_frame * 12, "$lte": end_frame * 12}}, batch_size=100
    )

    formatted_frames = {}
    for frame in tqdm(cursor):

        schema = APIFrame(
            frame_idx=frame["frame"],
            period=frame["period"],
            match_second=frame["match_second"]
            if not np.isnan(frame["match_second"])
            else None,
            phase_second=frame["phase_second"],
            ball_position={
                "x": frame["ball_position"]["adj_x"],
                "y": frame["ball_position"]["adj_y"],
            }
            if frame["ball_position"]["x"] is not None
            else None,
            possession_phase=frame["possession_phase"],
            passing_opportunity=frame["passing_opportunity"],
            players=[
                {
                    "x": player["adj_x"],
                    "y": player["adj_y"],
                    "team": player["team"],
                    "shirt_number": player["idx"],
                    "closest_opponent": player["closest_opponent"],
                    "within_opp_block": player["within_opp_block"],
                }
                for player in frame["players"].values()
            ],
            defensive_block=frame["defensive_block_boundaries"],
            closest_opponent_to_ball=frame["closest_opponent_to_ball"],
            a_target_goal=frame["a_target_goal"],
            b_target_goal=frame["b_target_goal"],
            distance_from_target_goal=frame["distance_from_target_goal"],
            possession_target_end=frame["possession_target_end"],
            # possession_target_end=frame["a_target_goal"][0]
            # if frame["possession_phase"] == "FIFATMA"
            # else frame["b_target_goal"][0]
            # if frame["possession_phase"] == "FIFATMB"
            # else None,
            # in_block_opportunities=frame["in_block_receiver_opportunities_coords"],
            # pitch_control_field=base64.b64encode(frame["pitch_control_field"]).decode(
            #     "utf-8"
            # )
            # if frame["pitch_control_field"]
            # else None,
            in_block_opportunities=[],
            pitch_control_field=None,
        )
        formatted_frames[frame["frame"]] = schema.dict()

    return formatted_frames


# GET /items/?item_id=123&name=example
