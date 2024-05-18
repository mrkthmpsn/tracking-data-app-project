import os

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from tqdm import tqdm

from api.schemas import APIFrame
from data_processing.utils.mongo_setup import get_database, get_collection

load_dotenv()


origins = [
    os.getenv("FE_LOCALHOST", ""),  # Localhost address
    os.getenv("FE_DOCKER", ""),
    os.getenv("FE_URL", ""),
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


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

    # TODO[***] Improve structure of API
    return {
        "data": [
            {
                "id": 1,
                "match_frame_count": match_frame_count,
                "min_frame_idx": min_frame_idx,
            }
        ]
    }


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

    # TODO[***] Improve structure of API
    return endpoint_data


@app.get("/frames/")
async def read_item(start_frame: int, end_frame: int):
    """
    This endpoint responds to GET requests at "/frames/".
    It requires two parameters:
    - start_frame: an integer identifying the item.
    - end_frame: a string representing the name of the item.
    """
    # TODO[***] Use sequential IDs on the frames and filter by those on the API call
    collection = get_collection("processed_frames_stage_three")

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

    # TODO[***] Improve structure of API
    return formatted_frames
