"""

"""

import numpy as np
import pandas as pd
from data_processing.utils.tracking_processing import (
    convert_to_meters,
    smooth_coordinates,
    calculate_speed,
)
from data_processing.utils.constants import PITCH_WIDTH_M, PITCH_LENGTH_M


# Test for convert_to_meters function
def test_convert_to_meters():
    x, y = 0.5, 0.5  # Center of the pitch
    adj_x, adj_y = convert_to_meters(
        x, y, pitch_length_m=PITCH_LENGTH_M, pitch_width_m=PITCH_WIDTH_M
    )
    assert (
        adj_x == PITCH_LENGTH_M / 2 and adj_y == PITCH_WIDTH_M / 2
    ), "Center point coordinates are incorrect"

    # Testing a corner point
    x, y = 1, 1  # Top right corner
    adj_x, adj_y = convert_to_meters(x, y)
    assert (
        adj_x == PITCH_LENGTH_M and adj_y == PITCH_WIDTH_M
    ), "Top right corner coordinates are incorrect"


# Test for smooth_coordinates function
def test_smooth_coordinates():
    data = pd.DataFrame({"x": np.linspace(0, 1, 10), "y": np.linspace(0, 1, 10)})
    smoothed_data = smooth_coordinates(data)

    # Check if the smoothed data is different from the original
    assert not np.array_equal(
        data["x"], smoothed_data["x"]
    ), "Smoothing not applied to x coordinates"
    assert not np.array_equal(
        data["y"], smoothed_data["y"]
    ), "Smoothing not applied to y coordinates"


# Test for calculate_speed function
def test_calculate_speed():
    data = pd.DataFrame({"adj_x": [0, 5, 10], "adj_y": [0, 5, 10]})
    calculated_data = calculate_speed(data, sample_frame_rate=int(25 / 5))

    # Assuming TIME_INTERVAL = 1 for simplicity
    expected_speeds = [np.nan, np.sqrt(2), np.sqrt(2)]
    np.testing.assert_array_almost_equal(
        calculated_data["speed_m_s"],
        expected_speeds,
        err_msg="Speed calculation is incorrect",
    )
