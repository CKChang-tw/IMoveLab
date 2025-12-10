# name: plot_benchmark_f4_placement_detail.py
# description: plot figure 4 for the benchmark kinematics paper
# author: Vu Phan
# date: 2025/02/26


import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import norm, gaussian_kde
import pingouin as pg

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt
from imu_benchmark.utils.eval import eval_utils


reference = '_direct'
title_alignment = '_alignment'


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
    ax.scatter(x, data, color = color, edgecolor = 'none', alpha = 0.5, s = 10, marker = '.')

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
    
def label_diff(ax, i, j, p, alpha_bon, height, font_size = 11, color = '#7D7C84', range = [0, 15], s_pos = 'top'):
    if p < alpha_bon:
        text = '*'
    # else:
    #     text = 'ns'

        height = height*(range[1] - range[0]) + range[0]

        if text == 'ns':
            askterisk_v = 0.03*(range[1] - range[0])
        else:
            askterisk_v = 0.007*(range[1] - range[0])
        bar_v       = 0.015*(range[1] - range[0])

        ax.hlines(height, i, j, color = color, lw = 0.5)
        if s_pos == 'top':
            ax.vlines(i, height, height - bar_v, color = color, lw = 0.5)
            ax.vlines(j, height, height - bar_v, color = color, lw = 0.5)
        else:
            ax.vlines(i, height, height + bar_v, color = color, lw = 0.5)
            ax.vlines(j, height, height + bar_v, color = color, lw = 0.5)
        ax.annotate(text, xy = ((i + j)/2, height + askterisk_v), zorder = 10, ha = 'center', va = 'center', fontsize = font_size, color = color)






# --- Plot overall knee flexion/extension RMSD --- #
# Sensor placement
# placement_list = {'hm': None, 'mm': None, 'lm': None,
#                   'hh': None, 'mh': None, 'lh': None,
#                   'hl': None, 'ml': None, 'll': None}
        
placement_list = {'hh': None, 'lh': None,
                  'hl': None, 'll': None}

f_type = 'VQF'
# f_type = 'Xsens'
# f_type = 'MAH'



# dim = '6d'
dim = '9d'

psa_str = ''
# psa_str = '_psa'




selected_task_for_plot = 'sls'






for placement in placement_list.keys():
    
    print('Placement: ', placement)

    subject_val = []
    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []

        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:

            if placement == 'mm':
                filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + psa_str + '.pkl'
            else:
                filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + placement + reference + title_alignment + '_mt' + psa_str + '.pkl'

            ja_mt = eval_utils.load_data(filename_mt)

            joint_val = []

            # if subject == 17:
            #     breakpoint()

            for joint in ja_mt.keys():

                # if task == 'treadmill_walking' or task == 'treadmill_running':
                #     if '_l' in joint:
                #         continue

                if '_l' in joint:
                    continue

                # if 'sts' not in task:
                #     continue
                    
                if selected_task_for_plot not in task: # only a specific task
                    continue

                if 'knee_flexion' not in joint:
                    continue

                joint_val.append(ja_mt[joint])

            task_val.append(np.nanmean(joint_val))

        subject_val.append(np.nanmean(task_val))
    
    placement_list[placement] = np.array(subject_val)

# breakpoint()

# --- Stats --- #
from scipy import stats
import pandas as pd
import pingouin as pg
# print(pd.DataFrame(placement_list))
print('*** Placement ***')
# print(pg.friedman(pd.DataFrame(placement_list)))
# hl, hh, lh, ll
# print(pg.wilcoxon(placement_list['hl'], placement_list['hh']))
# print(pg.wilcoxon(placement_list['hl'], placement_list['lh']))
# print(pg.wilcoxon(placement_list['hl'], placement_list['ll']))
# print(pg.wilcoxon(placement_list['hh'], placement_list['lh']))
# print(pg.wilcoxon(placement_list['hh'], placement_list['ll']))
# print(pg.wilcoxon(placement_list['lh'], placement_list['ll']))


# # Wilcoxon tests for all pairs
# placement_keys = list(placement_list.keys())
# for i in range(len(placement_keys)):
#     for j in range(i+1, len(placement_keys)):
#         print(placement_keys[i], placement_keys[j])
#         test = pg.wilcoxon(placement_list[placement_keys[i]], placement_list[placement_keys[j]])
#         if test['p-val'].values < 0.05/36:
#             print(' - p = ' + str(test))
#             print()


# breakpoint()

print('Placement')
# print(np.median(placement_list['mm']))
# print(np.median(placement_list['hm']))
# print(np.median(placement_list['lm']))
print(np.median(placement_list['hl']))
print('- Near Q1: ' + str(np.percentile(placement_list['hl'], 25)))
print('- Near Q3: ' + str(np.percentile(placement_list['hl'], 75)))
print(np.median(placement_list['hh']))
# print(np.median(placement_list['mh']))
print(np.median(placement_list['lh']))
print('- Distant Q1: ' + str(np.percentile(placement_list['lh'], 25)))

# print(np.median(placement_list['ml']))
print(np.median(placement_list['ll']))
print()
# breakpoint()

# print(np.median(placement_list['mm'] - placement_list['mh']))
# print(np.percentile(placement_list['mm'] - placement_list['mh'], 25))
# print(np.percentile(placement_list['mm'] - placement_list['mh'], 75))

# print()
# print(np.median(placement_list['mm'] - placement_list['ml']))
# print(np.percentile(placement_list['mm'] - placement_list['ml'], 25))
# print(np.percentile(placement_list['mm'] - placement_list['ml'], 75))



alpha_bon = 0.05/6




# --- Plot detailed segmented kinematics --- #
# f_type = 'VQF'
# dim    = '9d'

reference = 'direct'


placement_list_ik = {'hh': np.array([]), 'lh': np.array([]),
                  'hl': np.array([]), 'll': np.array([])}
mocap_list     = {'hh': np.array([]), 'lh': np.array([]),
                  'hl': np.array([]), 'll': np.array([])}

mocap_alignment  = True

import copy
from imu_benchmark.utils import common
from imu_benchmark.utils.mocap import ik_mocap
from imu_benchmark.utils.eval import eval_segment
subject_list = common.get_subject_list(None)

task = selected_task_for_plot

for subject in subject_list:
    print('*** Subject ' + str(subject))

    if reference == 'direct':
        filename_mc = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + str(subject) + '_' + task + '.pkl'
        ja_mc = eval_utils.load_data(filename_mc)
    else:
        filename_mc = constant_common.IN_LAB_PATH + 's' + str(subject) + '/' + constant_common.MOCAP_OPENSIM_PATH  + constant_common.LAB_TASK_NAME_MAP[task] + '/ik.mot'
        ja_mc = ik_mocap.get_all_ja_os(filename_mc, constant_mt.MT_SAMPLING_RATE)
        
        sync_fn   = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + task + '.pkl'
        sync_info = eval_utils.load_data(sync_fn)

        if sync_info['first_start'] == 'mocap':
            shifting_id = sync_info['shifting_id']
            ja_mc = eval_utils.resync_data(ja_mc, shifting_id)

    mocap_segment_flag = True
    for placement in placement_list_ik.keys():
        filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + placement + psa_str + '.pkl'
        ja_mt = eval_utils.load_data(filename_mt)

        lag             = eval_utils.find_lag(ja_mt['knee_flexion_r'], ja_mc['knee_flexion_r'])
        ja_mc, ja_mt, _ = eval_utils.do_resync(ja_mc, ja_mt, copy.deepcopy(ja_mt), lag)
        print(' - Lag: ' + str(lag))

        if mocap_alignment:

            if subject in list(constant_common.ISOLATED_CASES.keys()):
                if task in constant_common.ISOLATED_CASES[subject].keys():
                    alignment_id = [constant_common.ISOLATED_CASES[subject][task][0], constant_common.ISOLATED_CASES[subject][task][1]]
                else:
                    alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]

            else:
                alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]
            
            ja_mt = eval_utils.get_ja_alignment(ja_mt, ja_mc, alignment_id, task)

        event = eval_segment.get_events(subject, task, lag)
        
        segment_mc = eval_segment.get_segment(ja_mc, event, task)
        segment_mt = eval_segment.get_segment(ja_mt, event, task)

        # placement_list_ik[placement] = np.append((placement_list_ik[placement], segment_mt['knee_flexion_r']))
        # mocap_list[placement]     = np.append((mocap_list[placement], segment_mc['knee_flexion_r']))
        if placement_list_ik[placement].size == 0:
            placement_list_ik[placement] = segment_mt['knee_flexion_r']
        else:
            placement_list_ik[placement] = np.concatenate((placement_list_ik[placement], segment_mt['knee_flexion_r']), axis = 0)
        
        if mocap_list[placement].size == 0:
            mocap_list[placement]     = segment_mc['knee_flexion_r']
        else:
            mocap_list[placement]     = np.concatenate((mocap_list[placement], segment_mc['knee_flexion_r']), axis = 0)

# breakpoint()
            










# --- Plotting --- #
from scipy.stats import spearmanr
from scipy.optimize import curve_fit

def f(x, A, B):
    return A*x + B


np.random.seed(0)
box_width = 0.2
scale = 3
covf = 0.7

font_size = 10
fontsize_label = 13
# fontsize_stats = 10
fontsize_stats = 7

# color_mt = '#4F5D2F'
color_mt = '#6B4E71'
color_os = '#453F78'
color_mvn = '#772E25'

y_lim_min = 0
y_lim_max = 20

plt.rcParams.update({'font.size': font_size})
# fig = plt.figure(figsize=(10, 2.5))
fig = plt.figure(figsize=(4.3, 2))
gs = gridspec.GridSpec(1, 2, width_ratios = [0.6, 0.4])

gs.update(wspace = 0.4, bottom = 0.15)
# gs.update(hspace = 0.45, wspace = 0.3)

# ax1 = fig.add_subplot(gs[0, 0])
# ax2 = fig.add_subplot(gs[0, 1])
# ax3 = fig.add_subplot(gs[0, 2])
# ax4 = fig.add_subplot(gs[0, 3])
# ax5 = fig.add_subplot(gs[1, :])
# # ax6 = fig.add_subplot(gs[2, 0:2])
# # ax7 = fig.add_subplot(gs[2, 2:4])
# ax6 = fig.add_subplot(gs[2, :])

ax6 = fig.add_subplot(gs[0, 0])
ax  = fig.add_subplot(gs[0, 1])


# Placements

C1 = 'hl'
C2 = 'hh'
C3 = 'lh'
C4 = 'll'


color_c1 = '#967AA1'
color_c2 = '#4F5D2F'
color_c3 = '#5F021F'
color_c4 = '#453F78'

print(pg.friedman(pd.DataFrame(placement_list)))
print(' - p C2 vs. C4 = ' + str(pg.wilcoxon(placement_list[C2], placement_list[C4])['p-val'].iloc[0]))

# box_width = 0.1
plot_box(ax6, data = placement_list[C1], position = 1, color = color_c1, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C1], color = color_c1, position = 1.25)
plot_density(ax6, data = placement_list[C1], position = 1 + box_width/2, color = color_c1, scale = scale, covf = covf, side = 'right')
label_diff(ax6, 1 + box_width/1.1, 2 - box_width/1.1, pg.wilcoxon(placement_list[C1], placement_list[C2])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.8, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C1 vs. C2 = ' + str(pg.wilcoxon(placement_list[C1], placement_list[C2])['p-val'].iloc[0]))
label_diff(ax6, 1 + box_width/1.1, 3 - box_width/1.1, pg.wilcoxon(placement_list[C1], placement_list[C3])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.85, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C1 vs. C3 = ' + str(pg.wilcoxon(placement_list[C1], placement_list[C3])['p-val'].iloc[0]))


plot_box(ax6, data = placement_list[C2], position = 2, color = color_c2, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C2], color = color_c2, position = 2.25)
plot_density(ax6, data = placement_list[C2], position = 2 + box_width/2, color = color_c2, scale = scale, covf = covf, side = 'right')
label_diff(ax6, 2 + box_width/1.1, 3 - box_width/1.1, pg.wilcoxon(placement_list[C2], placement_list[C3])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.8, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C2 vs. C3 = ' + str(pg.wilcoxon(placement_list[C2], placement_list[C3])['p-val'].iloc[0]))
label_diff(ax6, 2 + box_width/1.1, 4 - box_width/1.1, pg.wilcoxon(placement_list[C2], placement_list[C4])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.95, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C2 vs. C4 = ' + str(pg.wilcoxon(placement_list[C2], placement_list[C4])['p-val'].iloc[0]))

plot_box(ax6, data = placement_list[C3], position = 3, color = color_c3, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C3], color = color_c3, position = 3.25)
plot_density(ax6, data = placement_list[C3], position = 3 + box_width/2, color = color_c3, scale = scale, covf = covf, side = 'right')
label_diff(ax6, 3 + box_width/1.1, 4 - box_width/1.1, pg.wilcoxon(placement_list[C3], placement_list[C4])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.8, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C3 vs. C4 = ' + str(pg.wilcoxon(placement_list[C3], placement_list[C4])['p-val'].iloc[0]))

plot_box(ax6, data = placement_list[C4], position = 4, color = color_c4, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C4], color = color_c4, position = 4.25)
plot_density(ax6, data = placement_list[C4], position = 4 + box_width/2, color = color_c4, scale = scale, covf = covf, side = 'right')
label_diff(ax6, 1 + box_width/1.1, 4 - box_width/1.1, pg.wilcoxon(placement_list[C4], placement_list[C1])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.95, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C1 vs. C4 = ' + str(pg.wilcoxon(placement_list[C4], placement_list[C1])['p-val'].iloc[0]))

print('corrected p = ' + str(alpha_bon))

ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.spines['left'].set_position(('outward', 8))
ax6.spines['bottom'].set_position(('outward', 5))

ax6.set_xlim([0.2, 4.8])
ax6.set_xticks([0.2, 1, 2, 3, 4, 4.8])
ax6.set_xticklabels(['', 'C1', 'C2', 'C3', 'C4', ''], fontsize = font_size)
ax6.set_ylim([y_lim_min, 20])

# ax6.set_ylabel(r'Knee F/E RMSD ($^\circ$)', fontsize = fontsize_label)
# ax6.set_ylabel(r'Hip F/E RMSD ($^\circ$)', fontsize = fontsize_label)
# ax6.set_ylabel(r'Ankle F/E RMSD ($^\circ$)', fontsize = fontsize_label)


# # Example of placement during sit-to-stand (or sts)


# ax7.spines['top'].set_visible(False)
# ax7.spines['right'].set_visible(False)
# ax7.spines['left'].set_position(('outward', 8))
# ax7.spines['bottom'].set_position(('outward', 5))

# ax7.set_ylabel(r'Knee Flexion ($^o$)', fontsize = fontsize_label)


# plt.savefig('imu_benchmark/plot/benchmark_f4_' + selected_task_for_plot + '.svg')




ax.plot(np.mean(mocap_list[C2], axis = 0), lw = 1.5, color = 'k', alpha = 0.8, linestyle = '--', label = 'Mocap')
# ax.fill_between(np.arange(mocap_list[C2].shape[1]), 
#                 np.mean(mocap_list[C2], axis = 0) - np.std(mocap_list[C2], axis = 0), 
#                 np.mean(mocap_list[C2], axis = 0) + np.std(mocap_list[C2], axis = 0), 
#                 color = 'k', edgecolor = 'none', alpha = 0.1)

ax.plot(np.mean(placement_list_ik[C1], axis = 0), lw = 1.5, color = color_c1, alpha = 0.5, linestyle = (0, (1, 1)), label = 'C1')
# ax.fill_between(np.arange(placement_list_ik[C1].shape[1]), 
#                 np.mean(placement_list_ik[C1], axis = 0) - np.std(placement_list_ik[C1], axis = 0), 
#                 np.mean(placement_list_ik[C1], axis = 0) + np.std(placement_list_ik[C1], axis = 0), 
#                 color = '#967AA1', edgecolor = 'none', alpha = 0.1)

ax.plot(np.mean(placement_list_ik[C2], axis = 0), lw = 1.5, color = color_c2, alpha = 0.5, linestyle = '-', label = 'C2')
# ax.fill_between(np.arange(placement_list_ik[C2].shape[1]), 
#                 np.mean(placement_list_ik[C2], axis = 0) - np.std(placement_list_ik[C2], axis = 0), 
#                 np.mean(placement_list_ik[C2], axis = 0) + np.std(placement_list_ik[C2], axis = 0), 
#                 color = '#4F5D2F', edgecolor = 'none', alpha = 0.1)

ax.plot(np.mean(placement_list_ik[C3], axis = 0), lw = 1.5, color = color_c3, alpha = 0.5, linestyle = '-', label = 'C3')
# ax.fill_between(np.arange(placement_list_ik[C3].shape[1]), 
#                 np.mean(placement_list_ik[C3], axis = 0) - np.std(placement_list_ik[C3], axis = 0), 
#                 np.mean(placement_list_ik[C3], axis = 0) + np.std(placement_list_ik[C3], axis = 0), 
#                 color = '#6B4E71', edgecolor = 'none', alpha = 0.1)

# ax.plot(np.mean(placement_list_ik[C4], axis = 0), lw = 2, color = color_c4, alpha = 0.5, linestyle = (0, (1, 2.5)), label = 'C4')
ax.plot(np.mean(placement_list_ik[C4], axis = 0), lw = 1.5, color = color_c4, alpha = 0.5, linestyle = (0, (3, 1, 1, 1)), label = 'C4')
# ax.fill_between(np.arange(placement_list_ik[C4].shape[1]), 
#                 np.mean(placement_list_ik[C4], axis = 0) - np.std(placement_list_ik[C4], axis = 0), 
#                 np.mean(placement_list_ik[C4], axis = 0) + np.std(placement_list_ik[C4], axis = 0), 
#                 color = '#453F78', edgecolor = 'none', alpha = 0.1)



ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_position(('outward', 8))
ax.spines['bottom'].set_position(('outward', 5))

ax.set_xlim([0, 100])

# if task in ['sts']:
#     ax.set_ylim([0, 100])
# elif task in ['squat']:
#     ax.set_ylim([0, 120]); ax.set_yticks([0, 30, 60, 90, 120])
# elif task in ['treadmill_walking', 'walking']:
#     ax.set_ylim([0, 80])
# elif task == 'treadmill_running':
#     ax.set_ylim([0, 80])

ax.set_ylim([0, 120]); ax.set_yticks([0, 30, 60, 90, 120])
# ax.legend(loc = 'upper left', fontsize = 8, frameon = False)
# ax.legend(loc = 'upper left', fontsize = 8, frameon = True, edgecolor = 'lightgray')

# if task in ['step_up_down']:
#     ax.legend(loc = 'upper right', fontsize = 8, frameon = False)


# fig.patch.set_alpha(0.3)
# ax.patch.set_alpha(0.3)
# ax.set_facecolor([1, 1, 1, 0.5])

fig.patch.set_facecolor([1, 1, 1, 0])
ax.patch.set_facecolor([1, 1, 1, 0.5])

plt.savefig('imu_benchmark/plot/benchmark_f4_' + selected_task_for_plot + '.svg')


plt.show()


























