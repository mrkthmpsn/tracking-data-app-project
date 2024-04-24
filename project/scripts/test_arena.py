"""
Test arena
"""
from project.utils.mongo_setup import get_database
from project.visualisation.utils import SoccerAnimation

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
