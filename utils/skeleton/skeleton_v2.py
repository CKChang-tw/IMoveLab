# Copyright (c) 2020-present, Assistive Robotics Lab
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import quaternion
import torch
from .rotations import quat_to_rotMat
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter


class Skeleton:
    """Skeleton for modeling and visualizing forward kinematics."""

    def __init__(self):
        """Initialize the skeleton, using segment lengths from P1.

        Have to initialize segments, parents of the segments, and map them
        together.
        """
        # segments = ["Pelvis",           # 0
        #             # "L5",               # 1
        #             # "L3",               # 2
        #             # "T12",              # 3
        #             # "T8",               # 4
        #             # "Neck",             # 5
        #             # "Head",             # 6
        #             # "RightShoulder",    # 7
        #             # "RightUpperArm",    # 8
        #             # "RightForeArm",     # 9
        #             # "RightHand",        # 10
        #             # "LeftShoulder",     # 11
        #             # "LeftUpperArm",     # 12
        #             # "LeftForeArm",      # 13
        #             # "LeftHand",         # 14
        #             "RightUpperLeg",    # 15
        #             "RightLowerLeg",    # 16
        #             "RightFoot",        # 17
        #             # "RightToe",         # 18
        #             "LeftUpperLeg",     # 19
        #             "LeftLowerLeg",     # 20
        #             "LeftFoot"]         # 21
        #             # "LeftToe"]          # 22

        segments = ['pelvis',
                    'l5',
                    'l3',
                    'pelvis_r',
                    'thigh_r',
                    'shank_r',
                    'foot_r',
                    'pelvis_l',
                    'thigh_l',
                    'shank_l',
                    'foot_l']

        # parents = [None,               # 0
        #         #    "Pelvis",           # 1
        #         #    "L5",               # 2
        #         #    "L3",               # 3
        #         #    "T12",              # 4
        #         #    "T8",               # 5
        #         #    "Neck",             # 6
        #         #    "T8",               # 7
        #         #    "RightShoulder",    # 8
        #         #    "RightUpperArm",    # 9
        #         #    "RightForeArm",     # 10
        #         #    "T8",               # 11
        #         #    "LeftShoulder",     # 12
        #         #    "LeftUpperArm",     # 13
        #         #    "LeftForeArm",      # 14
        #            "Pelvis",           # 15
        #            "RightUpperLeg",    # 16
        #            "RightLowerLeg",    # 17
        #         #    "RightFoot",        # 18
        #            "Pelvis",           # 19
        #            "LeftUpperLeg",     # 20
        #            "LeftLowerLeg"]     # 21
        #         #    "LeftFoot"]         # 22

        parents = [None,
                   'pelvis',
                   'l5',
                   'pelvis',
                   'pelvis_r',
                   'thigh_r',
                   'shank_r',
                   'pelvis',
                   'pelvis_l',
                   'thigh_l',
                   'shank_l']

        body_frame_segments = [None,                               # 0
                               [0.000000,  0.000000,  0.103107],   # 1
                               [0.000000,  0.000000,  0.095793],   # 2
                            #    [0.000000,  0.000000,  0.087564],   # 3
                            #    [0.000000,  0.000000,  0.120823],   # 4
                            #    [0.000000,  0.000000,  0.103068],   # 5
                            #    [0.000000,  0.000000,  0.208570],   # 6
                            #    [0.000000, -0.027320,  0.068158],   # 7
                            #    [0.000000, -0.141007,  0.000000],   # 8
                            #    [0.000000, -0.291763,  0.000000],   # 9
                            #    [0.000071, -0.240367,  0.000000],   # 10
                            #    [0.000000,  0.027320,  0.068158],   # 11
                            #    [0.000000,  0.141007,  0.000000],   # 12
                            #    [0.000000,  0.291763,  0.000000],   # 13
                            #    [0.000071,  0.240367,  0.000000],   # 14
                               [0.000000, -0.087677,  0.000000],   # 15
                               [-0.000055, 0.000000, -0.439960],   # 16 thigh
                               [0.000248,  0.000000, -0.445123],   # 17 shank
                               [0.192542,  0.000000, -0.087304],   # 18 foot
                               [0.000000,  0.087677,  0.000000],   # 19
                               [-0.000055, 0.000000, -0.439960],   # 20 thigh
                               [0.000248,  0.000000, -0.445123],   # 21 shank
                               [0.192542,  0.000000, -0.087304]]   # 22 foot

        # self.skeleton_tree = [[0, 1, 2, 3, 4],
        #                       [4, 7, 8, 9, 10],
        #                       [4, 11, 12, 13, 14],
        #                       [4, 5, 6],
        #                       [0, 15, 16, 17, 18],
        #                       [0, 19, 20, 21, 22]]

        self.skeleton_tree = [[0, 1, 2],
                              [0, 3, 4, 5, 6],
                              [0, 7, 8, 9, 10]]

        self.segments = segments
        self.index_of = dict(zip(segments, range(len(segments))))
        self.segment_parents = dict(zip(segments, parents))
        self.segment_positions_in_parent_frame = dict(zip(segments,
                                                          body_frame_segments))

    def forward_kinematics(self, orientations):
        """Compute positions of segment endpoints using orientation of segments.

        Args:
            orientations (torch.Tensor): orientations of segments in the
                skeleton

        Returns:
            torch.Tensor: position of segment endpoints
        """
        # xsens_indices = XSensDataIndices()

        num_samples = orientations[self.segments[0]].shape[0]

        positions = torch.zeros([len(self.segments),
                                 num_samples,
                                 3], dtype=torch.float32)

        for i, segment in enumerate(self.segments):
            parent = self.segment_parents[segment]

            if parent is None:
                continue
            else:
                # indices_map = xsens_indices({"orientation": [parent]})
                # parent_indices = indices_map["orientation"][0]

                segment_orientation = quaternion.as_float_array(orientations[segment])
                segment_orientation = torch.tensor(segment_orientation,
                                                   dtype=torch.float32)

                x_B = torch.tensor(
                    self.segment_positions_in_parent_frame[segment],
                    dtype=torch.float32)

                x_B = x_B.view(1, -1, 1).repeat(num_samples, 1, 1)

                R_GB = quat_to_rotMat(segment_orientation)
                positions[i] = (positions[self.index_of[parent]] +
                                R_GB.bmm(x_B).squeeze(2))

        return positions.permute(1, 0, 2)

    def animate_motion(self, orientations, azim, elev, title=None, fn=None, animation_save=False):
        """Animate frames of orientation data using forward kinematics.

        Args:
            orientations (torch.Tensor): orientations of the segments in the
                kinematic chain
            azim (float): azimuth of the plot point of view
            elev (float): elevation of the plot point of view
            title (str, optional): plot title. Defaults to None.

        Returns:
            animation.FuncAnimation: returns an animation that can be saved or
                viewed in a Jupyter Notebook
        """
        # if len(orientations.shape) == 1:
        #     orientations = orientations.unsqueeze(0)

        color = ['#F2D492', '#283845', '#B8B08D']

        def update_lines(num, data, lines):
            positions = data[num]

            for i, line in enumerate(lines):
                xs = list(positions[self.skeleton_tree[i], 0])
                ys = list(positions[self.skeleton_tree[i], 1])
                zs = list(positions[self.skeleton_tree[i], 2])

                line.set_data(xs, ys)
                line.set_3d_properties(zs)
                line.set_linestyle("-")
                line.set_color(color[i])
            return lines

        fig = plt.figure()
        # ax = p3.Axes3D(fig)
        ax = fig.add_subplot(111, projection="3d")

        if title is not None:
            ax.set_title(title)

        data = self.forward_kinematics(orientations)

        # breakpoint()

        # lines = [ax.plot([0], [0], [0])[0] for _ in range(6)]
        lines = [ax.plot([0], [0], [0])[0] for _ in range(3)]
        limits = [-1.0, 1.0]

        self._setup_axis(ax, limits, azim, elev)
        plt.axis('off')

        line_ani = animation.FuncAnimation(fig,
                                           update_lines,
                                           frames=range(data.shape[0]),
                                           fargs=(data, lines),
                                        #    interval=25,
                                           blit=True)
        
        if animation_save == False:
            plt.show()
        else:
            import moviepy.editor as mp
            line_ani.save(fn + '.gif', writer = PillowWriter(fps = 40))

            clip = mp.VideoFileClip(fn + ".gif")
            clip.write_videofile(fn + ".mp4")

        return line_ani

    def compare_motion(self, orientations, azim, elev,
                       fig_filename=None, titles=None):
        """Display plots of different orientation frames.

        Primarily useful for plotting skeletons for orientation outputs from
        different models.

        Args:
            orientations (torch.Tensor): orientations of the segments in the
                kinematic chain, typically of orientations from different
                models.
            azim (float): azimuth of the plot point of view
            elev (float): elevation of the plot point of view
            fig_filename (str, optional): figure filename. Defaults to None.
            titles (str, optional): plot titles. Defaults to None.

        Returns:
            matplotlib.pyplot.figure: figure that will be displayed and saved
                if fig_filename is provided.
        """
        if len(orientations.shape) == 1:
            orientations = orientations.unsqueeze(0)

        def update_lines(num, data, lines):
            positions = data[num]

            for i, line in enumerate(lines):
                xs = list(positions[self.skeleton_tree[i], 0])
                ys = list(positions[self.skeleton_tree[i], 1])
                zs = list(positions[self.skeleton_tree[i], 2])

                line.set_data(xs, ys)
                line.set_3d_properties(zs)
            return lines

        fig = plt.figure(figsize=(orientations.shape[0]*3, 3))
        data = self.forward_kinematics(orientations)

        limits = [-1.0, 1.0]
        for i in range(orientations.shape[0]):
            ax = fig.add_subplot(1,
                                 orientations.shape[0],
                                 i+1,
                                 projection="3d")

            # lines = [ax.plot([0], [0], [0])[0] for _ in range(6)]
            lines = [ax.plot([0], [0], [0])[0] for _ in range(3)]

            self._setup_axis(ax, limits, azim, elev)

            if titles is not None:
                ax.set_title(titles[i])

            update_lines(i, data, lines)

        plt.subplots_adjust(wspace=0)
        plt.show()
        if fig_filename:
            fig.savefig(fig_filename, bbox_inches="tight")
        return fig

    def _setup_axis(self, ax, limits, azim, elev):
        ax.set_xlim3d(limits)
        ax.set_ylim3d(limits)
        ax.set_zlim3d(limits)

        ax.grid(False)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        ax.view_init(azim=azim, elev=elev)
