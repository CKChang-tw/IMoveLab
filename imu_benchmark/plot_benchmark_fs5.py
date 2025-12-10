# name: plot_benchmark_f4_vframe.py


import pandas as pd 
import numpy as np 
import quaternion

from utils.visualization import va

from imu_benchmark.constants import constant_common, constant_mt, constant_mocap
from imu_benchmark.utils import common
from imu_benchmark.utils.mt import preprocessing_mt, calibration_mt, ik_mt

import matplotlib.pyplot as plt
from matplotlib import gridspec, animation
from matplotlib.animation import FuncAnimation, writers


# Selected filter (FIXED)
f_type   = 'VQF'
dim      = '9D'
f_params = common.get_filter_params(f_type)

# Selected subject
# subject = 4 # <-- change this to the subject you want to analyze
selected_task = 'static'


def get_setup_orientation(subject, selected_setup, selected_task, get_walking_flag = False):
    print()
    print('*** Sensor setup: ' + selected_setup)
    print()
    sensor_config  = {'pelvis': 'PELVIS', 
                    'foot_r': 'FOOT_R', 'shank_r': 'SHANK_R_' + selected_setup[0].upper(), 'thigh_r': 'THIGH_R_' + selected_setup[1].upper(),
                    'foot_l': 'FOOT_L', 'shank_l': 'SHANK_L_' + selected_setup[0].upper(), 'thigh_l': 'THIGH_L_' + selected_setup[1].upper()}

    # print(sensor_config)
    # breakpoint()

    print('- Find sensor-to-segment calibration')
    task_static     = 'static'
    data_static_mt  = preprocessing_mt.get_all_data_mt(subject, task_static, sensor_config)
    data_static_mt  = preprocessing_mt.match_data_mt(data_static_mt) 
    task_walking    = 'treadmill_walking' 
    data_walking_mt = preprocessing_mt.get_all_data_mt(subject, task_walking, sensor_config)
    task_jumping    = 'cmj' 
    data_jumping_mt = preprocessing_mt.get_all_data_mt(subject, task_jumping, sensor_config)

    if selected_setup[0].upper() == 'F':
        walking_period = calibration_mt.get_walking_4_calib(data_walking_mt['shank_r']['Gyr_Y'].to_numpy())
    else:
        walking_period = calibration_mt.get_walking_4_calib(data_walking_mt['shank_r']['Gyr_Z'].to_numpy())

    jumping_period = [0, data_jumping_mt['pelvis']['Gyr_Y'].shape[0]]

    seg2sens = calibration_mt.sensor_to_segment_mt(data_static_mt, data_walking_mt, walking_period, data_jumping_mt, jumping_period, selected_setup)

    data_main_mt = preprocessing_mt.get_all_data_mt(subject, selected_task, sensor_config)
    data_main_mt = preprocessing_mt.match_data_mt(data_main_mt)

    print('- Estimate joint angles')
    orientation_mt, _ = ik_mt.get_imu_orientation_mt(data_main_mt, f_type = f_type, fs = constant_mt.MT_SAMPLING_RATE, dim = dim.upper(), params = f_params, get_time = True)

    if get_walking_flag:
        return seg2sens, orientation_mt, data_walking_mt, walking_period
    else:
        return seg2sens, orientation_mt



# # --- Get static orientations of all subjects --- #
# # (Turn this off after the first run)
# subject_list = common.get_subject_list(None)

# for subject in subject_list:
#     print()
#     print('Subject: ' + str(subject))
#     print()

#     seg2sens_hh, orientation_hh = get_setup_orientation(subject, 'hh', selected_task)
#     seg2sens_ll, orientation_ll = get_setup_orientation(subject, 'll', selected_task)

#     filename_seg2sens_hh    = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_seg2sens_hh.pkl'
#     filename_seg2sens_ll    = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_seg2sens_ll.pkl'
#     filename_orientation_hh = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_orientation_hh.pkl'
#     filename_orientation_ll = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_orientation_ll.pkl'

#     with open(filename_seg2sens_hh, 'wb') as f:
#         pd.to_pickle(seg2sens_hh, f)
#     with open(filename_seg2sens_ll, 'wb') as f:
#         pd.to_pickle(seg2sens_ll, f)
#     with open(filename_orientation_hh, 'wb') as f:
#         pd.to_pickle(orientation_hh, f)
#     with open(filename_orientation_ll, 'wb') as f:
#         pd.to_pickle(orientation_ll, f)

#     print('- done!')






# seg2sens_hh, orientation_hh, data_walking_mt_hh, walking_period_hh = get_setup_orientation('hh', selected_task, get_walking_flag = True)
# seg2sens_ll, orientation_ll, data_walking_mt_ll, walking_period_ll = get_setup_orientation('ll', selected_task, get_walking_flag = True)



# --- Plot the static orientations of a specific subject --- #
subject = 4
# subject = 7

filename_seg2sens_hh    = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_seg2sens_hh.pkl'
filename_seg2sens_ll    = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_seg2sens_ll.pkl'
filename_orientation_hh = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_orientation_hh.pkl'
filename_orientation_ll = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_orientation_ll.pkl'

with open(filename_seg2sens_hh, 'rb') as f:
    seg2sens_hh = pd.read_pickle(f)
with open(filename_seg2sens_ll, 'rb') as f:
    seg2sens_ll = pd.read_pickle(f)
with open(filename_orientation_hh, 'rb') as f:
    orientation_hh = pd.read_pickle(f)
with open(filename_orientation_ll, 'rb') as f:
    orientation_ll = pd.read_pickle(f)


fig = plt.figure(figsize=(8, 8))
ax  = fig.add_subplot(111, projection='3d')

origin = np.array([[0], [0], [0]])
# x_axis = np.array([[1], [0], [0]])
# y_axis = np.array([[0], [1], [0]])
# z_axis = np.array([[0], [0], [1]])

x_axis = np.array([[.85], [0], [0]])
y_axis = np.array([[0], [.85], [0]])
z_axis = np.array([[0], [0], [.85]])

# # *** Before calibration
# x_pelvis, y_pelvis, z_pelvis = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['pelvis'].mean(axis = 0)), x_axis, y_axis, z_axis)

# x_thigh_r_h, y_thigh_r_h, z_thigh_r_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['thigh_r'].mean(axis = 0)), x_axis, y_axis, z_axis)
# x_thigh_l_h, y_thigh_l_h, z_thigh_l_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['thigh_l'].mean(axis = 0)), x_axis, y_axis, z_axis)
# x_shank_r_h, y_shank_r_h, z_shank_r_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['shank_r'].mean(axis = 0)), x_axis, y_axis, z_axis)
# x_shank_l_h, y_shank_l_h, z_shank_l_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['shank_l'].mean(axis = 0)), x_axis, y_axis, z_axis)

# x_thigh_r_l, y_thigh_r_l, z_thigh_r_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['thigh_r'].mean(axis = 0)), x_axis, y_axis, z_axis)
# x_thigh_l_l, y_thigh_l_l, z_thigh_l_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['thigh_l'].mean(axis = 0)), x_axis, y_axis, z_axis)
# x_shank_r_l, y_shank_r_l, z_shank_r_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['shank_r'].mean(axis = 0)), x_axis, y_axis, z_axis)
# x_shank_l_l, y_shank_l_l, z_shank_l_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['shank_l'].mean(axis = 0)), x_axis, y_axis, z_axis)

# x_foot_r, y_foot_r, z_foot_r = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['foot_r'].mean(axis = 0)), x_axis, y_axis, z_axis)
# x_foot_l, y_foot_l, z_foot_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['foot_l'].mean(axis = 0)), x_axis, y_axis, z_axis)


# *** After calibration
# x_pelvis, y_pelvis, z_pelvis = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['pelvis'].mean(axis = 0)) @ seg2sens_hh['pelvis'].T, x_axis, y_axis, z_axis)

x_thigh_r_h, y_thigh_r_h, z_thigh_r_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['thigh_r'].mean(axis = 0)) @ seg2sens_hh['thigh_r'].T, x_axis, y_axis, z_axis)
# x_thigh_l_h, y_thigh_l_h, z_thigh_l_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['thigh_l'].mean(axis = 0)) @ seg2sens_hh['thigh_l'].T, x_axis, y_axis, z_axis)
x_shank_r_h, y_shank_r_h, z_shank_r_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['shank_r'].mean(axis = 0)) @ seg2sens_hh['shank_r'].T, x_axis, y_axis, z_axis)
# x_shank_l_h, y_shank_l_h, z_shank_l_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['shank_l'].mean(axis = 0)) @ seg2sens_hh['shank_l'].T, x_axis, y_axis, z_axis)

x_thigh_r_l, y_thigh_r_l, z_thigh_r_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['thigh_r'].mean(axis = 0)) @ seg2sens_ll['thigh_r'].T, x_axis, y_axis, z_axis)
# x_thigh_l_l, y_thigh_l_l, z_thigh_l_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['thigh_l'].mean(axis = 0)) @ seg2sens_ll['thigh_l'].T, x_axis, y_axis, z_axis)
x_shank_r_l, y_shank_r_l, z_shank_r_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['shank_r'].mean(axis = 0)) @ seg2sens_ll['shank_r'].T, x_axis, y_axis, z_axis)
# x_shank_l_l, y_shank_l_l, z_shank_l_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['shank_l'].mean(axis = 0)) @ seg2sens_ll['shank_l'].T, x_axis, y_axis, z_axis)

# x_foot_r, y_foot_r, z_foot_r = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['foot_r'].mean(axis = 0)) @ seg2sens_hh['foot_r'].T, x_axis, y_axis, z_axis)
# x_foot_l, y_foot_l, z_foot_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['foot_l'].mean(axis = 0)) @ seg2sens_hh['foot_l'].T, x_axis, y_axis, z_axis)


# va.add_frame_3D(ax, origin, x_pelvis, y_pelvis, z_pelvis, offset = [0, 0, 6])

va.add_frame_3D(ax, origin, x_thigh_r_h, y_thigh_r_h, z_thigh_r_h, offset = [0, 1, 5])
# ax.scatter3D(0, 1, 5, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 5.03, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 4.97, c = 'orange', s = 50, marker = 's') # origin of right thigh
va.add_frame_3D(ax, origin, x_thigh_r_l, y_thigh_r_l, z_thigh_r_l, offset = [0, 1, 4])
# ax.scatter3D(0, 1, 4, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 4.03, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 3.97, c = 'orange', s = 50, marker = 's') # origin of right thigh

va.add_frame_3D(ax, origin, x_shank_r_h, y_shank_r_h, z_shank_r_h, offset = [0.25, 1, 2.5])
# ax.scatter3D(0.25, 1, 2.5, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 2.53, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 2.47, c = 'orange', s = 50, marker = 's') # origin of right shank
va.add_frame_3D(ax, origin, x_shank_r_l, y_shank_r_l, z_shank_r_l, offset = [0.25, 1, 1.5])
# ax.scatter3D(0.25, 1, 1.5, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 1.53, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 1.47, c = 'orange', s = 50, marker = 's') # origin of right shank

# va.add_frame_3D(ax, origin, x_thigh_l_h, y_thigh_l_h, z_thigh_l_h, offset = [0, -1, 5])
# va.add_frame_3D(ax, origin, x_thigh_l_l, y_thigh_l_l, z_thigh_l_l, offset = [0, -1, 4])

# va.add_frame_3D(ax, origin, x_shank_l_h, y_shank_l_h, z_shank_l_h, offset = [0, -1, 2.5])
# va.add_frame_3D(ax, origin, x_shank_l_l, y_shank_l_l, z_shank_l_l, offset = [0, -1, 1.5])

# va.add_frame_3D(ax, origin, x_foot_r, y_foot_r, z_foot_r, offset = [0, 1, 0])
# va.add_frame_3D(ax, origin, x_foot_l, y_foot_l, z_foot_l, offset = [0, -1, 0])


# ax.scatter(data_walking_mt_hh['shank_r']['Gyr_X'].to_numpy()[walking_period_hh[0]:walking_period_hh[1]]/6, 1 + data_walking_mt_hh['shank_r']['Gyr_Y'].to_numpy()[walking_period_hh[0]:walking_period_hh[1]]/6, 2.5 + data_walking_mt_hh['shank_r']['Gyr_Z'].to_numpy()[walking_period_hh[0]:walking_period_hh[1]]/6, c = 'r', s = 1)


# ax.grid(False)
ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.15))
ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.15))
ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.15))

ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([0, 7])
ax.set_aspect('equal', adjustable = 'box')

# set grid color
ax.xaxis._axinfo['grid'].update(color = 'lightgray', linestyle = ':', linewidth = 0.5, alpha = 0.8)
ax.yaxis._axinfo['grid'].update(color = 'lightgray', linestyle = ':', linewidth = 0.5, alpha = 0.8)
ax.zaxis._axinfo['grid'].update(color = 'lightgray', linestyle = ':', linewidth = 0.5, alpha = 0.8)

# change elevation and azimuth
# # ax.view_init(elev=25, azim=160) # for both legs
ax.view_init(elev=10, azim=100) # for right leg only

# ax.view_init(elev=90, azim=180)

ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])

# fig.patch.set_alpha(0.5)
# ax.patch.set_alpha(0.5)
# fig.patch.set_facecolor([1, 1, 1, 0.5])
# ax.set_facecolor([1, 1, 1, 0.5])

plt.savefig('imu_benchmark/plot/benchmark_f4_vframe.svg', dpi=300, bbox_inches='tight', transparent=True)


plt.show()
    

# # --- Plot the static orientations of all subjects --- #
# subject_list = common.get_subject_list(None)

# seg2sens_hh_list    = []
# seg2sens_ll_list    = []
# orientation_hh_list = []
# orientation_ll_list = []

# for subject in subject_list:
#     print()
#     print('Subject: ' + str(subject))
#     print()

#     filename_seg2sens_hh    = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_seg2sens_hh.pkl'
#     filename_seg2sens_ll    = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_seg2sens_ll.pkl'
#     filename_orientation_hh = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_orientation_hh.pkl'
#     filename_orientation_ll = 'imu_benchmark/outputs/alignment_static_mt/' + str(subject) + '_orientation_ll.pkl'

#     with open(filename_seg2sens_hh, 'rb') as f:
#         seg2sens_hh = pd.read_pickle(f)
#     with open(filename_seg2sens_ll, 'rb') as f:
#         seg2sens_ll = pd.read_pickle(f)
#     with open(filename_orientation_hh, 'rb') as f:
#         orientation_hh = pd.read_pickle(f)
#     with open(filename_orientation_ll, 'rb') as f:
#         orientation_ll = pd.read_pickle(f)

#     seg2sens_hh_list.append(seg2sens_hh)
#     seg2sens_ll_list.append(seg2sens_ll)
#     orientation_hh_list.append(orientation_hh)
#     orientation_ll_list.append(orientation_ll)


# fig = plt.figure(figsize=(8, 8))
# ax  = fig.add_subplot(111, projection='3d')

# origin = np.array([[0], [0], [0]])
# x_axis = np.array([[.85], [0], [0]])
# y_axis = np.array([[0], [.85], [0]])
# z_axis = np.array([[0], [0], [.85]])

# orientation_hh_thigh_all = []
# orientation_ll_thigh_all = []
# seg2sens_hh_thigh_all    = []
# seg2sens_ll_thigh_all    = []

# for i in range(len(subject_list)):
#     orientation_hh = orientation_hh_list[i]
#     orientation_ll = orientation_ll_list[i]
#     seg2sens_hh    = seg2sens_hh_list[i]
#     seg2sens_ll    = seg2sens_ll_list[i]

#     orientation_hh_thigh_all.append(orientation_hh['thigh_r'].mean(axis = 0))
#     orientation_ll_thigh_all.append(orientation_ll['thigh_r'].mean(axis = 0))
#     seg2sens_hh_thigh_all.append(quaternion.from_rotation_matrix(seg2sens_hh['thigh_r']))
#     seg2sens_ll_thigh_all.append(quaternion.from_rotation_matrix(seg2sens_ll['thigh_r']))

#     # *** After calibration
#     x_thigh_r_h, y_thigh_r_h, z_thigh_r_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['thigh_r'].mean(axis = 0)) @ seg2sens_hh['thigh_r'].T, x_axis, y_axis, z_axis)
#     x_shank_r_h, y_shank_r_h, z_shank_r_h = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh['shank_r'].mean(axis = 0)) @ seg2sens_hh['shank_r'].T, x_axis, y_axis, z_axis)

#     x_thigh_r_l, y_thigh_r_l, z_thigh_r_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['thigh_r'].mean(axis = 0)) @ seg2sens_ll['thigh_r'].T, x_axis, y_axis, z_axis)
#     x_shank_r_l, y_shank_r_l, z_shank_r_l = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll['shank_r'].mean(axis = 0)) @ seg2sens_ll['shank_r'].T, x_axis, y_axis, z_axis)

#     va.add_frame_3D(ax, origin, x_thigh_r_h, y_thigh_r_h, z_thigh_r_h, offset = [0, 1, 5], sidekick = True, alpha = 0.8)
#     va.add_frame_3D(ax, origin, x_thigh_r_l, y_thigh_r_l, z_thigh_r_l, offset = [0, 1, 4], sidekick = True, alpha = 0.8)
#     va.add_frame_3D(ax, origin, x_shank_r_h, y_shank_r_h, z_shank_r_h, offset = [0.25, 1, 2.5], sidekick = True, alpha = 0.8)
#     va.add_frame_3D(ax, origin, x_shank_r_l, y_shank_r_l, z_shank_r_l, offset = [0.25, 1, 1.5], sidekick = True, alpha = 0.8)

# orientation_hh_thigh_all = np.array(orientation_hh_thigh_all).mean(axis = 0)
# orientation_ll_thigh_all = np.array(orientation_ll_thigh_all).mean(axis = 0)
# seg2sens_hh_thigh_all = np.array(seg2sens_hh_thigh_all).mean(axis = 0)
# seg2sens_hh_thigh_all = quaternion.as_rotation_matrix(seg2sens_hh_thigh_all)
# seg2sens_ll_thigh_all = np.array(seg2sens_ll_thigh_all).mean(axis = 0)
# seg2sens_ll_thigh_all = quaternion.as_rotation_matrix(seg2sens_ll_thigh_all)

# x_thigh_r_h_all, y_thigh_r_h_all, z_thigh_r_h_all = va.rotate_frame(quaternion.as_rotation_matrix(orientation_hh_thigh_all) @ seg2sens_hh_thigh_all.T, x_axis, y_axis, z_axis)
# x_thigh_r_l_all, y_thigh_r_l_all, z_thigh_r_l_all = va.rotate_frame(quaternion.as_rotation_matrix(orientation_ll_thigh_all) @ seg2sens_ll_thigh_all.T, x_axis, y_axis, z_axis)

# va.add_frame_3D(ax, origin, x_thigh_r_h_all, y_thigh_r_h_all, z_thigh_r_h_all, offset = [0, 1, 5])
# va.add_frame_3D(ax, origin, x_thigh_r_l_all, y_thigh_r_l_all, z_thigh_r_l_all, offset = [0, 1, 4])

# # breakpoint()



# ax.scatter3D(0, 1, 5, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 5.03, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 4.97, c = 'orange', s = 50, marker = 's') # origin of right thigh

# ax.scatter3D(0, 1, 4, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 4.03, c = 'orange', s = 50, marker = 's') # origin of right thigh
# ax.scatter3D(0, 1, 3.97, c = 'orange', s = 50, marker = 's') # origin of right thigh


# ax.scatter3D(0.25, 1, 2.5, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 2.53, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 2.47, c = 'orange', s = 50, marker = 's') # origin of right shank

# ax.scatter3D(0.25, 1, 1.5, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 1.53, c = 'orange', s = 50, marker = 's') # origin of right shank
# ax.scatter3D(0.25, 1, 1.47, c = 'orange', s = 50, marker = 's') # origin of right shank

# # va.add_frame_3D(ax, origin, x_thigh_l_h, y_thigh_l_h, z_thigh_l_h, offset = [0, -1, 5])
# # va.add_frame_3D(ax, origin, x_thigh_l_l, y_thigh_l_l, z_thigh_l_l, offset = [0, -1, 4])

# # va.add_frame_3D(ax, origin, x_shank_l_h, y_shank_l_h, z_shank_l_h, offset = [0, -1, 2.5])
# # va.add_frame_3D(ax, origin, x_shank_l_l, y_shank_l_l, z_shank_l_l, offset = [0, -1, 1.5])

# # va.add_frame_3D(ax, origin, x_foot_r, y_foot_r, z_foot_r, offset = [0, 1, 0])
# # va.add_frame_3D(ax, origin, x_foot_l, y_foot_l, z_foot_l, offset = [0, -1, 0])


# # ax.scatter(data_walking_mt_hh['shank_r']['Gyr_X'].to_numpy()[walking_period_hh[0]:walking_period_hh[1]]/6, 1 + data_walking_mt_hh['shank_r']['Gyr_Y'].to_numpy()[walking_period_hh[0]:walking_period_hh[1]]/6, 2.5 + data_walking_mt_hh['shank_r']['Gyr_Z'].to_numpy()[walking_period_hh[0]:walking_period_hh[1]]/6, c = 'r', s = 1)


# # ax.grid(False)
# ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.15))
# ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.15))
# ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.15))

# ax.set_xlim([-2, 2])
# ax.set_ylim([-2, 2])
# ax.set_zlim([0, 7])
# ax.set_aspect('equal', adjustable = 'box')

# # set grid color
# ax.xaxis._axinfo['grid'].update(color = 'lightgray', linestyle = ':', linewidth = 0.5, alpha = 0.8)
# ax.yaxis._axinfo['grid'].update(color = 'lightgray', linestyle = ':', linewidth = 0.5, alpha = 0.8)
# ax.zaxis._axinfo['grid'].update(color = 'lightgray', linestyle = ':', linewidth = 0.5, alpha = 0.8)

# # change elevation and azimuth
# # ax.view_init(elev=25, azim=160) # for both legs
# ax.view_init(elev=10, azim=100) # for right leg only

# # ax.view_init(elev=90, azim=180)

# ax.set_xticklabels([])
# ax.set_yticklabels([])
# ax.set_zticklabels([])

# # fig.patch.set_alpha(0.5)
# # ax.patch.set_alpha(0.5)
# # fig.patch.set_facecolor([1, 1, 1, 0.5])
# # ax.set_facecolor([1, 1, 1, 0.5])

# plt.savefig('imu_benchmark/plot/benchmark_f4_vframe.svg', dpi=300, bbox_inches='tight', transparent=True)


# plt.show()



# print('Hello')













