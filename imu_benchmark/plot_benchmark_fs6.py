# name: plot_benchmark_fs3_mag_correlation.py

import pandas as pd 
import numpy as np 
import quaternion
import pickle
import time
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

from imu_benchmark.constants import constant_common, constant_mt, constant_mocap
from imu_benchmark.utils import common
from imu_benchmark.utils.eval import eval_utils, eval_segment
from imu_benchmark.utils.mt import preprocessing_mt, calibration_mt, ik_mt
from imu_benchmark.utils.mocap import preprocessing_mocap, ik_mocap

from scipy.stats import gaussian_kde


def plot_density(ax, dist, color, scale, covf, filling = True):
    density = gaussian_kde(dist, bw_method = scale)
    xs = np.linspace(np.min(dist) - 0.02, np.max(dist) + 0.02, 100)
    density.covariance_factor = lambda: covf
    density._compute_covariance()

    # ax.plot(xs, scale*density(xs), color = color, lw = 0.5, zorder = 1)
    if filling:
        ax.fill_between(xs, 0, scale*density(xs), color = color, edgecolor = 'none', alpha = 0.5, zorder = 0)


# selected_setup = 'mm'
selected_setup = 'hh'

sensor_config_ = {'pelvis_r': 'PELVIS', 'pelvis_l': 'PELVIS', 
                  'foot_r': 'FOOT_R', 'shank_r': 'SHANK_R_' + selected_setup[0].upper(), 'thigh_r': 'THIGH_R_' + selected_setup[1].upper(),
                  'foot_l': 'FOOT_L', 'shank_l': 'SHANK_L_' + selected_setup[0].upper(), 'thigh_l': 'THIGH_L_' + selected_setup[1].upper()}


task_list = common.get_task_list(None)
subject_list = common.get_subject_list(None)


mag_dist_all = {}

for sensor in sensor_config_.keys():
    if sensor == 'pelvis_l':
        pass 
    else:
        mag_dist_all[sensor] = []

        for subject in subject_list:
            # for task in task_list:
            for task in ['walking']: # focus on overground walking only
            # for task in ['step_n_hold']:
            # for task in ['walking', 'treadmill_walking', 'treadmill_running']:

                filename_mag = constant_common.OUT_MT_MAG_DIST_PATH + 'mag_dist_s' + str(subject) + '_' + task + '.pkl'
                mag_dist = eval_utils.load_data(filename_mag)

                mag_dist_all[sensor].append(mag_dist[sensor])

        mag_dist_all[sensor] = np.array(mag_dist_all[sensor])




font_size = 11
fontsize_label = 13
fontsize_stats = 10
        
# --- Correlation between magnetic disturbances and RMSD --- #
for sensor in sensor_config_.keys():
    mag_dist_all[sensor] = []

    for subject in subject_list:
        # for task in task_list:
        for task in ['walking']: # focus on overground walking only
        # for task in ['squat']: # focus on overground walking only
        # for task in ['walking', 'treadmill_walking', 'treadmill_running']:

            filename_mag = constant_common.OUT_MT_MAG_DIST_PATH + 'mag_dist_s' + str(subject) + '_' + task + '.pkl'
            mag_dist = eval_utils.load_data(filename_mag)

            mag_dist_all[sensor].append(mag_dist[sensor])

    mag_dist_all[sensor] = np.array(mag_dist_all[sensor])

f_type_xsens = 'Xsens'
f_type_vqf   = 'VQF'
dim    = '9D'
# dim = '6D' # test with 6D

# rmsd_all_xsens = {}
rmsd_all_vqf = {}
rmsd_all_vqf_os = {}

reference = 'direct'
title_alignment = '_alignment'

for joint in ['hip_flexion_r', 'hip_flexion_l', 'knee_flexion_r', 'knee_flexion_l', 'ankle_flexion_r', 'ankle_flexion_l']:
    # rmsd_all_xsens[joint] = []
    rmsd_all_vqf[joint] = []
    rmsd_all_vqf_os[joint] = []

    for subject in subject_list:
        # for task in task_list:
        for task in ['walking']: # focus on overground walking only
        # for task in ['squat']: # focus on overground walking only
        # for task in ['walking', 'treadmill_walking', 'treadmill_running']:

            # filename_xsens = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type_xsens.lower() + '_' + dim.upper() + '_' + task + '_' + reference + title_alignment + '_mt' + '.pkl'
            filename_vqf   = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type_vqf.lower() + '_' + dim.upper() + '_' + task + '_' + reference + title_alignment + '_mt' + '.pkl'
            filename_vqf_os = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type_vqf.lower() + '_' + dim.upper() + '_' + task + '_' + reference + title_alignment + '_os' + '.pkl'
            # rmsd_data_xsens = eval_utils.load_data(filename_xsens)
            rmsd_data_vqf = eval_utils.load_data(filename_vqf)
            rmsd_data_vqf_os = eval_utils.load_data(filename_vqf_os)

            # rmsd_all_xsens[joint].append(rmsd_data_xsens[joint])
            rmsd_all_vqf[joint].append(rmsd_data_vqf[joint])
            rmsd_all_vqf_os[joint].append(rmsd_data_vqf_os[joint])

    # rmsd_all_xsens[joint] = np.array(rmsd_all_xsens[joint])
    rmsd_all_vqf[joint] = np.array(rmsd_all_vqf[joint])
    rmsd_all_vqf_os[joint] = np.array(rmsd_all_vqf_os[joint])

# breakpoint()
    
color_mt = '#6B4E71'
color_os = '#453F78'

marker_size = 40
    
plt.rcParams.update({'font.size': font_size})
fig, ax = plt.subplots(figsize = (10, 4), gridspec_kw = {'hspace': -0.6, 'bottom': 0.15})

mag_dist_corr = []
mag_dist_corr.append((mag_dist_all['pelvis_r'] + mag_dist_all['thigh_r'])/2)
mag_dist_corr.append((mag_dist_all['thigh_r'] + mag_dist_all['shank_r'])/2)
mag_dist_corr.append((mag_dist_all['shank_r'] + mag_dist_all['foot_r'])/2)
mag_dist_corr.append((mag_dist_all['pelvis_l'] + mag_dist_all['thigh_l'])/2)
mag_dist_corr.append((mag_dist_all['thigh_l'] + mag_dist_all['shank_l'])/2)
mag_dist_corr.append((mag_dist_all['shank_l'] + mag_dist_all['foot_l'])/2)
mag_dist_corr = np.array(mag_dist_corr)
mag_dist_corr = mag_dist_corr.flatten()

rmsd_corr = []
rmsd_corr.append(rmsd_all_vqf['hip_flexion_r'])
rmsd_corr.append(rmsd_all_vqf['knee_flexion_r'])
rmsd_corr.append(rmsd_all_vqf['ankle_flexion_r'])
rmsd_corr.append(rmsd_all_vqf['hip_flexion_l'])
rmsd_corr.append(rmsd_all_vqf['knee_flexion_l'])
rmsd_corr.append(rmsd_all_vqf['ankle_flexion_l'])
rmsd_corr = np.array(rmsd_corr)
rmsd_corr = rmsd_corr.flatten()

rmsd_corr_os = []
rmsd_corr_os.append(rmsd_all_vqf_os['hip_flexion_r'])
rmsd_corr_os.append(rmsd_all_vqf_os['knee_flexion_r'])
rmsd_corr_os.append(rmsd_all_vqf_os['ankle_flexion_r'])
rmsd_corr_os.append(rmsd_all_vqf_os['hip_flexion_l'])
rmsd_corr_os.append(rmsd_all_vqf_os['knee_flexion_l'])
rmsd_corr_os.append(rmsd_all_vqf_os['ankle_flexion_l'])
rmsd_corr_os = np.array(rmsd_corr_os)
rmsd_corr_os = rmsd_corr_os.flatten()


from scipy.stats import pearsonr, spearmanr

print('--- Spearman correlation ---')
print(spearmanr(mag_dist_corr, rmsd_corr))
print(spearmanr(mag_dist_corr, rmsd_corr_os))
# print(spearmanr(mag_dist_corr, rmsd_corr_os))


# ax.scatter(mag_dist_corr, rmsd_corr, s = marker_size, color = color_mt, label = 'Direct', marker = 'o', edgecolor = 'none', alpha = 0.5)
# ax.scatter(mag_dist_corr, rmsd_corr_os, s = marker_size, color = 'none', label = 'Constrained', marker = 'o', edgecolor = color_mt, alpha = 0.8)

from scipy.optimize import curve_fit

def f(x, A, B):
    return A*x + B
u_popt, _ = curve_fit(f, mag_dist_corr, rmsd_corr)
xline = np.linspace(np.min(mag_dist_corr) - 0.02, np.max(mag_dist_corr) + 0.02, 200)
yline = f(xline, u_popt[0], u_popt[1])

u_popt_os, _ = curve_fit(f, mag_dist_corr, rmsd_corr_os)
yline_os = f(xline, u_popt_os[0], u_popt_os[1])




ax.scatter(mag_dist_corr, rmsd_corr, s = marker_size, color = 'none', label = 'Direct', marker = 'o', edgecolor = color_mt, alpha = 0.5)
# ax.plot(xline, yline, color = color_mt, lw = 4, linestyle = '--', alpha = 0.5, zorder = 2, label = 'Linear Fit (Direct)')
ax.plot(xline, yline, color = color_mt, lw = 4, linestyle = (0, (1.5, 1)), alpha = 0.5, zorder = 2, label = 'Linear Fit (Direct)')

ax.scatter(mag_dist_corr, rmsd_corr_os, s = marker_size, color = color_mt, label = 'Constrained', marker = 'o', edgecolor = 'none', alpha = 0.5)

ax.plot(xline, yline_os, color = color_mt, lw = 4, linestyle = '-', alpha = 0.8, zorder = 2, label = 'Linear Fit (Constrained)')



ax.set_xlim(0, 0.28)
ax.set_ylim(0, 10)
ax.set_xticks([0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28])

ax.set_xlabel('Magnetic Field Norm SD (a.u.)', fontsize = fontsize_label)
ax.set_ylabel(r'RMSD $(^o)$', fontsize = fontsize_label)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_position(('outward', 8))
ax.spines['bottom'].set_position(('outward', 5))

ax.legend(loc = 'upper left', fontsize = fontsize_stats, frameon = False, markerscale = 0.8, handletextpad = 0.8, labelspacing = 0.4, borderpad = 0.2, ncols = 2, columnspacing = 15)

ax.annotate(r"(Spearman's $\rho$ = " + str(round(spearmanr(mag_dist_corr, rmsd_corr)[0], 2)) + ' , p <0.001)', xy = (0.13, 0.93), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray')
ax.annotate(r"(Spearman's $\rho$ = " + str(round(spearmanr(mag_dist_corr, rmsd_corr_os)[0], 2)) + ' , p <0.001)', xy = (0.66, 0.93), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray')


# ax.annotate(r'R$_{Direct}$ = ' + str(round(spearmanr(mag_dist_corr, rmsd_corr)[0], 2)) + ' (p <0.001 *)', xy = (0.05, 0.9), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray')
# ax.annotate(r'R$_{Constrained}$ = ' + str(round(spearmanr(mag_dist_corr, rmsd_corr_os)[0], 2)) + ' (p <0.001 *)', xy = (0.05, 0.8), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray')

plt.savefig('imu_benchmark/plot/benchmark_fs3_mag_corr.svg')

plt.show()

# # --- Magnetic disturbances distribution plot --- #
# scale_factor = 0.008 # for walking
# covf_factor  = 0.8

# plt.rcParams.update({'font.size': font_size})
# fig, ax = plt.subplots(nrows = 7, ncols = 1, figsize = (10, 4), sharey = True, gridspec_kw = {'hspace': -0.6, 'bottom': 0.15})

# ax[0].scatter(mag_dist_all['pelvis_r'], 0.02*np.ones(mag_dist_all['pelvis_r'].shape[0]), label = 'pelvis_r', s = 5, marker = '.', color = 'k')
# ax[0].set_ylim(0, 1)
# plot_density(ax[0], mag_dist_all['pelvis_r'], color = '#DCD6F7', scale = scale_factor, covf = covf_factor, filling = True)

# ax[1].scatter(mag_dist_all['thigh_r'], 0.02*np.ones(mag_dist_all['thigh_r'].shape[0]), label = 'thigh_r', s = 5, marker = '.', color = 'k')
# plot_density(ax[1], mag_dist_all['thigh_r'], color = '#A6B1E1', scale = scale_factor, covf = covf_factor, filling = True)

# ax[2].scatter(mag_dist_all['shank_r'], 0.02*np.ones(mag_dist_all['shank_r'].shape[0]), label = 'shank_r', s = 5, marker = '.', color = 'k')
# plot_density(ax[2], mag_dist_all['shank_r'], color = '#B4869F', scale = scale_factor, covf = covf_factor, filling = True)

# ax[3].scatter(mag_dist_all['foot_r'], 0.02*np.ones(mag_dist_all['foot_r'].shape[0]), label = 'foot_r', s = 5, marker = '.', color = 'k')
# plot_density(ax[3], mag_dist_all['foot_r'], color = '#985F6F', scale = scale_factor, covf = covf_factor, filling = True)

# ax[4].scatter(mag_dist_all['thigh_l'], 0.02*np.ones(mag_dist_all['thigh_l'].shape[0]), label = 'thigh_l', s = 5, marker = '.', color = 'k')
# plot_density(ax[4], mag_dist_all['thigh_l'], color = '#A6B1E1', scale = scale_factor, covf = covf_factor, filling = True)

# ax[5].scatter(mag_dist_all['shank_l'], 0.02*np.ones(mag_dist_all['shank_l'].shape[0]), label = 'shank_l', s = 5, marker = '.', color = 'k')
# plot_density(ax[5], mag_dist_all['shank_l'], color = '#B4869F', scale = scale_factor, covf = covf_factor, filling = True)

# ax[6].scatter(mag_dist_all['foot_l'], 0.02*np.ones(mag_dist_all['foot_l'].shape[0]), label = 'foot_l', s = 5, marker = '.', color = 'k')
# plot_density(ax[6], mag_dist_all['foot_l'], color = '#985F6F', scale = scale_factor, covf = covf_factor, filling = True)

# # ax[6].set_xlabel('Magnetic Field Norm SD (a.u.)', fontsize = fontsize_label)




# for i in range(len(ax)):
#     ax[i].set_xlim(0, 0.28)
#     ax[i].set_xticks([0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28])

#     ax[i].set_yticks([])
#     if i != len(ax) - 1:
#         # ax[i].xaxis.set_ticks_position('none')
#         ax[i].set_xticks([])
#         ax[i].spines['bottom'].set_visible(False)
#     ax[i].spines['top'].set_visible(False)
#     ax[i].spines['right'].set_visible(False)
#     ax[i].spines['left'].set_visible(False)
#     # ax[i].spines['left'].set_position(('outward', 8))
#     ax[i].spines['bottom'].set_position(('outward', 5))
#     # ax[i].spines['bottom'].set_color('lightgray')
#     ax[i].patch.set_alpha(0.0)

# # plt.savefig('imu_benchmark/plot/benchmark_fs3_mag_dist.svg')

# plt.show()








