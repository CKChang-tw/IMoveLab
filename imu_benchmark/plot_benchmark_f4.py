# name: plot_benchmark_f5_xsens_added.py
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
                    #  flierprops = dict(marker = '+', markerfacecolor = '#9F84BD', markeredgecolor = '#9F84BD', ms = 4), 
                    showfliers = False,
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

filter_list = {'VQF-9D': {'t1': [], 't2': [], 't3': []}, 
               'Xsens-9D': {'t1': [], 't2': [], 't3': []},
               'VQF-6D': {'t1': [], 't2': [], 't3': []},
               'RIANN-6D': {'t1': [], 't2': [], 't3': []}}

filter_list_chunk = {'VQF-9D': {'t1': [], 't2': [], 't3': []}, 
                     'Xsens-9D': {'t1': [], 't2': [], 't3': []},
                     'VQF-6D': {'t1': [], 't2': [], 't3': []},
                     'RIANN-6D': {'t1': [], 't2': [], 't3': []}}

for subject in subject_list:
    for trial in trial_list:

        for filter_info in filter_list.keys():
            f_type, dim = filter_info.split('-')

            filename = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial) + '_mt.pkl'
            data = pd.read_pickle(filename)

            ind_mean = []
            for joint in data.keys():
                ind_mean.append(data[joint])
            filter_list[filter_info]['t' + str(trial)].append(np.mean(ind_mean, axis = 0))
            print('*** Subject ' + str(subject) + ' - Trial ' + str(trial))

            filename_chunk = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial) + '_mt_chunk.pkl'
            data_chunk = pd.read_pickle(filename_chunk)

            ind_mean_chunk = []
            for joint in data_chunk.keys():
                ind_mean_chunk.append(data_chunk[joint])
            filter_list_chunk[filter_info]['t' + str(trial)].append(np.mean(ind_mean_chunk, axis = 0))

filter_list_chunk['VQF-9D']['t1']   = np.array(filter_list_chunk['VQF-9D']['t1'])
filter_list_chunk['VQF-9D']['t2']   = np.array(filter_list_chunk['VQF-9D']['t2'])
filter_list_chunk['VQF-9D']['t3']   = np.array(filter_list_chunk['VQF-9D']['t3'])
filter_list_chunk['Xsens-9D']['t1'] = np.array(filter_list_chunk['Xsens-9D']['t1'])
filter_list_chunk['Xsens-9D']['t2'] = np.array(filter_list_chunk['Xsens-9D']['t2'])
filter_list_chunk['Xsens-9D']['t3'] = np.array(filter_list_chunk['Xsens-9D']['t3'])
filter_list_chunk['VQF-6D']['t1']   = np.array(filter_list_chunk['VQF-6D']['t1'])
filter_list_chunk['VQF-6D']['t2']   = np.array(filter_list_chunk['VQF-6D']['t2'])
filter_list_chunk['VQF-6D']['t3']   = np.array(filter_list_chunk['VQF-6D']['t3'])
filter_list_chunk['RIANN-6D']['t1'] = np.array(filter_list_chunk['RIANN-6D']['t1'])
filter_list_chunk['RIANN-6D']['t2'] = np.array(filter_list_chunk['RIANN-6D']['t2'])
filter_list_chunk['RIANN-6D']['t3'] = np.array(filter_list_chunk['RIANN-6D']['t3'])

t1_time = np.arange(1, 11, 1)
t2_time = np.arange(16, 26, 1)
t3_time = np.arange(31, 41, 1)


# breakpoint()


# --- Stats --- #
# VQF 9D
print('VQF 9D')
print(pg.friedman(pd.DataFrame(filter_list['VQF-9D'])))
print(pg.wilcoxon(filter_list['VQF-9D']['t1'], filter_list['VQF-9D']['t2']))
print(pg.wilcoxon(filter_list['VQF-9D']['t1'], filter_list['VQF-9D']['t3']))
print(pg.wilcoxon(filter_list['VQF-9D']['t2'], filter_list['VQF-9D']['t3']))
print()

# Xsens 9D
print('Xsens 9D')
print(pg.friedman(pd.DataFrame(filter_list['Xsens-9D'])))
print(pg.wilcoxon(filter_list['Xsens-9D']['t1'], filter_list['Xsens-9D']['t2']))
print(pg.wilcoxon(filter_list['Xsens-9D']['t1'], filter_list['Xsens-9D']['t3']))
print(pg.wilcoxon(filter_list['Xsens-9D']['t2'], filter_list['Xsens-9D']['t3']))

# RIANN 6D
print('RIANN 6D')
print(pg.friedman(pd.DataFrame(filter_list['RIANN-6D'])))
print(pg.wilcoxon(filter_list['RIANN-6D']['t1'], filter_list['RIANN-6D']['t2']))
print(pg.wilcoxon(filter_list['RIANN-6D']['t1'], filter_list['RIANN-6D']['t3']))
print(pg.wilcoxon(filter_list['RIANN-6D']['t2'], filter_list['RIANN-6D']['t3']))
print()

# VQF 6D
print('VQF 6D')
print(pg.friedman(pd.DataFrame(filter_list['VQF-6D'])))
print(pg.wilcoxon(filter_list['VQF-6D']['t1'], filter_list['VQF-6D']['t2']))
print(pg.wilcoxon(filter_list['VQF-6D']['t1'], filter_list['VQF-6D']['t3']))
print(pg.wilcoxon(filter_list['VQF-6D']['t2'], filter_list['VQF-6D']['t3']))
print()

print('VQF 9D')
print(np.median(filter_list['VQF-9D']['t1']))
print(np.median(filter_list['VQF-9D']['t2']))
print(np.median(filter_list['VQF-9D']['t3']))

print('Xsens 9D')
print(np.median(filter_list['Xsens-9D']['t1']))
print('Xsens 9D t1 Q1:', np.percentile(filter_list['Xsens-9D']['t1'], 25))
print('Xsens 9D t1 Q3:', np.percentile(filter_list['Xsens-9D']['t1'], 75))
print(np.median(filter_list['Xsens-9D']['t2']))
print('Xsens 9D t2 Q1:', np.percentile(filter_list['Xsens-9D']['t2'], 25))
print('Xsens 9D t2 Q3:', np.percentile(filter_list['Xsens-9D']['t2'], 75))
print(np.median(filter_list['Xsens-9D']['t3']))
print('Xsens 9D t3 Q1:', np.percentile(filter_list['Xsens-9D']['t3'], 25))
print('Xsens 9D t3 Q3:', np.percentile(filter_list['Xsens-9D']['t3'], 75))

print('RIANN 6D')
print(np.median(filter_list['RIANN-6D']['t1']))
print(np.median(filter_list['RIANN-6D']['t2']))
print(np.median(filter_list['RIANN-6D']['t3']))

print('VQF 6D')
print(np.median(filter_list['VQF-6D']['t1']))
print('VQF 6D t1 Q1:', np.percentile(filter_list['VQF-6D']['t1'], 25))
print('VQF 6D t1 Q3:', np.percentile(filter_list['VQF-6D']['t1'], 75))
print(np.median(filter_list['VQF-6D']['t2']))
print('VQF 6D t2 Q1:', np.percentile(filter_list['VQF-6D']['t2'], 25))
print('VQF 6D t2 Q3:', np.percentile(filter_list['VQF-6D']['t2'], 75))
print(np.median(filter_list['VQF-6D']['t3']))
print('VQF 6D t3 Q1:', np.percentile(filter_list['VQF-6D']['t3'], 25))
print('VQF 6D t3 Q3:', np.percentile(filter_list['VQF-6D']['t3'], 75))

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

plt.rcParams.update({'font.size': font_size})
fig = plt.figure(figsize=(10, 7.2))
gs = gridspec.GridSpec(2, 4)
# increase spaces between subplots
gs.update(wspace=0.3, hspace=0.3)

ax1 = fig.add_subplot(gs[0, 0]) # for 9D VQF
ax5 = fig.add_subplot(gs[0, 1]) # for 9D Xsens
ax2 = fig.add_subplot(gs[0, 2]) # for 6D RIANN
ax3 = fig.add_subplot(gs[0, 3]) # for 6D VQF

ax4 = fig.add_subplot(gs[1, :]) # for all drifting


# VQF 9D
plot_box(ax1, filter_list['VQF-9D']['t1'], 1, color_mt, box_width, 0.5, side = 'right')
plot_density(ax1, filter_list['VQF-9D']['t1'], 1 + box_width/2, color_mt, scale, covf, side = 'right')
plot_data_point(ax1, filter_list['VQF-9D']['t1'], color_mt, position = 1.25)

plot_box(ax1, filter_list['VQF-9D']['t2'], 2, color_mt, box_width, 0.5, side = 'right')
plot_density(ax1, filter_list['VQF-9D']['t2'], 2 + box_width/2, color_mt, scale, covf, side = 'right')
plot_data_point(ax1, filter_list['VQF-9D']['t2'], color_mt, position = 2.25)

plot_box(ax1, filter_list['VQF-9D']['t3'], 3, color_mt, box_width, 0.5, side = 'right')
plot_density(ax1, filter_list['VQF-9D']['t3'], 3 + box_width/2, color_mt, scale, covf, side = 'right')
plot_data_point(ax1, filter_list['VQF-9D']['t3'], color_mt, position = 3.25)

ax1.scatter(0.7, 37, color = color_mt, edgecolor = 'none', alpha = 0.5, s = 47, marker = 'v', zorder = 2)
ax1.annotate('9D VQF', xy = (0.14, 0.95), xycoords = 'axes fraction', fontsize = 11, ha = 'left', va = 'top', color = color_mt)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_position(('outward', 8))
ax1.spines['bottom'].set_position(('outward', 5))

ax1.set_ylim([y_lim_min, y_lim_max])
ax1.set_yticks([0, 10, 20, 30, 40])
ax1.set_xlim([0.5, 3.5])
ax1.set_xticks([0.5, 1, 2, 3, 3.5])
ax1.set_xticklabels(['', 'T1', 'T2', 'T3', ''])
ax1.set_ylabel(r'Overall RMSD $(^o)$', fontsize = fontsize_label)

# Xsens 9D
plot_box(ax5, filter_list['Xsens-9D']['t1'], 1, color_os, box_width, 0.5, side = 'right')
plot_density(ax5, filter_list['Xsens-9D']['t1'], 1 + box_width/2, color_os, scale*5, covf, side = 'right')
plot_data_point(ax5, filter_list['Xsens-9D']['t1'], color_os, position = 1.25)

plot_box(ax5, filter_list['Xsens-9D']['t2'], 2, color_os, box_width, 0.5, side = 'right')
plot_density(ax5, filter_list['Xsens-9D']['t2'], 2 + box_width/2, color_os, scale*5, covf, side = 'right')
plot_data_point(ax5, filter_list['Xsens-9D']['t2'], color_os, position = 2.25)

plot_box(ax5, filter_list['Xsens-9D']['t3'], 3, color_os, box_width, 0.5, side = 'right')
plot_density(ax5, filter_list['Xsens-9D']['t3'], 3 + box_width/2, color_os, scale*5, covf, side = 'right')
plot_data_point(ax5, filter_list['Xsens-9D']['t3'], color_os, position = 3.25)

ax5.scatter(0.7, 37, color = color_os, edgecolor = 'none', alpha = 0.5, s = 100, marker = '.', zorder = 2)
ax5.annotate('9D XKF (*)', xy = (0.14, 0.95), xycoords = 'axes fraction', fontsize = 11, ha = 'left', va = 'top', color = color_os)

ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.spines['left'].set_position(('outward', 8))
ax5.spines['bottom'].set_position(('outward', 5))

ax5.set_ylim([y_lim_min, y_lim_max])
ax5.set_yticks([0, 10, 20, 30, 40])
ax5.set_xlim([0.5, 3.5])
ax5.set_xticks([0.5, 1, 2, 3, 3.5])
ax5.set_xticklabels(['', 'T1', 'T2', 'T3', ''])


# RIANN 6D
plot_box(ax2, filter_list['RIANN-6D']['t1'], 1, '#414535', box_width, 0.5, side = 'right')
plot_density(ax2, filter_list['RIANN-6D']['t1'], 1 + box_width/2, '#414535', scale + 0.4, covf, side = 'right')
plot_data_point(ax2, filter_list['RIANN-6D']['t1'], '#414535', position = 1.25)

plot_box(ax2, filter_list['RIANN-6D']['t2'], 2, '#414535', box_width, 0.5, side = 'right')
plot_density(ax2, filter_list['RIANN-6D']['t2'], 2 + box_width/2, '#414535', scale + 0.4, covf, side = 'right')
plot_data_point(ax2, filter_list['RIANN-6D']['t2'], '#414535', position = 2.25)

plot_box(ax2, filter_list['RIANN-6D']['t3'], 3, '#414535', box_width, 0.5, side = 'right')
plot_density(ax2, filter_list['RIANN-6D']['t3'], 3 + box_width/2, '#414535', scale + 0.4, covf, side = 'right')
plot_data_point(ax2, filter_list['RIANN-6D']['t3'], '#414535', position = 3.25)

ax2.scatter(0.7, 37, color = '#414535', edgecolor = 'none', alpha = 0.5, s = 100, marker = '*', zorder = 2)
ax2.annotate('6D RIANN', xy = (0.14, 0.95), xycoords = 'axes fraction', fontsize = 11, ha = 'left', va = 'top', color = '#414535')

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_position(('outward', 8))
ax2.spines['bottom'].set_position(('outward', 5))

ax2.set_ylim([y_lim_min, y_lim_max])
ax2.set_yticks([0, 10, 20, 30, 40])
ax2.set_xlim([0.5, 3.5])
ax2.set_xticks([0.5, 1, 2, 3, 3.5])
ax2.set_xticklabels(['', 'T1', 'T2', 'T3', ''])


# VQF 6D
plot_box(ax3, filter_list['VQF-6D']['t1'], 1, '#82A7A6', box_width, 0.5, side = 'right')
plot_density(ax3, filter_list['VQF-6D']['t1'], 1 + box_width/2, '#82A7A6', scale*20, covf, side = 'right')
plot_data_point(ax3, filter_list['VQF-6D']['t1'], '#82A7A6', position = 1.25)

plot_box(ax3, filter_list['VQF-6D']['t2'], 2, '#82A7A6', box_width, 0.5, side = 'right')
plot_density(ax3, filter_list['VQF-6D']['t2'], 2 + box_width/2, '#82A7A6', scale*20, covf, side = 'right')
plot_data_point(ax3, filter_list['VQF-6D']['t2'], '#82A7A6', position = 2.25)

plot_box(ax3, filter_list['VQF-6D']['t3'], 3, '#82A7A6', box_width, 0.5, side = 'right')
plot_density(ax3, filter_list['VQF-6D']['t3'], 3 + box_width/2, '#82A7A6', scale*20, covf, side = 'right')
plot_data_point(ax3, filter_list['VQF-6D']['t3'], '#82A7A6', position = 3.25)

ax3.scatter(0.7, 74, color = '#82A7A6', edgecolor = 'none', alpha = 0.5, s = 47, marker = 's', zorder = 2)
ax3.annotate('6D VQF (*)', xy = (0.14, 0.95), xycoords = 'axes fraction', fontsize = 11, ha = 'left', va = 'top', color = '#82A7A6')

ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['left'].set_position(('outward', 8))
ax3.spines['bottom'].set_position(('outward', 5))

ax3.set_ylim([y_lim_min, 80])
ax3.set_yticks([0, 20, 40, 60, 80])
ax3.set_xlim([0.5, 3.5])
ax3.set_xticks([0.5, 1, 2, 3, 3.5])
ax3.set_xticklabels(['', 'T1', 'T2', 'T3', ''])


def get_whisker(mt_trial):
    Q1_rmsd = np.percentile(mt_trial, 25, axis = 0)
    Q2_rmsd = np.percentile(mt_trial, 50, axis = 0)
    Q3_rmsd = np.percentile(mt_trial, 75, axis = 0)
    IQR_rmsd = Q3_rmsd - Q1_rmsd
    lower_whisker_rmsd = np.maximum(np.min(mt_trial, axis = 0), Q1_rmsd - 1.5*IQR_rmsd)
    upper_whisker_rmsd = np.minimum(np.max(mt_trial, axis = 0), Q3_rmsd + 1.5*IQR_rmsd)

    return lower_whisker_rmsd, upper_whisker_rmsd
    

vqf9d_t1_median                = np.median(filter_list_chunk['VQF-9D']['t1'], axis = 0)
vqf9d_t1_lower, vqf9d_t1_upper = get_whisker(filter_list_chunk['VQF-9D']['t1'])
vqf9d_t2_median                = np.median(filter_list_chunk['VQF-9D']['t2'], axis = 0)
vqf9d_t2_lower, vqf9d_t2_upper = get_whisker(filter_list_chunk['VQF-9D']['t2'])
vqf9d_t3_median                = np.median(filter_list_chunk['VQF-9D']['t3'], axis = 0)
vqf9d_t3_lower, vqf9d_t3_upper = get_whisker(filter_list_chunk['VQF-9D']['t3'])

xsens9d_t1_median                  = np.median(filter_list_chunk['Xsens-9D']['t1'], axis = 0)
xsens9d_t1_lower, xsens9d_t1_upper = get_whisker(filter_list_chunk['Xsens-9D']['t1'])
xsens9d_t2_median                  = np.median(filter_list_chunk['Xsens-9D']['t2'], axis = 0)
xsens9d_t2_lower, xsens9d_t2_upper = get_whisker(filter_list_chunk['Xsens-9D']['t2'])
xsens9d_t3_median                  = np.median(filter_list_chunk['Xsens-9D']['t3'], axis = 0)
xsens9d_t3_lower, xsens9d_t3_upper = get_whisker(filter_list_chunk['Xsens-9D']['t3'])

riann6d_t1_median                  = np.median(filter_list_chunk['RIANN-6D']['t1'], axis = 0)
riann6d_t1_lower, riann6d_t1_upper = get_whisker(filter_list_chunk['RIANN-6D']['t1'])
riann6d_t2_median                  = np.median(filter_list_chunk['RIANN-6D']['t2'], axis = 0)
riann6d_t2_lower, riann6d_t2_upper = get_whisker(filter_list_chunk['RIANN-6D']['t2'])
riann6d_t3_median                  = np.median(filter_list_chunk['RIANN-6D']['t3'], axis = 0)
riann6d_t3_lower, riann6d_t3_upper = get_whisker(filter_list_chunk['RIANN-6D']['t3'])

vqf6d_t1_median                = np.median(filter_list_chunk['VQF-6D']['t1'], axis = 0)
vqf6d_t1_lower, vqf6d_t1_upper = get_whisker(filter_list_chunk['VQF-6D']['t1'])
vqf6d_t2_median                = np.median(filter_list_chunk['VQF-6D']['t2'], axis = 0)
vqf6d_t2_lower, vqf6d_t2_upper = get_whisker(filter_list_chunk['VQF-6D']['t2'])
vqf6d_t3_median                = np.median(filter_list_chunk['VQF-6D']['t3'], axis = 0)
vqf6d_t3_lower, vqf6d_t3_upper = get_whisker(filter_list_chunk['VQF-6D']['t3'])


ax4.plot(t1_time, vqf9d_t1_median, color = color_mt, linewidth = 1.5, label = 'VQF 9D', alpha = 0.8, zorder = 1)
# ax4.fill_between(t1_time, vqf9d_t1_lower, vqf9d_t1_upper, color = color_mt, alpha = 0.2)
ax4.plot(t2_time, vqf9d_t2_median, color = color_mt, linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t2_time, vqf9d_t2_lower, vqf9d_t2_upper, color = color_mt, alpha = 0.2)
ax4.plot(t3_time, vqf9d_t3_median, color = color_mt, linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t3_time, vqf9d_t3_lower, vqf9d_t3_upper, color = color_mt, alpha = 0.2)
ax4.scatter(t1_time[0], vqf9d_t1_median[0], color = color_mt, edgecolor = 'none', alpha = 0.5, s = 47, marker = 'v', zorder = 2)
ax4.scatter(t3_time[0], vqf9d_t3_median[0], color = color_mt, edgecolor = 'none', alpha = 0.5, s = 47, marker = 'v', zorder = 2)

ax4.plot(t1_time, xsens9d_t1_median, color = color_os, linewidth = 1.5, label = 'Xsens 9D', alpha = 0.8, zorder = 1)
# ax4.fill_between(t1_time, xsens9d_t1_lower, xsens9d_t1_upper, color = color_os, alpha = 0.2)
ax4.plot(t2_time, xsens9d_t2_median, color = color_os, linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t2_time, xsens9d_t2_lower, xsens9d_t2_upper, color = color_os, alpha = 0.2)
ax4.plot(t3_time, xsens9d_t3_median, color = color_os, linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t3_time, xsens9d_t3_lower, xsens9d_t3_upper, color = color_os, alpha = 0.2)
ax4.scatter(t1_time[0], xsens9d_t1_median[0], color = color_os, edgecolor = 'none', alpha = 0.5, s = 100, marker = '.', zorder = 2)
ax4.scatter(t3_time[0], xsens9d_t3_median[0], color = color_os, edgecolor = 'none', alpha = 0.5, s = 100, marker = '.', zorder = 2)

ax4.plot(t1_time, riann6d_t1_median, color = '#414535', linewidth = 1.5, label = 'RIANN 6D', alpha = 0.8, zorder = 1)
# ax4.fill_between(t1_time, riann6d_t1_lower, riann6d_t1_upper, color = color_mt, alpha = 0.2)
ax4.plot(t2_time, riann6d_t2_median, color = '#414535', linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t2_time, riann6d_t2_lower, riann6d_t2_upper, color = color_mt, alpha = 0.2)
ax4.plot(t3_time, riann6d_t3_median, color = '#414535', linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t3_time, riann6d_t3_lower, riann6d_t3_upper, color = color_mt, alpha = 0.2)
ax4.scatter(t1_time[0], riann6d_t1_median[0], color = '#414535', edgecolor = 'none', alpha = 0.5, s = 100, marker = '*', zorder = 2)
ax4.scatter(t3_time[0], riann6d_t3_median[0], color = '#414535', edgecolor = 'none', alpha = 0.5, s = 100, marker = '*', zorder = 2)

ax4.plot(t1_time, vqf6d_t1_median, color = '#82A7A6', linewidth = 1.5, label = 'VQF 6D', alpha = 0.8, zorder = 1)
# ax4.fill_between(t1_time, vqf6d_t1_lower, vqf6d_t1_upper, color = color_mt, alpha = 0.2)
ax4.plot(t2_time, vqf6d_t2_median, color = '#82A7A6', linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t2_time, vqf6d_t2_lower, vqf6d_t2_upper, color = color_mt, alpha = 0.2)
ax4.plot(t3_time, vqf6d_t3_median, color = '#82A7A6', linewidth = 1.5, alpha = 0.8, zorder = 1)
# ax4.fill_between(t3_time, vqf6d_t3_lower, vqf6d_t3_upper, color = color_mt, alpha = 0.2)
ax4.scatter(t1_time[0], vqf6d_t1_median[0], color = '#82A7A6', edgecolor = 'none', alpha = 0.5, s = 47, marker = 's', zorder = 2)
ax4.scatter(t3_time[0], vqf6d_t3_median[0], color = '#82A7A6', edgecolor = 'none', alpha = 0.5, s = 47, marker = 's', zorder = 2)

# color_mt = '#6B4E71'
# color_os = '#453F78'

# ax4.fill_between(np.arange(10, 16, 1), 0, 80, color = 'lightgray', edgecolor = 'none', alpha = 0.5)
# ax4.fill_between(np.arange(25, 31, 1), 0, 80, color = 'lightgray', edgecolor = 'none', alpha = 0.5)


# vqf9d_t1_mean = np.mean(filter_list_chunk['VQF-9D']['t1'], axis = 0)
# vqf9d_t1_std  = np.std(filter_list_chunk['VQF-9D']['t1'], axis = 0)
# vqf9d_t2_mean = np.mean(filter_list_chunk['VQF-9D']['t2'], axis = 0)
# vqf9d_t2_std  = np.std(filter_list_chunk['VQF-9D']['t2'], axis = 0)
# vqf9d_t3_mean = np.mean(filter_list_chunk['VQF-9D']['t3'], axis = 0)
# vqf9d_t3_std  = np.std(filter_list_chunk['VQF-9D']['t3'], axis = 0)

# riann6d_t1_mean = np.mean(filter_list_chunk['RIANN-6D']['t1'], axis = 0)
# riann6d_t1_std  = np.std(filter_list_chunk['RIANN-6D']['t1'], axis = 0)
# riann6d_t2_mean = np.mean(filter_list_chunk['RIANN-6D']['t2'], axis = 0)
# riann6d_t2_std  = np.std(filter_list_chunk['RIANN-6D']['t2'], axis = 0)
# riann6d_t3_mean = np.mean(filter_list_chunk['RIANN-6D']['t3'], axis = 0)
# riann6d_t3_std  = np.std(filter_list_chunk['RIANN-6D']['t3'], axis = 0)

# vqf6d_t1_mean = np.mean(filter_list_chunk['VQF-6D']['t1'], axis = 0)
# vqf6d_t1_std  = np.std(filter_list_chunk['VQF-6D']['t1'], axis = 0)
# vqf6d_t2_mean = np.mean(filter_list_chunk['VQF-6D']['t2'], axis = 0)
# vqf6d_t2_std  = np.std(filter_list_chunk['VQF-6D']['t2'], axis = 0)
# vqf6d_t3_mean = np.mean(filter_list_chunk['VQF-6D']['t3'], axis = 0)
# vqf6d_t3_std  = np.std(filter_list_chunk['VQF-6D']['t3'], axis = 0)

# ax4.plot(t1_time, vqf9d_t1_mean, color = color_mt, linewidth = 1.5, label = 'VQF 9D')
# ax4.fill_between(t1_time, vqf9d_t1_mean - vqf9d_t1_std, vqf9d_t1_mean + vqf9d_t1_std, color = color_mt, alpha = 0.2, edgecolor = 'none')
# ax4.plot(t2_time, vqf9d_t2_mean, color = color_mt, linewidth = 1.5)
# ax4.fill_between(t2_time, vqf9d_t2_mean - vqf9d_t2_std, vqf9d_t2_mean + vqf9d_t2_std, color = color_mt, alpha = 0.2, edgecolor = 'none')
# ax4.plot(t3_time, vqf9d_t3_mean, color = color_mt, linewidth = 1.5)
# ax4.fill_between(t3_time, vqf9d_t3_mean - vqf9d_t3_std, vqf9d_t3_mean + vqf9d_t3_std, color = color_mt, alpha = 0.2, edgecolor = 'none')

# ax4.plot(t1_time, riann6d_t1_mean, color = color_mt, linewidth = 1.5, label = 'RIANN 6D')
# ax4.fill_between(t1_time, riann6d_t1_mean - riann6d_t1_std, riann6d_t1_mean + riann6d_t1_std, color = color_mt, alpha = 0.2, edgecolor = 'none')
# ax4.plot(t2_time, riann6d_t2_mean, color = color_mt, linewidth = 1.5)
# ax4.fill_between(t2_time, riann6d_t2_mean - riann6d_t2_std, riann6d_t2_mean + riann6d_t2_std, color = color_mt, alpha = 0.2, edgecolor = 'none')
# ax4.plot(t3_time, riann6d_t3_mean, color = color_mt, linewidth = 1.5)
# ax4.fill_between(t3_time, riann6d_t3_mean - riann6d_t3_std, riann6d_t3_mean + riann6d_t3_std, color = color_mt, alpha = 0.2, edgecolor = 'none')

# ax4.plot(t1_time, vqf6d_t1_mean, color = color_mt, linewidth = 1.5, label = 'VQF 6D')
# ax4.fill_between(t1_time, vqf6d_t1_mean - vqf6d_t1_std, vqf6d_t1_mean + vqf6d_t1_std, color = color_mt, alpha = 0.2, edgecolor = 'none')
# ax4.plot(t2_time, vqf6d_t2_mean, color = color_mt, linewidth = 1.5)
# ax4.fill_between(t2_time, vqf6d_t2_mean - vqf6d_t2_std, vqf6d_t2_mean + vqf6d_t2_std, color = color_mt, alpha = 0.2, edgecolor = 'none')
# ax4.plot(t3_time, vqf6d_t3_mean, color = color_mt, linewidth = 1.5)
# ax4.fill_between(t3_time, vqf6d_t3_mean - vqf6d_t3_std, vqf6d_t3_mean + vqf6d_t3_std, color = color_mt, alpha = 0.2, edgecolor = 'none')

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset, inset_axes

# axins = zoomed_inset_axes(ax4, zoom = 2.5, loc='upper left')  # zoom = 2.5x
axins = inset_axes(ax4, width="60%", height="60%", loc='upper left',
                   bbox_to_anchor=(0.08, 0.06, 0.25, 0.7),  # position relative to figure or axes
                   bbox_transform=ax4.transAxes,  # use the main axes' coordinate system
                   borderpad=0)
axins.plot(t1_time, vqf9d_t1_median, color = color_mt, linewidth = 1.5, label = 'VQF 9D', alpha = 0.8)
axins.plot(t2_time, vqf9d_t2_median, color = color_mt, linewidth = 1.5, alpha = 0.8)
axins.plot(t3_time, vqf9d_t3_median, color = color_mt, linewidth = 1.5, alpha = 0.8)
axins.plot(t1_time, xsens9d_t1_median, color = color_os, linewidth = 1.5, label = 'Xsens 9D', alpha = 0.8)
axins.plot(t2_time, xsens9d_t2_median, color = color_os, linewidth = 1.5, alpha = 0.8)
axins.plot(t3_time, xsens9d_t3_median, color = color_os, linewidth = 1.5, alpha = 0.8)
axins.plot(t1_time, riann6d_t1_median, color = '#414535', linewidth = 1.5, label = 'RIANN 6D', alpha = 0.8)
axins.plot(t2_time, riann6d_t2_median, color = '#414535', linewidth = 1.5, alpha = 0.8)
axins.plot(t3_time, riann6d_t3_median, color = '#414535', linewidth = 1.5, alpha = 0.8)
axins.plot(t1_time, vqf6d_t1_median, color = '#82A7A6', linewidth = 1.5, label = 'VQF 6D', alpha = 0.8)
axins.plot(t2_time, vqf6d_t2_median, color = '#82A7A6', linewidth = 1.5, alpha = 0.8)
axins.plot(t3_time, vqf6d_t3_median, color = '#82A7A6', linewidth = 1.5, alpha = 0.8)

axins.scatter(t1_time[0], vqf9d_t1_median[0], color = color_mt, edgecolor = 'none', alpha = 0.5, s = 47, marker = 'v', zorder = 2)
axins.scatter(t1_time[0], xsens9d_t1_median[0], color = color_os, edgecolor = 'none', alpha = 0.5, s = 100, marker = '.', zorder = 2)
axins.scatter(t1_time[0], riann6d_t1_median[0], color = '#414535', edgecolor = 'none', alpha = 0.5, s = 100, marker = '*', zorder = 2)
axins.scatter(t1_time[0], vqf6d_t1_median[0], color = '#82A7A6', edgecolor = 'none', alpha = 0.5, s = 47, marker = 's', zorder = 2)

axins.patch.set_facecolor('none')
# color_mt = '#6B4E71'

axins.set_xlim([0.5, 4])
axins.set_ylim([0.5, 15])

# mark_inset(ax4, axins, loc1=2, loc2=4, fc = 'lightgray', ec = 'none', alpha = 0.4, zorder = 0)
mark_inset(ax4, axins, loc1=2, loc2=4, fc = 'none', ec = '#320E3B', linestyle = 'dashed', alpha = 0.3, zorder = 0)

axins.spines['top'].set_visible(False)
axins.spines['right'].set_visible(False)
# axins.spines['left'].set_position(('outward', 8))
# axins.spines['bottom'].set_position(('outward', 5))

# ax4.vlines(1, 0, 80, linestyles = 'dashed', color = 'lightgray', lw = 1.5)
# ax4.annotate('1st min', xy = (1, 75), xytext = (0, 69), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84', rotation = 90)
# ax4.annotate(r'1$^{st}$ min', xy = (1, 75), xytext = (4, 49), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84', rotation = 0, zorder = 10)
ax4.annotate(r'1$^{st}$ min', xy = (1, 75), xytext = (1, 11), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84', rotation = 0, zorder = 10)
ax4.annotate('T1 Walking', xy = (1, 75), xytext = (1, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax4.annotate(r'(0$^{th}$-10$^{th}$ min)', xy = (1, 75), xytext = (1, 70), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

# ax4.vlines(16, 0, 80, linestyles = 'dashed', color = 'lightgray', lw = 1.5)
# ax4.annotate('31st min', xy = (16, 75), xytext = (15, 69), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84', rotation = 90)
ax4.annotate('T2 Walking', xy = (16, 75), xytext = (16, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax4.annotate(r'(30$^{th}$-40$^{th}$ min)', xy = (16, 75), xytext = (16, 70), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

# ax4.vlines(31, 0, 80, linestyles = 'dashed', color = 'lightgray', lw = 1.5)
# ax4.annotate('61st min', xy = (31, 75), xytext = (30, 69), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84', rotation = 90)
ax4.annotate(r'61$^{st}$ min', xy = (31, 75), xytext = (31, 40), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84', rotation = 0, zorder = 10)
ax4.annotate('T3 Walking', xy = (31, 75), xytext = (31, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax4.annotate(r'(60$^{th}$-70$^{th}$ min)', xy = (31, 75), xytext = (31, 70), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['left'].set_position(('outward', 8))
ax4.spines['bottom'].set_position(('outward', 5))

ax4.set_ylim([y_lim_min, 80])
ax4.set_yticks([0, 20, 40, 60, 80])
ax4.set_xlim([0, 40])
ax4.set_xticks([0, 5, 10, 12.5, 15, 20, 25, 27.5, 30, 35, 40])
ax4.set_xticklabels(['0', '5', '10', '...', '30', '35', '40', '...', '60', '65', '70'])
ax4.set_xlabel('Time (minute)', fontsize = fontsize_label)

ax4.set_ylabel(r'Overall RMSD $(^o)$', fontsize = fontsize_label)



plt.savefig('imu_benchmark/plot/benchmark_f5_xsens_added.svg')


plt.show()


# breakpoint()

























