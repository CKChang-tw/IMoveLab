# name: plot_benchmark_fs2.py
# export PYTHONPATH=$PYTHONPATH:/path/to/imu_benchmark


import pandas as pd 
import numpy as np 
import quaternion
import pickle
import time
import copy
from scipy.stats import norm, gaussian_kde

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from imu_benchmark.constants import constant_common, constant_mt, constant_mocap
from imu_benchmark.utils import common
from imu_benchmark.utils.mt import preprocessing_mt, calibration_mt, ik_mt
from imu_benchmark.utils.eval import eval_utils, eval_segment

import pingouin as pg
from scipy import stats


def plot_box(ax, data, position, color, width, alpha, side = 'left'):
    box = ax.boxplot(data, positions = [position],
                     widths = width,
                     vert = True,
                     patch_artist = True,
                     boxprops = dict(facecolor = color, alpha = alpha),
                     capprops = dict(visible = False),
                     showmeans = True,
                     meanprops = dict(marker = 'x', markeredgecolor = '#F5EE9E', ms = 4),
                     # whiskerprops = dict(x = get_xdata()),
                     medianprops = dict(color = '#4A4063', linewidth = 2.5),
                     flierprops = dict(marker = '+', markerfacecolor = '#9F84BD', markeredgecolor = '#9F84BD', ms = 4), 
                     zorder = 1)
    
    for whisker in box['whiskers']:
        x = whisker.get_xdata()
        if side == 'left':
            whisker.set_xdata([x[0] - width/2, x[1] - width/2])
        else:
            whisker.set_xdata([x[0] + width/2, x[1] + width/2])
        
    for flier in box['fliers']:
        x = flier.get_xdata()
        if side == 'left':
            flier.set_xdata(x - width/2)
        else:
            flier.set_xdata(x + width/2)

def plot_data_point(ax, data, color, position):
    # generate random numbers around position
    n = len(data)
    x = np.random.normal(position, 0.02, n)
    ax.scatter(x, data, color = color, edgecolor = 'none', alpha = 0.5, s = 25, marker = '.')

    return x

def plot_gauss(ax, data, color, position, alpha, scale):
    mu, std = norm.fit(data)
    y = np.linspace(mu - 3*std, mu + 3*std, 100)
    p = norm.pdf(y, mu, std)
    ax.plot(scale*p + position, y, color = color, alpha = alpha, linewidth = 1)

def plot_density(ax, data, position, color, scale, covf, side = 'left'):
    mu, std = norm.fit(data)

    density = gaussian_kde(data)
    ys = np.linspace(mu - 3*std, mu + 3*std, 100)
    density.covariance_factor = lambda : covf
    density._compute_covariance()

    if side == 'left':
        # ax.plot(scale*density(ys) + position, ys, color = color, lw = 1.4, zorder = 1)
        ax.fill_betweenx(ys, position, scale*density(ys) + position, color = color, alpha = 0.2, edgecolor = None, zorder = 0)
    else:
        # ax.plot(position, scale*density(ys) + ys, color = color, lw = 1.4, zorder = 1)
        ax.fill_betweenx(ys, position, -scale*density(ys) + position, color = color, alpha = 0.2, edgecolor = None, zorder = 0)
    
def label_diff(ax, i, j, p, alpha_bon, height, font_size = 11, color = '#7D7C84', range = [0, 15]):
    if p < alpha_bon:
        if alpha_bon == 0.05:
            text = r'$\dag $'
        else:
            text = '*'
    else:
        text = 'ns'

    height = height*(range[1] - range[0]) + range[0]

    askterisk_v = 0.03*(range[1] - range[0])
    bar_v       = 0.015*(range[1] - range[0])

    ax.hlines(height, i, j, color = color, lw = 0.5)
    ax.vlines(i, height, height - bar_v, color = color, lw = 0.5)
    ax.vlines(j, height, height - bar_v, color = color, lw = 0.5)
    ax.annotate(text, xy = ((i + j)/2, height + askterisk_v), zorder = 10, ha = 'center', va = 'center', fontsize = font_size, color = color)



# f_type = 'VQF'
# # f_type = 'MAD'
# # f_type = 'MAH'
# # f_type = 'EKF'
# # f_type = 'RIANN'

# dim = '6D'

# # f_type = 'Xsens'
# # dim = '9D'
task = 'long_walk'

subject_list = ['4l', '5l', '6l', '13l', '23l']
trial_list   = [1, 2, 3]

filter_list_chunk = {'Xsens-9D': {'t1': {'hip': [], 'knee': [], 'ankle': []},
                                  't2': {'hip': [], 'knee': [], 'ankle': []},
                                  't3': {'hip': [], 'knee': [], 'ankle': []}},
                     'VQF-6D': {'t1': {'hip': [], 'knee': [], 'ankle': []},
                                't2': {'hip': [], 'knee': [], 'ankle': []},
                                't3': {'hip': [], 'knee': [], 'ankle': []}}}

for subject in subject_list:
    for trial in trial_list:

        for filter_info in filter_list_chunk.keys():
            f_type, dim = filter_info.split('-')

            filename_chunk = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial) + '_mt_chunk.pkl'
            data_chunk = pd.read_pickle(filename_chunk)

            ind_mean_hip = []
            ind_mean_knee = []
            ind_mean_ankle = []
            for joint in data_chunk.keys():
                if 'hip' in joint:
                    ind_mean_hip.append(data_chunk[joint])
                elif 'knee' in joint:
                    ind_mean_knee.append(data_chunk[joint])
                elif 'ankle' in joint:
                    ind_mean_ankle.append(data_chunk[joint])

            filter_list_chunk[filter_info]['t' + str(trial)]['hip'].append(np.mean(ind_mean_hip, axis = 0))
            filter_list_chunk[filter_info]['t' + str(trial)]['knee'].append(np.mean(ind_mean_knee, axis = 0))
            filter_list_chunk[filter_info]['t' + str(trial)]['ankle'].append(np.mean(ind_mean_ankle, axis = 0))
            
            #     ind_mean_chunk.append(data_chunk[joint])
            # filter_list_chunk[filter_info]['t' + str(trial)].append(np.mean(ind_mean_chunk, axis = 0))

# filter_list_chunk['VQF-9D']['t1']   = np.array(filter_list_chunk['VQF-9D']['t1'])
# filter_list_chunk['VQF-9D']['t2']   = np.array(filter_list_chunk['VQF-9D']['t2'])
# filter_list_chunk['VQF-9D']['t3']   = np.array(filter_list_chunk['VQF-9D']['t3'])
# filter_list_chunk['Xsens-9D']['t1'] = np.array(filter_list_chunk['Xsens-9D']['t1'])
# filter_list_chunk['Xsens-9D']['t2'] = np.array(filter_list_chunk['Xsens-9D']['t2'])
# filter_list_chunk['Xsens-9D']['t3'] = np.array(filter_list_chunk['Xsens-9D']['t3'])
# filter_list_chunk['VQF-6D']['t1']   = np.array(filter_list_chunk['VQF-6D']['t1'])
# filter_list_chunk['VQF-6D']['t2']   = np.array(filter_list_chunk['VQF-6D']['t2'])
# filter_list_chunk['VQF-6D']['t3']   = np.array(filter_list_chunk['VQF-6D']['t3'])
# filter_list_chunk['RIANN-6D']['t1'] = np.array(filter_list_chunk['RIANN-6D']['t1'])
# filter_list_chunk['RIANN-6D']['t2'] = np.array(filter_list_chunk['RIANN-6D']['t2'])
# filter_list_chunk['RIANN-6D']['t3'] = np.array(filter_list_chunk['RIANN-6D']['t3'])


for filter_info in filter_list_chunk.keys():
    for trial in filter_list_chunk[filter_info].keys():
        for joint in filter_list_chunk[filter_info][trial].keys():
            filter_list_chunk[filter_info][trial][joint] = np.array(filter_list_chunk[filter_info][trial][joint])


# breakpoint()


t1_time = np.arange(1, 11, 1)
t2_time = np.arange(16, 26, 1)
t3_time = np.arange(31, 41, 1)


# --- Plot --- #
np.random.seed(0)
box_width = 0.2
scale = 0.7
covf = 0.7

font_size = 11
fontsize_label = 13
fontsize_stats = 10

# color_mt = '#4F5D2F'
color_mt = '#6B4E71'
color_os = '#453F78'
color_mvn = '#772E25'

y_lim_min = 0
y_lim_max = 40




# vqf9d_t1_median                = np.median(filter_list_chunk['VQF-9D']['t1'], axis = 0)

xsens_9d_t1_hip_median     = np.median(filter_list_chunk['Xsens-9D']['t1']['hip'], axis = 0)
xsens_9d_t1_knee_median    = np.median(filter_list_chunk['Xsens-9D']['t1']['knee'], axis = 0)
xsens_9d_t1_ankle_median   = np.median(filter_list_chunk['Xsens-9D']['t1']['ankle'], axis = 0)

xsens_9d_t2_hip_median     = np.median(filter_list_chunk['Xsens-9D']['t2']['hip'], axis = 0)
xsens_9d_t2_knee_median    = np.median(filter_list_chunk['Xsens-9D']['t2']['knee'], axis = 0)
xsens_9d_t2_ankle_median   = np.median(filter_list_chunk['Xsens-9D']['t2']['ankle'], axis = 0)

xsens_9d_t3_hip_median     = np.median(filter_list_chunk['Xsens-9D']['t3']['hip'], axis = 0)
xsens_9d_t3_knee_median    = np.median(filter_list_chunk['Xsens-9D']['t3']['knee'], axis = 0)
xsens_9d_t3_ankle_median   = np.median(filter_list_chunk['Xsens-9D']['t3']['ankle'], axis = 0)



vqf_6d_t1_hip_median     = np.median(filter_list_chunk['VQF-6D']['t1']['hip'], axis = 0)
vqf_6d_t1_knee_median    = np.median(filter_list_chunk['VQF-6D']['t1']['knee'], axis = 0)
vqf_6d_t1_ankle_median   = np.median(filter_list_chunk['VQF-6D']['t1']['ankle'], axis = 0)

vqf_6d_t2_hip_median     = np.median(filter_list_chunk['VQF-6D']['t2']['hip'], axis = 0)
vqf_6d_t2_knee_median    = np.median(filter_list_chunk['VQF-6D']['t2']['knee'], axis = 0)
vqf_6d_t2_ankle_median   = np.median(filter_list_chunk['VQF-6D']['t2']['ankle'], axis = 0)

vqf_6d_t3_hip_median     = np.median(filter_list_chunk['VQF-6D']['t3']['hip'], axis = 0)
vqf_6d_t3_knee_median    = np.median(filter_list_chunk['VQF-6D']['t3']['knee'], axis = 0)
vqf_6d_t3_ankle_median   = np.median(filter_list_chunk['VQF-6D']['t3']['ankle'], axis = 0)




plt.rcParams.update({'font.size': font_size})
fig = plt.figure(figsize=(10, 7))
gs = gridspec.GridSpec(2, 1)
# increase spaces between subplots
gs.update(wspace=0.3, hspace=0.4)

ax1 = fig.add_subplot(gs[0, 0]) # for 9D Xsens
ax2 = fig.add_subplot(gs[1, 0]) # for 6D VQF


ax1.plot(t1_time, xsens_9d_t1_hip_median, alpha = 0.8, linewidth = 1.5, color = '#495D63', label = 'hip')
ax1.plot(t1_time, xsens_9d_t1_knee_median, alpha = 0.8, linewidth = 1.5, color = '#98B6B1', label = 'knee')
ax1.plot(t1_time, xsens_9d_t1_ankle_median, alpha = 0.8, linewidth = 1.5, color = '#FAC8CD', label = 'ankle')

ax1.plot(t2_time, xsens_9d_t2_hip_median, alpha = 0.8, linewidth = 1.5, color = '#495D63')
ax1.plot(t2_time, xsens_9d_t2_knee_median, alpha = 0.8, linewidth = 1.5, color = '#98B6B1')
ax1.plot(t2_time, xsens_9d_t2_ankle_median, alpha = 0.8, linewidth = 1.5, color = '#FAC8CD')

ax1.plot(t3_time, xsens_9d_t3_hip_median, alpha = 0.8, linewidth = 1.5, color = '#495D63')
ax1.plot(t3_time, xsens_9d_t3_knee_median, alpha = 0.8, linewidth = 1.5, color = '#98B6B1')
ax1.plot(t3_time, xsens_9d_t3_ankle_median, alpha = 0.8, linewidth = 1.5, color = '#FAC8CD')

ax1.annotate('T1 Walking', xy = (1, 20), xytext = (1, 24), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax1.annotate(r'(0$^{th}$-10$^{th}$ min)', xy = (1, 20), xytext = (1, 22), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

ax1.annotate('T2 Walking', xy = (16, 20), xytext = (16, 24), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax1.annotate(r'(30$^{th}$-40$^{th}$ min)', xy = (16, 20), xytext = (16, 22), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

ax1.annotate('T3 Walking', xy = (31, 20), xytext = (31, 24), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax1.annotate(r'(60$^{th}$-70$^{th}$ min)', xy = (31, 20), xytext = (31, 22), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')


# ax1.set_title('Xsens 9D', fontsize = fontsize_label)
ax1.set_ylabel(r'RMSD $(^o)$', fontsize = fontsize_label)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_position(('outward', 8))
ax1.spines['bottom'].set_position(('outward', 5))

ax1.set_ylim([0, 25])
# ax2.set_yticks([0, 20, 40, 60, 80])
ax1.set_xlim([0, 40])
ax1.set_xticks([0, 5, 10, 12.5, 15, 20, 25, 27.5, 30, 35, 40])
ax1.set_xticklabels(['0', '5', '10', '...', '30', '35', '40', '...', '60', '65', '70'])
# ax1.set_xlabel('Time (minute)', fontsize = fontsize_label)

# ax1.legend(frameon = False)


ax2.plot(t1_time, vqf_6d_t1_hip_median, alpha = 0.8, linewidth = 1.5, color = '#495D63', label = 'flexion')
ax2.plot(t1_time, vqf_6d_t1_knee_median, alpha = 0.8, linewidth = 1.5, color = '#98B6B1')
ax2.plot(t1_time, vqf_6d_t1_ankle_median, alpha = 0.8, linewidth = 1.5, color = '#FAC8CD')

ax2.plot(t2_time, vqf_6d_t2_hip_median, alpha = 0.8, linewidth = 1.5, color = '#495D63')
ax2.plot(t2_time, vqf_6d_t2_knee_median, alpha = 0.8, linewidth = 1.5, color = '#98B6B1')
ax2.plot(t2_time, vqf_6d_t2_ankle_median, alpha = 0.8, linewidth = 1.5, color = '#FAC8CD')

ax2.plot(t3_time, vqf_6d_t3_hip_median, alpha = 0.8, linewidth = 1.5, color = '#495D63')
ax2.plot(t3_time, vqf_6d_t3_knee_median, alpha = 0.8, linewidth = 1.5, color = '#98B6B1')
ax2.plot(t3_time, vqf_6d_t3_ankle_median, alpha = 0.8, linewidth = 1.5, color = '#FAC8CD')

ax2.annotate('T1 Walking', xy = (1, 20), xytext = (1, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax2.annotate(r'(0$^{th}$-10$^{th}$ min)', xy = (1, 20), xytext = (1, 69), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

ax2.annotate('T2 Walking', xy = (16, 20), xytext = (16, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax2.annotate(r'(30$^{th}$-40$^{th}$ min)', xy = (16, 20), xytext = (16, 69), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

ax2.annotate('T3 Walking', xy = (31, 20), xytext = (31, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax2.annotate(r'(60$^{th}$-70$^{th}$ min)', xy = (31, 20), xytext = (31, 69), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')



ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_position(('outward', 8))
ax2.spines['bottom'].set_position(('outward', 5))

# ax2.set_title('VQF 6D', fontsize = fontsize_label)
ax2.set_ylabel(r'RMSD $(^o)$', fontsize = fontsize_label)

ax2.set_ylim([0, 80])
# ax2.set_yticks([0, 20, 40, 60, 80])
ax2.set_xlim([0, 40])
ax2.set_xticks([0, 5, 10, 12.5, 15, 20, 25, 27.5, 30, 35, 40])
ax2.set_xticklabels(['0', '5', '10', '...', '30', '35', '40', '...', '60', '65', '70'])
ax2.set_xlabel('Time (minute)', fontsize = fontsize_label)

# ax2.legend(frameon = False)

import os

os.makedirs('imu_benchmark/figures', exist_ok = True)

plt.savefig('imu_benchmark/figures/benchmark_fs2.svg')

plt.show()





















