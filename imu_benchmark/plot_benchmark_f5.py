# name: plot_benchmark_f3.py
# description: plot figure 3 of the benchmark kinematics paper
# author: Vu Phan
# date: 2025/02/25


import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import norm, gaussian_kde

import pandas as pd

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt
from imu_benchmark.utils.eval import eval_utils


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
    
def label_diff(ax, i, j, p, alpha_bon, height, font_size = 11, color = '#7D7C84', range = [0, 15], s_pos = 'top'):
    if p < alpha_bon:
        text = '*'
    else:
        text = 'ns'

    height = height*(range[1] - range[0]) + range[0]

    if text == 'ns':
        askterisk_v = 0.03*(range[1] - range[0])
    else:
        askterisk_v = 0.01*(range[1] - range[0])
    bar_v       = 0.015*(range[1] - range[0])

    ax.hlines(height, i, j, color = color, lw = 0.5)
    if s_pos == 'top':
        ax.vlines(i, height, height - bar_v, color = color, lw = 0.5)
        ax.vlines(j, height, height - bar_v, color = color, lw = 0.5)
    else:
        ax.vlines(i, height, height + bar_v, color = color, lw = 0.5)
        ax.vlines(j, height, height + bar_v, color = color, lw = 0.5)
    ax.annotate(text, xy = ((i + j)/2, height + askterisk_v), zorder = 10, ha = 'center', va = 'center', fontsize = font_size, color = color)


# --- Unconstrained vs. OpenSense (main experiment) --- #

# filter_list = {'VQF-9D': None, 'RIANN-6D': None}
# filter_list_os = {'VQF-9D': None, 'RIANN-6D': None}
    
filter_list = {'VQF-9D': None}
filter_list_os = {'VQF-9D': None}

reference = '_direct'
# reference = 'opensim'
title_alignment = '_alignment'

for filter_info in filter_list.keys():
    f_type, dim = filter_info.split('-')

    print('*** Filter ' + f_type + ' ' + dim)

    subject_val = []
    subject_val_os = []

    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []
        task_val_os = []


        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:
        # for task in ['treadmill_walking']:
            filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + '.pkl'
            filename_os = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_os' + '.pkl'
            
            ja_mt = eval_utils.load_data(filename_mt)
            ja_os = eval_utils.load_data(filename_os)

            # # if subject == 18:
            # if subject == 7:
            #     breakpoint()

            joint_val = []
            joint_val_os = []

            for joint in ja_os.keys(): # only 5 DoFs
                if task == 'treadmill_walking' or task == 'treadmill_running':
                    if '_l' in joint:
                        continue
                
                if 'ankle_angle' in joint:
                    joint_mt = joint.replace('ankle_angle', 'ankle_flexion')
                else:
                    joint_mt = joint
                joint_val.append(ja_mt[joint_mt])
                joint_val_os.append(ja_os[joint])

            task_val.append(np.mean(joint_val))
            task_val_os.append(np.mean(joint_val_os))

        subject_val.append(np.mean(task_val))
        subject_val_os.append(np.mean(task_val_os))
    
    filter_list[filter_info] = np.array(subject_val)
    filter_list_os[filter_info] = np.array(subject_val_os)

    # breakpoint()

# --- Unconstrained vs. OpenSense vs. Xsens (sub experiment) --- #
sub_filter_list     = {'Xsens-9D': None}
sub_filter_list_os  = {'Xsens-9D': None}
sub_filter_list_mvn = {'Xsens-9D': None}

reference = 'direct'
# reference = 'opensim'

for filter_info in sub_filter_list.keys():
    f_type, dim = filter_info.split('-')

    print('*** Filter ' + f_type + ' ' + dim)

    subject_val = []
    subject_val_os = []
    subject_val_mvn = []

    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []
        task_val_os = []
        task_val_mvn = []


        for task in ['sts_x', 'walking_x', 'running_x']:
        # for task in ['running_x']:
            filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mvn' + '.pkl'
            filename_os = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mvn_opensense' + '.pkl'
            filename_mvn = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mvn_biomodel' + '.pkl'
            
            ja_mt = eval_utils.load_data(filename_mt)
            ja_os = eval_utils.load_data(filename_os)
            ja_mvn = eval_utils.load_data(filename_mvn)

            # # if subject == 18:
            # if subject == 7:
            #     breakpoint()

            joint_val = []
            joint_val_os = []
            joint_val_mvn = []

            for joint in ja_os.keys(): # only 5 DoFs
                if task == 'walking_x' or task == 'running_x':
                    if '_l' in joint:
                        continue
                
                joint_val.append(ja_mt[joint])
                joint_val_os.append(ja_os[joint])
                joint_val_mvn.append(ja_mvn[joint])

            task_val.append(np.mean(joint_val))
            task_val_os.append(np.mean(joint_val_os))
            task_val_mvn.append(np.mean(joint_val_mvn))

        subject_val.append(np.mean(task_val))
        subject_val_os.append(np.mean(task_val_os))
        subject_val_mvn.append(np.mean(task_val_mvn))
    
    sub_filter_list[filter_info] = np.array(subject_val)
    sub_filter_list_os[filter_info] = np.array(subject_val_os)
    sub_filter_list_mvn[filter_info] = np.array(subject_val_mvn)
        



# --- Unconstrained vs. Constrained for long walk data --- #
task = 'long_walk'

subject_list = ['4l', '5l', '6l', '13l', '23l']
trial_list   = [1, 2, 3]

lw_filter_list = {'Xsens-9D': {'t1': [], 't2': [], 't3': []},
               'VQF-6D': {'t1': [], 't2': [], 't3': []}}

lw_filter_list_os = {'Xsens-9D': {'t1': [], 't2': [], 't3': []},
                  'VQF-6D': {'t1': [], 't2': [], 't3': []}}

lw_filter_list_chunk = {'Xsens-9D': {'t1': [], 't2': [], 't3': []},
                     'VQF-6D': {'t1': [], 't2': [], 't3': []}}

lw_filter_list_os_chunk = {'Xsens-9D': {'t1': [], 't2': [], 't3': []},
                        'VQF-6D': {'t1': [], 't2': [], 't3': []}}


for subject in subject_list:
    for trial in trial_list:

        for filter_info in lw_filter_list.keys():
            f_type, dim = filter_info.split('-')

            filename = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial) + '_mt.pkl'
            filename_os = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial) + '_os.pkl'
            data = pd.read_pickle(filename)
            data_os = pd.read_pickle(filename_os)

            ind_mean = []
            ind_mean_os = []
            for joint in data.keys():
                ind_mean.append(data[joint])
                ind_mean_os.append(data_os[joint])
            lw_filter_list[filter_info]['t' + str(trial)].append(np.mean(ind_mean, axis = 0))
            lw_filter_list_os[filter_info]['t' + str(trial)].append(np.mean(ind_mean_os, axis = 0))
            print('*** Subject ' + str(subject) + ' - Trial ' + str(trial))

            filename_chunk = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial) + '_mt_chunk.pkl'
            filename_os_chunk = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial) + '_os_chunk.pkl'
            data_chunk = pd.read_pickle(filename_chunk)
            data_os_chunk = pd.read_pickle(filename_os_chunk)

            ind_mean_chunk = []
            ind_mean_os_chunk = []
            for joint in data_chunk.keys():
                ind_mean_chunk.append(data_chunk[joint])
                ind_mean_os_chunk.append(data_os_chunk[joint])
            lw_filter_list_chunk[filter_info]['t' + str(trial)].append(np.mean(ind_mean_chunk, axis = 0))
            lw_filter_list_os_chunk[filter_info]['t' + str(trial)].append(np.mean(ind_mean_os_chunk, axis = 0))

lw_filter_list_chunk['Xsens-9D']['t1'] = np.array(lw_filter_list_chunk['Xsens-9D']['t1'])
lw_filter_list_chunk['Xsens-9D']['t2'] = np.array(lw_filter_list_chunk['Xsens-9D']['t2'])
lw_filter_list_chunk['Xsens-9D']['t3'] = np.array(lw_filter_list_chunk['Xsens-9D']['t3'])
lw_filter_list_chunk['VQF-6D']['t1']   = np.array(lw_filter_list_chunk['VQF-6D']['t1'])
lw_filter_list_chunk['VQF-6D']['t2']   = np.array(lw_filter_list_chunk['VQF-6D']['t2'])
lw_filter_list_chunk['VQF-6D']['t3']   = np.array(lw_filter_list_chunk['VQF-6D']['t3'])

lw_filter_list_os_chunk['Xsens-9D']['t1'] = np.array(lw_filter_list_os_chunk['Xsens-9D']['t1'])
lw_filter_list_os_chunk['Xsens-9D']['t2'] = np.array(lw_filter_list_os_chunk['Xsens-9D']['t2'])
lw_filter_list_os_chunk['Xsens-9D']['t3'] = np.array(lw_filter_list_os_chunk['Xsens-9D']['t3'])
lw_filter_list_os_chunk['VQF-6D']['t1']   = np.array(lw_filter_list_os_chunk['VQF-6D']['t1'])
lw_filter_list_os_chunk['VQF-6D']['t2']   = np.array(lw_filter_list_os_chunk['VQF-6D']['t2'])
lw_filter_list_os_chunk['VQF-6D']['t3']   = np.array(lw_filter_list_os_chunk['VQF-6D']['t3'])

t1_time = np.arange(1, 11, 1)
t2_time = np.arange(16, 26, 1)
t3_time = np.arange(31, 41, 1)



# --- Stats --- #
import pingouin as pg
import pandas as pd

print('*** Main experiment ***')
print('# Normality test')
print(pg.normality(filter_list['VQF-9D']))
# print(pg.normality(filter_list['RIANN-6D']))
print(pg.normality(filter_list_os['VQF-9D']))
# print(pg.normality(filter_list_os['RIANN-6D']))
print()
print('# Friedman test')
print(pg.friedman(pd.DataFrame({'Unconstrained': filter_list['VQF-9D'], 'OpenSense': filter_list_os['VQF-9D']})))
print()
print('# Wilcoxon test')
unconstrained_vs_opensense = pg.wilcoxon(filter_list['VQF-9D'], filter_list_os['VQF-9D'])
print('Unconstrained vs. OpenSense: p = ' + str(unconstrained_vs_opensense['p-val'].values[0]))
# breakpoint()
print()
print()
print('*** Sub experiment ***')
print('# Normality test')
print(pg.normality(sub_filter_list['Xsens-9D']))
print(pg.normality(sub_filter_list_os['Xsens-9D']))
print(pg.normality(sub_filter_list_mvn['Xsens-9D']))
print()
print('# Friedman test')
print(pg.friedman(pd.DataFrame({'Unconstrained': sub_filter_list['Xsens-9D'], 'OpenSense': sub_filter_list_os['Xsens-9D'], 'MVN': sub_filter_list_mvn['Xsens-9D']})))
print()
print('# Wilcoxon test')
sub_unconstrained_vs_opensense = pg.wilcoxon(sub_filter_list['Xsens-9D'], sub_filter_list_os['Xsens-9D'])
print('Unconstrained vs. OpenSense: p = ' + str(sub_unconstrained_vs_opensense['p-val'].values[0]))
sub_unconstrained_vs_mvn = pg.wilcoxon(sub_filter_list['Xsens-9D'], sub_filter_list_mvn['Xsens-9D'])
print('Unconstrained vs. MVN: p = ' + str(sub_unconstrained_vs_mvn['p-val'].values[0]))
sub_opensense_vs_mvn = pg.wilcoxon(sub_filter_list_os['Xsens-9D'], sub_filter_list_mvn['Xsens-9D'])
print('OpenSense vs. MVN: p = ' + str(sub_opensense_vs_mvn['p-val'].values[0]))
print()

print('Unconstrained (main) = ' + str(np.median(filter_list['VQF-9D'])))
print('OpenSense (main) = ' + str(np.median(filter_list_os['VQF-9D'])))
print('--> difference = ' + str(np.median(filter_list['VQF-9D']) - np.median(filter_list_os['VQF-9D'])))
print()
print('Unconstrained (sub) = ' + str(np.median(sub_filter_list['Xsens-9D'])))
print('OpenSense (sub) = ' + str(np.median(sub_filter_list_os['Xsens-9D'])))
print('--> difference = ' + str(np.median(sub_filter_list['Xsens-9D']) - np.median(sub_filter_list_os['Xsens-9D'])))
print('MVN (sub) = ' + str(np.median(sub_filter_list_mvn['Xsens-9D'])))
print('--> difference = ' + str(np.median(sub_filter_list['Xsens-9D']) - np.median(sub_filter_list_mvn['Xsens-9D'])))



print()
print('***')
print(np.median(filter_list_os['VQF-9D'] - filter_list['VQF-9D']))
print(np.percentile(filter_list_os['VQF-9D'] - filter_list['VQF-9D'], 25))
print(np.percentile(filter_list_os['VQF-9D'] - filter_list['VQF-9D'], 75))
print()
print()
print(np.median(sub_filter_list_os['Xsens-9D'] - sub_filter_list['Xsens-9D']))
print(np.percentile(sub_filter_list_os['Xsens-9D'] - sub_filter_list['Xsens-9D'], 25))
print(np.percentile(sub_filter_list_os['Xsens-9D'] - sub_filter_list['Xsens-9D'], 75))
print()
print(np.median(sub_filter_list_mvn['Xsens-9D'] - sub_filter_list['Xsens-9D']))
print(np.percentile(sub_filter_list_mvn['Xsens-9D'] - sub_filter_list['Xsens-9D'], 25))
print(np.percentile(sub_filter_list_mvn['Xsens-9D'] - sub_filter_list['Xsens-9D'], 75))


print()
print('*** Long walk experiment ***')
print('# 6D VQF')
lw_vqf6d_t1 = pg.wilcoxon(lw_filter_list['VQF-6D']['t1'], lw_filter_list_os['VQF-6D']['t1'])
print('VQF-6D T1: p = ' + str(lw_vqf6d_t1['p-val'].values[0]))
lw_vqf6d_t2 = pg.wilcoxon(lw_filter_list['VQF-6D']['t2'], lw_filter_list_os['VQF-6D']['t2'])
print('VQF-6D T2: p = ' + str(lw_vqf6d_t2['p-val'].values[0]))
lw_vqf6d_t3 = pg.wilcoxon(lw_filter_list['VQF-6D']['t3'], lw_filter_list_os['VQF-6D']['t3'])
print('VQF-6D T3: p = ' + str(lw_vqf6d_t3['p-val'].values[0]))
print()
print('# 9D Xsens')
lw_xsens9d_t1 = pg.wilcoxon(lw_filter_list['Xsens-9D']['t1'], lw_filter_list_os['Xsens-9D']['t1'])
print('Xsens-9D T1: p = ' + str(lw_xsens9d_t1['p-val'].values[0]))
lw_xsens9d_t2 = pg.wilcoxon(lw_filter_list['Xsens-9D']['t2'], lw_filter_list_os['Xsens-9D']['t2'])
print('Xsens-9D T2: p = ' + str(lw_xsens9d_t2['p-val'].values[0]))
lw_xsens9d_t3 = pg.wilcoxon(lw_filter_list['Xsens-9D']['t3'], lw_filter_list_os['Xsens-9D']['t3'])
print('Xsens-9D T3: p = ' + str(lw_xsens9d_t3['p-val'].values[0]))




# --- Plot --- #
np.random.seed(0)
box_width = 0.2
scale = 1.5
covf = 0.7

font_size = 11
fontsize_label = 13
fontsize_stats = 10

# color_mt = '#4F5D2F'
color_mt = '#6B4E71'
color_os = '#453F78'
color_mvn = '#772E25'

plt.rcParams.update({'font.size': font_size})
fig = plt.figure(figsize=(10, 3.5))
# gs = gridspec.GridSpec(3, 2, width_ratios=[0.43, 0.57])
gs = gridspec.GridSpec(1, 2)

# add more space between the first and second rows
gs.update(wspace = 0.15, hspace = 0.4, bottom = 0.2)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])



# Unconstrained vs. OpenSense (main experiment)
plot_box(ax1, data = filter_list['VQF-9D'], position = 1, color = color_mt, width = box_width/1.3, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = filter_list['VQF-9D'], color = color_mt, position = 1.25)
plot_density(ax1, data = filter_list['VQF-9D'], position = 1 + box_width/1.3/2, color = color_mt, scale = scale, covf = covf, side = 'right')

plot_box(ax1, data = filter_list_os['VQF-9D'], position = 2, color = color_mt, width = box_width/1.3, alpha = 0.8, side = 'left')
plot_data_point(ax1, data = filter_list_os['VQF-9D'], color = color_mt, position = 1.75)
plot_density(ax1, data = filter_list_os['VQF-9D'], position = 2 - box_width/1.3/2, color = color_mt, scale = scale, covf = covf, side = 'left')
label_diff(ax1, 1, 2, unconstrained_vs_opensense['p-val'].iloc[0], 0.05, height = 0.92, font_size = fontsize_stats, color = color_mt)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_position(('outward', 8))
ax1.spines['bottom'].set_position(('outward', 5))

ax1.set_xlim([0.2, 2.8])
ax1.set_xticks([0.2, 1, 2, 2.8])
# ax1.set_xticklabels(['', 'Unconstrained', 'OpenSense', ''], fontsize = font_size)
ax1.set_xticklabels([])
tick_positions = [0.2, 1, 2, 2.8]
labels_top = ['', 'Direct', 'OpenSense', '']
labels_bottom = ['', '(9D VQF)', '(9D VQF)', '']

for i, (top, bottom) in enumerate(zip(labels_top, labels_bottom)):
    ax1.text(tick_positions[i], -1.9, top, ha='center', va='center', fontsize = font_size, color='k', transform=ax1.transData)  # Top row (red)
    ax1.text(tick_positions[i], -3.3, bottom, ha='center', va='center', fontsize = fontsize_stats, color= color_mt, transform=ax1.transData)  # Bottom row (blue)


ax1.set_ylim([0, 15])
ax1.set_yticks([0, 5, 10, 15])
ax1.set_ylabel(r'Overall RMSD ($^\circ$)', fontsize = fontsize_label)

# Unconstrained vs. OpenSense vs. Xsens (sub experiment)
plot_box(ax2, data = sub_filter_list['Xsens-9D'], position = 1, color = color_os, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax2, data = sub_filter_list['Xsens-9D'], color = color_os, position = 1.25)
plot_density(ax2, data = sub_filter_list['Xsens-9D'], position = 1 + box_width/2, color = color_os, scale = scale, covf = covf, side = 'right')

plot_box(ax2, data = sub_filter_list_os['Xsens-9D'], position = 2, color = color_os, width = box_width, alpha = 0.8, side = 'left')
plot_data_point(ax2, data = sub_filter_list_os['Xsens-9D'], color = color_os, position = 1.75)
plot_density(ax2, data = sub_filter_list_os['Xsens-9D'], position = 2 - box_width/2, color = color_os, scale = scale, covf = covf, side = 'left')
label_diff(ax2, 1, 2, sub_unconstrained_vs_opensense['p-val'].iloc[0], 0.05/2, height = 0.92, font_size = fontsize_stats, color = color_os)

plot_box(ax2, data = sub_filter_list_mvn['Xsens-9D'], position = 3, color = color_os, width = box_width, alpha = 0.8, side = 'left')
plot_data_point(ax2, data = sub_filter_list_mvn['Xsens-9D'], color = color_os, position = 2.75)
plot_density(ax2, data = sub_filter_list_mvn['Xsens-9D'], position = 3 - box_width/2, color = color_os, scale = scale, covf = covf, side = 'left')
label_diff(ax2, 1, 3, sub_unconstrained_vs_mvn['p-val'].iloc[0], 0.05/2, height = 0.99, font_size = fontsize_stats, color = color_os)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_position(('outward', 8))
ax2.spines['bottom'].set_position(('outward', 5))

ax2.set_xlim([0.2, 3.8])
ax2.set_xticks([0.2, 1, 2, 3, 3.8])
# ax2.set_xticklabels(['', 'Unconstrained', 'OpenSense', 'MVN', ''], fontsize = font_size)
ax2.set_xticklabels([])
tick_positions = [0.2, 1, 2, 3, 3.8]
labels_top = ['', 'Direct', 'OpenSense', 'MVN', '']
labels_bottom = ['', '(9D XKF)', '(9D XKF)', '(9D XKF)', '']

for i, (top, bottom) in enumerate(zip(labels_top, labels_bottom)):
    ax2.text(tick_positions[i], -1.9, top, ha='center', va='center', fontsize = font_size, color='k', transform=ax2.transData)  # Top row (red)
    ax2.text(tick_positions[i], -3.3, bottom, ha='center', va='center', fontsize = fontsize_stats, color= color_os, transform=ax2.transData)  # Bottom row (blue)

ax2.set_ylim([0, 15])
ax2.set_yticks([0, 5, 10, 15])
# ax2.set_yticklabels([])


plt.savefig('imu_benchmark/plot/benchmark_f3_part1.svg')
# plt.show()



plt.rcParams.update({'font.size': font_size})
fig = plt.figure(figsize=(10, 7))
# gs = gridspec.GridSpec(3, 2, width_ratios=[0.43, 0.57])
gs = gridspec.GridSpec(2, 2)

# add more space between the first and second rows
gs.update(wspace = 0.15, hspace = 0.4, bottom = 0.1)

ax3 = fig.add_subplot(gs[0, 0])
ax4 = fig.add_subplot(gs[0, 1])

ax5 = fig.add_subplot(gs[1, :])


box_width/= 2
scale/= 4

# print(np.median(lw_filter_list_os_chunk['VQF-6D']['t2'], axis = 0))
# print(np.median(lw_filter_list_os_chunk['VQF-6D']['t3'], axis = 0))

plot_box(ax3, lw_filter_list['VQF-6D']['t1'], 0.8, '#82A7A6', box_width, 0.5, side = 'right')
plot_density(ax3, lw_filter_list['VQF-6D']['t1'], 0.8 + box_width/2, '#82A7A6', scale*20, covf, side = 'right')
plot_data_point(ax3, lw_filter_list['VQF-6D']['t1'], '#82A7A6', position = 0.9)

plot_box(ax3, lw_filter_list_os['VQF-6D']['t1'], 1.2, '#82A7A6', box_width, 0.8, side = 'left')
plot_density(ax3, lw_filter_list_os['VQF-6D']['t1'], 1.2 - box_width/2, '#82A7A6', scale*20, covf, side = 'left')
plot_data_point(ax3, lw_filter_list_os['VQF-6D']['t1'], '#82A7A6', position = 1.1)
label_diff(ax3, 0.8, 1.2, lw_vqf6d_t1['p-val'].values[0], 0.05/3, height = 0.97, range = (0, 80), font_size = fontsize_stats, color = '#82A7A6')

plot_box(ax3, lw_filter_list['VQF-6D']['t2'], 1.8, '#82A7A6', box_width, 0.5, side = 'right')
plot_density(ax3, lw_filter_list['VQF-6D']['t2'], 1.8 + box_width/2, '#82A7A6', scale*20, covf, side = 'right')
plot_data_point(ax3, lw_filter_list['VQF-6D']['t2'], '#82A7A6', position = 1.9)

plot_box(ax3, lw_filter_list_os['VQF-6D']['t2'], 2.2, '#82A7A6', box_width, 0.8, side = 'left')
plot_density(ax3, lw_filter_list_os['VQF-6D']['t2'], 2.2 - box_width/2, '#82A7A6', scale*20, covf, side = 'left')
plot_data_point(ax3, lw_filter_list_os['VQF-6D']['t2'], '#82A7A6', position = 2.1)
label_diff(ax3, 1.8, 2.2, lw_vqf6d_t2['p-val'].values[0], 0.05/3, height = 0.97, range = (0, 80), font_size = fontsize_stats, color = '#82A7A6')

plot_box(ax3, lw_filter_list['VQF-6D']['t3'], 2.8, '#82A7A6', box_width, 0.5, side = 'right')
plot_density(ax3, lw_filter_list['VQF-6D']['t3'], 2.8 + box_width/2, '#82A7A6', scale*20, covf, side = 'right')
plot_data_point(ax3, lw_filter_list['VQF-6D']['t3'], '#82A7A6', position = 2.9)

plot_box(ax3, lw_filter_list_os['VQF-6D']['t3'], 3.2, '#82A7A6', box_width, 0.8, side = 'left')
plot_density(ax3, lw_filter_list_os['VQF-6D']['t3'], 3.2 - box_width/2, '#82A7A6', scale*20, covf, side = 'left')
plot_data_point(ax3, lw_filter_list_os['VQF-6D']['t3'], '#82A7A6', position = 3.1)
label_diff(ax3, 2.8, 3.2, lw_vqf6d_t3['p-val'].values[0], 0.05/3, height = 0.97, range = (0, 80), font_size = fontsize_stats, color = '#82A7A6')



ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['left'].set_position(('outward', 8))
ax3.spines['bottom'].set_position(('outward', 5))

ax3.set_ylabel('Overall RMSD ($^\circ$)', fontsize = fontsize_label)

# ax3.scatter(0.7, 74, color = '#82A7A6', edgecolor = 'none', alpha = 0.5, s = 47, marker = 's', zorder = 2)
# ax3.annotate('6D VQF', xy = (0.05, 0.95), xycoords = 'axes fraction', fontsize = 11, ha = 'left', va = 'top', color = '#82A7A6')


ax3.set_ylim([0, 80])
ax3.set_yticks([0, 20, 40, 60, 80])
ax3.set_xlim([0.5, 3.5])
ax3.set_xticks([0.5, 1, 2, 3, 3.5])
ax3.set_xticklabels(['', 'T1', 'T2', 'T3', ''])
ax3.text(2, -17, '(6D VQF)', ha='center', va='center', fontsize = fontsize_stats, color= '#82A7A6', transform=ax3.transData)  # Bottom row (blue)




plot_box(ax4, lw_filter_list['Xsens-9D']['t1'], 0.8, color_os, box_width, 0.5, side = 'right')
plot_density(ax4, lw_filter_list['Xsens-9D']['t1'], 0.8 + box_width/2, color_os, scale*5, covf, side = 'right')
plot_data_point(ax4, lw_filter_list['Xsens-9D']['t1'], color_os, position = 0.9)

plot_box(ax4, lw_filter_list_os['Xsens-9D']['t1'], 1.2, color_os, box_width, 0.8, side = 'left')
plot_density(ax4, lw_filter_list_os['Xsens-9D']['t1'], 1.2 - box_width/2, color_os, scale*5, covf, side = 'left')
plot_data_point(ax4, lw_filter_list_os['Xsens-9D']['t1'], color_os, position = 1.1)
label_diff(ax4, 0.8, 1.2, lw_xsens9d_t1['p-val'].values[0], 0.05/3, height = 0.45, range = (0, 40), font_size = fontsize_stats, color = color_os)

plot_box(ax4, lw_filter_list['Xsens-9D']['t2'], 1.8, color_os, box_width, 0.5, side = 'right')
plot_density(ax4, lw_filter_list['Xsens-9D']['t2'], 1.8 + box_width/2, color_os, scale*5, covf, side = 'right')
plot_data_point(ax4, lw_filter_list['Xsens-9D']['t2'], color_os, position = 1.9)

plot_box(ax4, lw_filter_list_os['Xsens-9D']['t2'], 2.2, color_os, box_width, 0.8, side = 'left')
plot_density(ax4, lw_filter_list_os['Xsens-9D']['t2'], 2.2 - box_width/2, color_os, scale*5, covf, side = 'left')
plot_data_point(ax4, lw_filter_list_os['Xsens-9D']['t2'], color_os, position = 2.1)
label_diff(ax4, 1.8, 2.2, lw_xsens9d_t2['p-val'].values[0], 0.05/3, height = 0.75, range = (0, 40), font_size = fontsize_stats, color = color_os)

plot_box(ax4, lw_filter_list['Xsens-9D']['t3'], 2.8, color_os, box_width, 0.5, side = 'right')
plot_density(ax4, lw_filter_list['Xsens-9D']['t3'], 2.8 + box_width/2, color_os, scale*5, covf, side = 'right')
plot_data_point(ax4, lw_filter_list['Xsens-9D']['t3'], color_os, position = 2.9)

plot_box(ax4, lw_filter_list_os['Xsens-9D']['t3'], 3.2, color_os, box_width, 0.8, side = 'left')
plot_density(ax4, lw_filter_list_os['Xsens-9D']['t3'], 3.2 - box_width/2, color_os, scale*5, covf, side = 'left')
plot_data_point(ax4, lw_filter_list_os['Xsens-9D']['t3'], color_os, position = 3.1)
label_diff(ax4, 2.8, 3.2, lw_xsens9d_t3['p-val'].values[0], 0.05/3, height = 0.97, range = (0, 40), font_size = fontsize_stats, color = color_os)




# plot_box(ax4, lw_filter_list['Xsens-9D']['t1'], 1, color_os, box_width, 0.5, side = 'right')
# plot_density(ax4, lw_filter_list['Xsens-9D']['t1'], 1 + box_width/2, color_os, scale*5, covf, side = 'right')
# plot_data_point(ax4, lw_filter_list['Xsens-9D']['t1'], color_os, position = 1.25)

# plot_box(ax4, lw_filter_list['Xsens-9D']['t2'], 2, color_os, box_width, 0.5, side = 'right')
# plot_density(ax4, lw_filter_list['Xsens-9D']['t2'], 2 + box_width/2, color_os, scale*5, covf, side = 'right')
# plot_data_point(ax4, lw_filter_list['Xsens-9D']['t2'], color_os, position = 2.25)

# plot_box(ax4, lw_filter_list['Xsens-9D']['t3'], 3, color_os, box_width, 0.5, side = 'right')
# plot_density(ax4, lw_filter_list['Xsens-9D']['t3'], 3 + box_width/2, color_os, scale*5, covf, side = 'right')
# plot_data_point(ax4, lw_filter_list['Xsens-9D']['t3'], color_os, position = 3.25)

ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['left'].set_position(('outward', 8))
ax4.spines['bottom'].set_position(('outward', 5))


ax4.set_ylim([0, 40])
ax4.set_yticks([0, 10, 20, 30, 40])
ax4.set_xlim([0.5, 3.5])
ax4.set_xticks([0.5, 1, 2, 3, 3.5])
ax4.set_xticklabels(['', 'T1', 'T2', 'T3', ''])
ax4.text(2, -17/2, '(9D XKF)', ha='center', va='center', fontsize = fontsize_stats, color= color_os, transform=ax4.transData)  # Bottom row (blue)







xsens9d_t1_median                  = np.median(lw_filter_list_chunk['Xsens-9D']['t1'], axis = 0)
xsens9d_t2_median                  = np.median(lw_filter_list_chunk['Xsens-9D']['t2'], axis = 0)
xsens9d_t3_median                  = np.median(lw_filter_list_chunk['Xsens-9D']['t3'], axis = 0)

xsens9d_os_t1_median               = np.median(lw_filter_list_os_chunk['Xsens-9D']['t1'], axis = 0)
xsens9d_os_t2_median               = np.median(lw_filter_list_os_chunk['Xsens-9D']['t2'], axis = 0)
xsens9d_os_t3_median               = np.median(lw_filter_list_os_chunk['Xsens-9D']['t3'], axis = 0)

vqf6d_t1_median                = np.median(lw_filter_list_chunk['VQF-6D']['t1'], axis = 0)
vqf6d_t2_median                = np.median(lw_filter_list_chunk['VQF-6D']['t2'], axis = 0)
vqf6d_t3_median                = np.median(lw_filter_list_chunk['VQF-6D']['t3'], axis = 0)

vqf6d_os_t1_median             = np.median(lw_filter_list_os_chunk['VQF-6D']['t1'], axis = 0)
vqf6d_os_t2_median             = np.median(lw_filter_list_os_chunk['VQF-6D']['t2'], axis = 0)
vqf6d_os_t3_median             = np.median(lw_filter_list_os_chunk['VQF-6D']['t3'], axis = 0)


ax5.plot(t1_time, xsens9d_t1_median, color = color_os, linestyle = '--', linewidth = 1.5, label = '9D XKF', alpha = 0.5, zorder = 1)
ax5.plot(t2_time, xsens9d_t2_median, color = color_os, linestyle = '--', linewidth = 1.5, alpha = 0.8, zorder = 1)
ax5.plot(t3_time, xsens9d_t3_median, color = color_os, linestyle = '--', linewidth = 1.5, alpha = 0.8, zorder = 1)

ax5.plot(t1_time, xsens9d_os_t1_median, color = color_os, linestyle = '-', linewidth = 1.5, label = 'OpenSense', alpha = 0.8, zorder = 2)
ax5.plot(t2_time, xsens9d_os_t2_median, color = color_os, linestyle = '-', linewidth = 1.5, alpha = 0.8, zorder = 2)
ax5.plot(t3_time, xsens9d_os_t3_median, color = color_os, linestyle = '-', linewidth = 1.5, alpha = 0.8, zorder = 2)


ax5.plot(t1_time, vqf6d_t1_median, color = '#82A7A6', linestyle = '--', linewidth = 1.5, label = '6D VQF', alpha = 0.5, zorder = 3)
ax5.plot(t2_time, vqf6d_t2_median, color = '#82A7A6', linestyle = '--', linewidth = 1.5, alpha = 0.8, zorder = 3)
ax5.plot(t3_time, vqf6d_t3_median, color = '#82A7A6', linestyle = '--', linewidth = 1.5, alpha = 0.8, zorder = 3)

ax5.plot(t1_time, vqf6d_os_t1_median, color = '#82A7A6', linestyle = '-', linewidth = 1.5, label = 'OpenSense', alpha = 0.8, zorder = 4)
ax5.plot(t2_time, vqf6d_os_t2_median, color = '#82A7A6', linestyle = '-', linewidth = 1.5, alpha = 0.8, zorder = 4)
ax5.plot(t3_time, vqf6d_os_t3_median, color = '#82A7A6', linestyle = '-', linewidth = 1.5, alpha = 0.8, zorder = 4)


from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset, inset_axes

# axins = zoomed_inset_axes(ax4, zoom = 2.5, loc='upper left')  # zoom = 2.5x
axins = inset_axes(ax5, width="60%", height="60%", loc='upper left',
                   bbox_to_anchor=(0.08, 0.06, 0.25, 0.7),  # position relative to figure or axes
                   bbox_transform=ax5.transAxes,  # use the main axes' coordinate system
                   borderpad=0)
axins.plot(t1_time, xsens9d_t1_median, color = color_os, linestyle = '--', linewidth = 1.5, label = 'Xsens 9D', alpha = 0.5)
axins.plot(t2_time, xsens9d_t2_median, color = color_os, linestyle = '--', linewidth = 1.5, alpha = 0.5)
axins.plot(t3_time, xsens9d_t3_median, color = color_os, linestyle = '--', linewidth = 1.5, alpha = 0.5)
axins.plot(t1_time, xsens9d_os_t1_median, color = color_os, linewidth = 1.5, label = 'OpenSense', alpha = 0.8)
axins.plot(t2_time, xsens9d_os_t2_median, color = color_os, linewidth = 1.5, alpha = 0.8)
axins.plot(t3_time, xsens9d_os_t3_median, color = color_os, linewidth = 1.5, alpha = 0.8)
axins.plot(t1_time, vqf6d_t1_median, color = '#82A7A6', linestyle = '--', linewidth = 1.5, label = 'VQF 6D', alpha = 0.5)
axins.plot(t2_time, vqf6d_t2_median, color = '#82A7A6', linestyle = '--', linewidth = 1.5, alpha = 0.5)
axins.plot(t3_time, vqf6d_t3_median, color = '#82A7A6', linestyle = '--', linewidth = 1.5, alpha = 0.5)
axins.plot(t1_time, vqf6d_os_t1_median, color = '#82A7A6', linewidth = 1.5, alpha = 0.8)
axins.plot(t2_time, vqf6d_os_t2_median, color = '#82A7A6', linewidth = 1.5, alpha = 0.8)
axins.plot(t3_time, vqf6d_os_t3_median, color = '#82A7A6', linewidth = 1.5, alpha = 0.8)

axins.patch.set_facecolor('none')
# color_mt = '#6B4E71'

axins.set_xlim([0.5, 4])
axins.set_ylim([0.5, 15])

# mark_inset(ax4, axins, loc1=2, loc2=4, fc = 'lightgray', ec = 'none', alpha = 0.4, zorder = 0)
mark_inset(ax5, axins, loc1=2, loc2=4, fc = 'none', ec = '#320E3B', linestyle = 'dashed', alpha = 0.3, zorder = 0)

axins.spines['top'].set_visible(False)
axins.spines['right'].set_visible(False)


ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.spines['left'].set_position(('outward', 8))
ax5.spines['bottom'].set_position(('outward', 5))

ax5.set_ylabel('Overall RMSD ($^\circ$)', fontsize = fontsize_label)

ax5.set_ylim([0, 80])
ax5.set_yticks([0, 20, 40, 60, 80])
ax5.set_xlim([0, 40])
ax5.set_xticks([0, 5, 10, 12.5, 15, 20, 25, 27.5, 30, 35, 40])
ax5.set_xticklabels(['0', '5', '10', '...', '30', '35', '40', '...', '60', '65', '70'])
ax5.set_xlabel('Time (minute)', fontsize = fontsize_label)

ax5.annotate('T1 Walking', xy = (1, 75), xytext = (1, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax5.annotate(r'(0$^{th}$-10$^{th}$ min)', xy = (1, 75), xytext = (1, 70), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

ax5.annotate('T2 Walking', xy = (16, 75), xytext = (16, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax5.annotate(r'(30$^{th}$-40$^{th}$ min)', xy = (16, 75), xytext = (16, 70), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')

ax5.annotate('T3 Walking', xy = (31, 75), xytext = (31, 76), ha = 'left', va = 'center', fontsize = 11, color = 'k')
ax5.annotate(r'(60$^{th}$-70$^{th}$ min)', xy = (31, 75), xytext = (31, 70), ha = 'left', va = 'center', fontsize = fontsize_stats, color = '#7D7C84')





# plt.savefig('imu_benchmark/plot/benchmark_f3.svg')
plt.savefig('imu_benchmark/plot/benchmark_f3_part2.svg')

plt.show()






