"""
Test arena
"""
from data_processing.utils.mongo_setup import get_database, get_collection
from data_processing.visualisation.utils import SoccerAnimation

collection = get_collection("processed_frames_stage_three")
cursor = collection.find({})
cursor_data = list(cursor)

clip_frames = cursor_data[5485:5590]

soccer_anim = SoccerAnimation(num_players=22)
soccer_anim.plot_animation(clip_frames)
