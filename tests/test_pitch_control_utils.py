"""
TODO[**] Rewrite some hard-coded parts of this
"""

import numpy as np
from data_processing.utils.data_science.pitch_control import (
    vectorized_time_to_reach_grid,
)


def test_max_speed_over_short_distance():
    """
    Test the scenario where a player is already moving at max speed over a short distance.
    """
    current_x, current_y = 0, 0
    velocity_x, velocity_y = 8, 0  # Moving at 8 m/s along the x-axis
    reaction_time = 0.2
    acceleration = 3
    max_speed = 8
    distance = 8  # 8 meters straight ahead

    time_grid = vectorized_time_to_reach_grid(
        current_x,
        current_y,
        velocity_x,
        velocity_y,
        acceleration=acceleration,
        reaction_time=reaction_time,
        max_speed=max_speed,
    )

    # Time to cover 8 meters at 8 m/s should be 1 second plus reaction time
    expected_time = 1 + reaction_time
    calculated_time = time_grid[0, distance]  # time to reach the point 8 meters ahead

    np.testing.assert_almost_equal(
        calculated_time,
        expected_time,
        decimal=2,
        err_msg="Time to cover 8 meters at max speed is incorrect",
    )
