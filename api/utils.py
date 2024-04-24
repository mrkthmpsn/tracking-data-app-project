"""
File for utils used in the API
"""

import gzip
import io
from typing import List

import numpy as np


def unzip_pitch_control_field(zipped_pitch_control_field) -> np.array:
    """
    Unzips a zipped pitch control field instance

    :param zipped_pitch_control_field: Pitch control field compressed with gzip
    :return: 2D numpy array
    """
    if zipped_pitch_control_field is None:
        return None

    decompressed_data = gzip.decompress(zipped_pitch_control_field)
    # Reconstruct the BytesIO object
    buffer = io.BytesIO(decompressed_data)
    # Load the NumPy array
    reconstructed_pitch_control_field = np.load(buffer)

    return reconstructed_pitch_control_field


def reduce_pitch_control_field(
    raw_pitch_control_grid: np.array, new_width: int = 35, new_height: int = 34
) -> List[dict]:
    """
    Reduces the granularity of a pitch control field (i.e. 2D array).

    As the original pitch control field is 105x68 (1mx1m sections for a standard pitch), 35x34 is a
    reasonable reduction (3mx2m sections for a standard pitch).

    :param raw_pitch_control_grid: 2D array of pitch control values
    :param new_width: int
    :param new_height: int
    :return: list of pitch control value objects in format TODO[**] - define format
    """
    if raw_pitch_control_grid is None:
        return None
    # Assuming data is a NumPy array of shape (68, 105)
    old_height, old_width = raw_pitch_control_grid.shape
    grouped_data = []

    # Factor by which the original dimensions are reduced
    width_factor = old_width // new_width
    height_factor = old_height // new_height

    for i in range(new_height):
        for j in range(new_width):
            # Calculate the start and end indices of the original grid
            start_i = i * height_factor
            end_i = start_i + height_factor
            start_j = j * width_factor
            end_j = start_j + width_factor

            # Extract the subgrid and calculate the mean
            subgrid = raw_pitch_control_grid[start_i:end_i, start_j:end_j]
            grouped_data.append(
                {
                    "x": j * 3,
                    "y": i * 2,
                    "i": j,
                    "j": i,
                    "height": 2,
                    "width": 3,
                    "value": float(np.mean(subgrid)),
                }
            )

    return grouped_data
