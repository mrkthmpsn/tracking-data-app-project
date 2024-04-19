# Import FastAPI library
import base64
import json

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from tqdm import tqdm

from api.schemas import APIFrame
from api.utils import reduce_pitch_control_field, unzip_pitch_control_field
from project.utils.mongo_setup import get_database

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
async def read_item():
    """
    Endpoint to fetch match information

    In reality, a dummy endpoint
    """

    db = get_database("metrica_tracking")
    collection = db["processed_frames_stage_three"]

    match_frame_count = collection.count_documents({})

    return {"data": [{"id": 1, "match_frame_count": match_frame_count}]}


# TODO[***] Endpoint to get frames where in-block opps are, filter on that field, to render timeline comp
# In real life this would be off a specific match but we only have one match so it can be general
@app.get("/progression_opportunities/")
async def read_item():
    """
    TODO[**] Docstring
    """
    db = get_database("metrica_tracking")
    collection = db["processed_frames_stage_three"]

    opportunities_frames = collection.find({"in_ball_opportunities": {"$gt": 0}})

    # Will want to format this in some way, but how


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
    # cursor_data = list(cursor)

    # request_frames = cursor_data[start_frame:end_frame]

    formatted_frames = {}
    for frame in tqdm(cursor):
        # new_pitch_control_field = reduce_pitch_control_field(
        #     unzip_pitch_control_field(frame["pitch_control_field"])
        # )

        schema = APIFrame(
            frame_idx=frame["frame"],
            ball_position={
                "x": frame["ball_position"]["adj_x"],
                "y": frame["ball_position"]["adj_y"],
            }
            if frame["ball_position"]["x"] is not None
            else None,
            possession_phase=frame["possession_phase"],
            players=[
                {
                    "x": player["adj_x"],
                    "y": player["adj_y"],
                    "team": player["team"],
                    "shirt_number": player["idx"],
                }
                for player in frame["players"].values()
            ],
            defensive_block=frame["defensive_block_boundaries"],
            in_block_opportunities=frame["in_block_receiver_opportunities_coords"],
            pitch_control_field=base64.b64encode(frame["pitch_control_field"]).decode(
                "utf-8"
            )
            if frame["pitch_control_field"]
            else None,
        )
        formatted_frames[frame["frame"]] = schema.dict()

    return formatted_frames


# GET /items/?item_id=123&name=example
