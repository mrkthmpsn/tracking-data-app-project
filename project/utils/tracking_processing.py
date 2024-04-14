"""
Basic processing utils
"""
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from project.utils.constants import PITCH_WIDTH_M, PITCH_LENGTH_M


# TODO[*]: Possibly refactor this util, not sure it 's the right concept - but unimportant
def convert_to_meters(
    x: float,
    y: float,
    pitch_length_m: float = PITCH_LENGTH_M,
    pitch_width_m: float = PITCH_WIDTH_M,
) -> pd.Series:
    """Convert coordinates from 0-1 range to meters."""
    adj_x = (x) * pitch_length_m
    adj_y = (y) * pitch_width_m
    return pd.Series([adj_x, adj_y])


def smooth_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Apply smoothing to the coordinates."""
    smoothed_df = df.copy()
    smoothed_df["x"] = savgol_filter(smoothed_df["x"], 5, 2, mode="nearest")
    smoothed_df["y"] = savgol_filter(smoothed_df["y"], 5, 2, mode="nearest")

    return smoothed_df


def calculate_speed(df: pd.DataFrame, sample_frame_rate: float) -> pd.DataFrame:
    """Calculate speed in meters per second."""
    # Calculate differences between consecutive frames
    df["delta_x"] = df["adj_x"].diff() / sample_frame_rate
    df["delta_y"] = df["adj_y"].diff() / sample_frame_rate

    # Actual speed calculation (magnitude of velocity vector)
    df["speed_m_s"] = np.sqrt(df["delta_x"] ** 2 + df["delta_y"] ** 2)

    return df
