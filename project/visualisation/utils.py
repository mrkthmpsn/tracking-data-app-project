"""
Visualisation utils
"""
import gzip
import io
from functools import partial

import numpy as np
from matplotlib import animation, pyplot as plt, patches
from mplsoccer import Pitch

from project.utils.data_science.metrics import (
    search_area_for_value,
    get_defensive_block_boundaries,
)


def plot_frame(frame_data, defensive_block=None, in_block_opportunities=None):
    """

    :param frame_data:
    :return:
    """

    decompressed_data = gzip.decompress(frame_data["pitch_control_field"])

    # Reconstruct the BytesIO object
    buffer = io.BytesIO(decompressed_data)

    # Load the NumPy array
    reconstructed_pitch_control_field = np.load(buffer)

    pitch = Pitch(
        pitch_type="custom",
        # orientation='horizontal',
        pitch_color="grass",
        line_color="white",
        pitch_width=68,
        pitch_length=105
        # figsize=(10, 7)
    )
    fig, ax = pitch.draw()

    # Create the heatmap
    ax.imshow(
        reconstructed_pitch_control_field,
        extent=(0, 105, 68, 0),
        aspect="auto",
        cmap="bwr",
        vmin=0,
        vmax=1,
    )

    if defensive_block:
        defensive_block_patch = patches.Rectangle(
            (defensive_block.left, defensive_block.bottom),
            width=defensive_block.right - defensive_block.left,
            height=defensive_block.top - defensive_block.bottom,
            alpha=0.3,
            color="black",
        )
        ax.add_patch(defensive_block_patch)

    if in_block_opportunities:
        for opportunity in in_block_opportunities:
            ax.add_patch(
                patches.Rectangle(
                    (opportunity[0], opportunity[1]),
                    width=opportunity[2] - opportunity[0],
                    height=opportunity[3] - opportunity[1],
                    alpha=0.7,
                    color="yellow",
                )
            )

    # Plot each player's position and velocity vector
    for player_id, player_data in list(frame_data["players"].items()):
        ax.plot(
            player_data["adj_x"],
            player_data["adj_y"],
            "o",
            markerfacecolor="purple" if player_data["team"] == "TEAM_A" else "pink",
            color="yellow" if player_data["passing_opportunity"] else "black",
            markersize=10,
        )  # Player's position
        ax.text(player_data["adj_x"], player_data["adj_y"], player_id)
        ax.arrow(
            player_data["adj_x"],
            player_data["adj_y"],
            player_data["delta_x"] * 5,
            player_data["delta_y"] * 5,
            head_width=1,
            head_length=1,
            fc="yellow",
            ec="yellow",
        )  # Velocity vector
    ax.plot(
        frame_data["ball_position"]["adj_x"],
        frame_data["ball_position"]["adj_y"],
        "o",
        markerfacecolor="white",
        color="black",
        markersize=7,
    )

    return fig


def init_plot(num_players: int = 22):
    pitch = Pitch(
        pitch_type="custom",
        pitch_color="grass",
        line_color="white",
        pitch_width=68,
        pitch_length=105,
    )
    fig, ax = pitch.draw()
    heatmap = ax.imshow(
        np.zeros((68, 105)),
        extent=(0, 105, 68, 0),
        aspect="auto",
        cmap="bwr",
        vmin=0,
        vmax=1,
    )

    # Initialize a placeholder for the defensive block patch
    defensive_block_patch = patches.Rectangle((0, 0), 0, 0, alpha=0.3, color="black")
    ax.add_patch(defensive_block_patch)

    # Initialize placeholders for in-block opportunities
    opportunity_patches = []
    for _ in range(
        num_players * 2
    ):  # 'max_opportunities' should be the maximum number you expect
        patch = patches.Rectangle((0, 0), 0, 0, alpha=0.7, color="yellow")
        ax.add_patch(patch)
        opportunity_patches.append(patch)

    (players,) = ax.plot(
        [],
        [],
        "o",
        markerfacecolor="purple",
        color="yellow",
        markersize=10,
    )
    (ball,) = ax.plot([], [], "o", markerfacecolor="white", color="black", markersize=7)
    velocity_arrows = []
    for _ in range(num_players):
        arrow = ax.arrow(
            0, 0, 0, 0, head_width=1, head_length=1, fc="yellow", ec="yellow"
        )
        velocity_arrows.append(arrow)

    return (
        fig,
        ax,
        heatmap,
        players,
        ball,
        velocity_arrows,
        defensive_block_patch,
        opportunity_patches,
    )


# def update(frame_data, ax, players, ball, heatmap, velocity_arrows, defensive_block_patch, opportunity_patches):
def update(frame_data, ax):

    # TODO[**] Deal with frames with no pitch control
    # Update the heatmap
    decompressed_data = gzip.decompress(frame_data["pitch_control_field"])
    # Reconstruct the BytesIO object
    buffer = io.BytesIO(decompressed_data)
    # Load the NumPy array
    reconstructed_pitch_control_field = np.load(buffer)

    defensive_block_data = get_defensive_block_boundaries(frame_data)
    opportunities_data = search_area_for_value(
        frame_data=frame_data,
        defensive_block_data=defensive_block_data,
        target_avg=0.75,
    )

    global heatmap
    heatmap.set_data(reconstructed_pitch_control_field)

    # global defensive_block_patch, opportunity_patches

    # Update the defensive block patch
    global defensive_block_patch
    if defensive_block_data:
        defensive_block_patch.set_bounds(
            defensive_block_data.left,
            defensive_block_data.bottom,
            defensive_block_data.right - defensive_block_data.left,
            defensive_block_data.top - defensive_block_data.bottom,
        )
    else:
        defensive_block_patch.set_width(0)  # Hide the patch if no defensive block

    # Update the in-block opportunity patches
    global opportunity_patches
    for patch, opportunity in zip(opportunity_patches, opportunities_data):
        patch.set_bounds(
            opportunity[0],
            opportunity[1],
            opportunity[2] - opportunity[0],
            opportunity[3] - opportunity[1],
        )

    # Hide any unused patches
    for patch in opportunity_patches[len(opportunities_data) :]:
        patch.set_width(0)

    # Update players' positions
    # player_positions = [(data["adj_x"], data["adj_y"]) for data in frame_data["players"].values()]
    # players.set_data(*zip(*player_positions))
    # Update players: remove existing markers and create new ones with updated colors

    global players  # Use global or nonlocal depending on where 'players' is defined
    players.remove()  # Remove the existing player markers
    player_x_positions = [
        player_data["adj_x"] for player_data in frame_data["players"].values()
    ]
    player_y_positions = [
        player_data["adj_y"] for player_data in frame_data["players"].values()
    ]
    player_colors = [
        "purple" if player_data["team"] == "TEAM_A" else "pink"
        for player_data in frame_data["players"].values()
    ]
    player_edgecolors = [
        "yellow" if player_data["passing_opportunity"] else "black"
        for player_data in frame_data["players"].values()
    ]
    players = ax.scatter(
        player_x_positions,
        player_y_positions,
        c=player_colors,
        edgecolors=player_edgecolors,
        s=100,
    )  # Create new markers with updated colors

    # Update the ball's position
    global ball
    ball.set_data(
        frame_data["ball_position"]["adj_x"], frame_data["ball_position"]["adj_y"]
    )

    # Update velocity arrows
    # Remove existing arrows
    global velocity_arrows
    for arrow in velocity_arrows:
        arrow.remove()
    velocity_arrows.clear()

    # Create new arrows
    for player_data in frame_data["players"].values():
        arrow = ax.arrow(
            player_data["adj_x"],
            player_data["adj_y"],
            player_data["delta_x"] * 10,
            player_data["delta_y"] * 10,
            head_width=1,
            head_length=1,
            fc="yellow",
            ec="yellow",
        )
        velocity_arrows.append(arrow)

    return (
        heatmap,
        players,
        ball,
        *velocity_arrows,
        defensive_block_patch,
        *opportunity_patches,
    )


def plot_animation(frame_list):
    # Initialize the plot
    (
        fig,
        ax,
        heatmap,
        players,
        ball,
        velocity_arrows,
        defensive_block_patch,
        opportunity_patches,
    ) = init_plot()

    partial_update = partial(update, ax=ax)

    # Create animation
    anim = animation.FuncAnimation(
        fig, partial_update, frames=frame_list, blit=True, interval=1000 / (25 / 12)
    )

    plt.show()

    # anim.save('my_animation.mp4', fps=frame_rate, extra_args=['-vcodec', 'libx264'])


# -------
# start_idx = 1000
# end_idx = 1200
# frame_list = [cursor_data[idx] for idx in list(range(start_idx, end_idx+1))]
# # Number of extra frames to create the pause
# pause_frames = 5
#
# # Repeat the last frame data for the duration of the pause
# last_frame_data = frame_list[-1]
# pause_frame_data = [last_frame_data] * pause_frames
#
# # Extend the frames list with the extra pause frames
# frame_list.extend(pause_frame_data)


class SoccerAnimation:
    def __init__(self, num_players=22):
        self.pitch = Pitch(
            pitch_type="custom",
            pitch_color="grass",
            line_color="white",
            pitch_width=68,
            pitch_length=105,
            line_zorder=3,
        )
        self.fig, self.ax = self.pitch.draw()
        self.heatmap = self.ax.imshow(
            np.zeros((68, 105)),
            extent=(0, 105, 68, 0),
            aspect="auto",
            cmap="bwr",
            vmin=0,
            vmax=1,
        )
        self.defensive_block_patch = patches.Rectangle(
            (0, 0), 0, 0, alpha=0.3, color="black"
        )
        self.ax.add_patch(self.defensive_block_patch)
        self.opportunity_patches = [
            self.ax.add_patch(
                patches.Polygon(
                    [(0, 0), (0, 0)], closed=True, alpha=0.7, color="yellow"
                )
            )
            for _ in range(num_players * 2)
        ]
        # self.players = [
        #     self.ax.plot(
        #         [], [], "o", markerfacecolor="purple", color="yellow", markersize=10
        #     )[0]
        #     for _ in range(num_players)
        # ]
        self.players = None
        (self.ball,) = self.ax.plot(
            [], [], "o", markerfacecolor="white", color="black", markersize=7, zorder=4
        )
        self.velocity_arrows = [
            self.ax.arrow(
                0, 0, 0, 0, head_width=1, head_length=1, fc="yellow", ec="yellow"
            )
            for _ in range(num_players)
        ]

    def update(self, frame_data):
        # Update heatmap
        if frame_data["pitch_control_field"] is None:
            self.heatmap.set_visible(False)
        else:
            decompressed_data = gzip.decompress(frame_data["pitch_control_field"])
            buffer = io.BytesIO(decompressed_data)
            reconstructed_pitch_control_field = np.load(buffer)
            self.heatmap.set_data(reconstructed_pitch_control_field)
            self.heatmap.set_visible(True)

        # defensive_block_data = get_defensive_block_boundaries(frame_data)
        # opportunities_data = search_area_for_value(
        #     frame_data=frame_data,
        #     defensive_block_data=defensive_block_data,
        #     target_avg=0.75,
        # )

        # Update defensive block patch
        if frame_data["defensive_block_boundaries"]:
            self.defensive_block_patch.set_bounds(
                frame_data["defensive_block_boundaries"]["left"],
                frame_data["defensive_block_boundaries"]["bottom"],
                frame_data["defensive_block_boundaries"]["right"]
                - frame_data["defensive_block_boundaries"]["left"],
                frame_data["defensive_block_boundaries"]["top"]
                - frame_data["defensive_block_boundaries"]["bottom"],
            )
            self.defensive_block_patch.set_color(
                "red" if frame_data["possession_phase"] == "FIFATMA" else "blue"
            )
        else:
            self.defensive_block_patch.set_width(
                0
            )  # Hide the patch if no defensive block

        # Update opportunity patches
        for patch, opportunity in zip(
            self.opportunity_patches,
            frame_data["in_block_receiver_opportunities_coords"],
        ):
            patch.set_xy(opportunity)
            patch.set_visible(True)

        # Hide unused patches
        for patch in self.opportunity_patches[
            len(frame_data["in_block_receiver_opportunities_coords"]) :
        ]:
            patch.set_visible(False)

        # Update player markers
        if self.players is None:
            self.players = [
                self.ax.plot(
                    player_data["adj_x"],
                    player_data["adj_y"],
                    "o",
                    markerfacecolor="purple"
                    if player_data["team"] == "TEAM_A"
                    else "pink",
                    markeredgecolor="yellow"
                    if player_data["passing_opportunity"]
                    else "black",
                    markersize=10,
                    zorder=3,
                )[0]
                for player_data in frame_data["players"].values()
            ]  # Create new markers with updated colors
        else:
            for player, player_data in zip(
                self.players, frame_data["players"].values()
            ):
                player.set_data(player_data["adj_x"], player_data["adj_y"])
                player.set_markerfacecolor(
                    "purple" if player_data["team"] == "TEAM_A" else "pink"
                )
                player.set_markeredgecolor(
                    "yellow" if player_data["passing_opportunity"] else "black"
                )

            # Update ball position
        self.ball.set_data(
            frame_data["ball_position"]["adj_x"], frame_data["ball_position"]["adj_y"]
        )

        # Update velocity arrows
        for arrow in self.velocity_arrows:
            arrow.remove()
        self.velocity_arrows = []
        for player_data in frame_data["players"].values():
            arrow = self.ax.arrow(
                player_data["adj_x"],
                player_data["adj_y"],
                player_data["delta_x"] * 5,
                player_data["delta_y"] * 5,
                head_width=1,
                head_length=1,
                fc="yellow",
                ec="yellow",
            )
            self.velocity_arrows.append(arrow)

        return [
            self.heatmap,
            *self.players,
            self.ball,
            *self.velocity_arrows,
            self.defensive_block_patch,
            *self.opportunity_patches,
        ]

    def plot_animation(self, frame_list, save_animation: bool = False):
        anim = animation.FuncAnimation(
            self.fig,
            self.update,
            frames=frame_list,
            blit=True,
            interval=1000 / (25 / 12),
        )
        plt.show()
        # Optionally, save the animation
        if save_animation:
            anim.save(
                "./test_animation.mp4",
                fps=int(25 / 12),
                # extra_args=['-vcodec', 'libx264']
            )
