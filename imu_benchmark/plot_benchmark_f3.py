# name: plot_benchmark_f2.py
# description: plot figure 2 of the benchmark IMU paper
# author: Vu Phan
# date: 2025/02/25



import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import norm, gaussian_kde

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


# --- Obtain overall RMSD --- #
filter_list = {'Xsens-9D': None, 'VQF-9D': None, 'EKF-9D': None, 'MAD-9D': None, 'MAH-9D': None, 'VQF-6D': None, 'EKF-6D': None, 'MAD-6D': None, 'MAH-6D': None, 'RIANN-6D': None}
runtime_list = {'Xsens-9D': None, 'VQF-9D': None, 'EKF-9D': None, 'MAD-9D': None, 'MAH-9D': None, 'VQF-6D': None, 'EKF-6D': None, 'MAD-6D': None, 'MAH-6D': None, 'RIANN-6D': None}

reference = '_direct'
title_alignment = '_alignment'
# reference = '_opensim'

for filter_info in filter_list.keys():
    f_type, dim = filter_info.split('-')

    print('*** Filter ' + f_type + ' ' + dim)

    subject_val = []
    subject_rt_val = []

    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []
        task_rt_val = []

        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:
            if subject == 21 and task == 'treadmill_running':
                continue 

            filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + '.pkl'
            ja_mt = eval_utils.load_data(filename_mt)

            filename_rt_mt = constant_common.OUT_MT_RUN_TIME_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '.pkl'
            rt_mt = eval_utils.load_data(filename_rt_mt)

            joint_val = []

            # if subject == 18:
            #     breakpoint()

            for joint in ja_mt.keys():
                if task == 'treadmill_walking' or task == 'treadmill_running':
                    if '_l' in joint:
                        continue

                joint_val.append(ja_mt[joint])

            for rt in rt_mt.values():
                task_rt_val.append(rt*1e6)

            task_val.append(np.nanmean(joint_val))

        subject_val.append(np.nanmean(task_val))
        subject_rt_val.append(np.nanmean(task_rt_val))
    
    filter_list[filter_info] = np.array(subject_val)
    runtime_list[filter_info] = np.array(subject_rt_val)


# --- Stats --- #
import pingouin as pg
import pandas as pd

print('*** Stats ***')
# Normality test
print('# Normality test')
print(pg.normality(pd.DataFrame(filter_list)))
print()
# Friedman test to see effects of filters on RMSD
print('# Friedman test')
print(pg.friedman(pd.DataFrame(filter_list)))
print()
# Post-hoc test with Wilcoxon signed-rank test
print('# Comparisons with Xsens-9D')
print('Median values:')
print(np.median(filter_list['Xsens-9D']))
print('Xsens-9D Q1: ' + str(np.percentile(filter_list['Xsens-9D'], 25)))
print('Xsens-9D Q3: ' + str(np.percentile(filter_list['Xsens-9D'], 75)))
print(np.median(filter_list['VQF-9D']))
print('VQF-9D Q1: ' + str(np.percentile(filter_list['VQF-9D'], 25)))
print('VQF-9D Q3: ' + str(np.percentile(filter_list['VQF-9D'], 75)))
# xsens_vs_vqf9d   = pg.wilcoxon(filter_list['Xsens-9D'], filter_list['VQF-9D'])
# xsens_vs_ekf9d   = pg.wilcoxon(filter_list['Xsens-9D'], filter_list['EKF-9D'])
# xsens_vs_mad9d   = pg.wilcoxon(filter_list['Xsens-9D'], filter_list['MAD-9D'])
# xsens_vs_mah9d   = pg.wilcoxon(filter_list['Xsens-9D'], filter_list['MAH-9D'])
# xsens_vs_riann6d = pg.wilcoxon(filter_list['Xsens-9D'], filter_list['RIANN-6D'])

vqf9d_vs_xsens   = pg.wilcoxon(filter_list['VQF-9D'], filter_list['Xsens-9D'])
vqf9d_vs_ekf9d   = pg.wilcoxon(filter_list['VQF-9D'], filter_list['EKF-9D'])
vqf9d_vs_mad9d   = pg.wilcoxon(filter_list['VQF-9D'], filter_list['MAD-9D'])
vqf9d_vs_mah9d   = pg.wilcoxon(filter_list['VQF-9D'], filter_list['MAH-9D'])
vqf9d_vs_riann6d = pg.wilcoxon(filter_list['VQF-9D'], filter_list['RIANN-6D'])

# print('Xsens vs. VQF-9D: ' + str(xsens_vs_vqf9d['p-val'].iloc[0]))
# print('Xsens vs. EKF-9D: ' + str(xsens_vs_ekf9d['p-val'].iloc[0]))
# print('Xsens vs. MAD-9D: ' + str(xsens_vs_mad9d['p-val'].iloc[0]))
# print('Xsens vs. MAH-9D: ' + str(xsens_vs_mah9d['p-val'].iloc[0]))
# print('Xsens vs. RIANN-6D: ' + str(xsens_vs_riann6d['p-val'].iloc[0]))

print('VQF-9D vs. Xsens: ' + str(vqf9d_vs_xsens['p-val'].iloc[0]))
print('difference with Xsens-9D: ' + str(np.median(filter_list['VQF-9D'] - filter_list['Xsens-9D'])))
print('VQF-9D vs. EKF-9D: ' + str(vqf9d_vs_ekf9d['p-val'].iloc[0]))
print('difference with EKF-9D: ' + str(np.median(filter_list['VQF-9D'] - filter_list['EKF-9D'])))
print('difference Q1: ' + str(np.percentile(filter_list['VQF-9D'] - filter_list['EKF-9D'], 25)))
print('difference Q3: ' + str(np.percentile(filter_list['VQF-9D'] - filter_list['EKF-9D'], 75)))
print('VQF-9D vs. MAD-9D: ' + str(vqf9d_vs_mad9d['p-val'].iloc[0]))
print('difference with MAD-9D: ' + str(np.median(filter_list['VQF-9D'] - filter_list['MAD-9D'])))
print('VQF-9D vs. MAH-9D: ' + str(vqf9d_vs_mah9d['p-val'].iloc[0]))
print('difference with MAH-9D: ' + str(np.median(filter_list['VQF-9D'] - filter_list['MAH-9D'])))
print('VQF-9D vs. RIANN-6D: ' + str(vqf9d_vs_riann6d['p-val'].iloc[0]))
print('difference with RIANN-6D: ' + str(np.median(filter_list['VQF-9D'] - filter_list['RIANN-6D'])))
print('difference Q1: ' + str(np.percentile(filter_list['VQF-9D'] - filter_list['RIANN-6D'], 25)))
print('difference Q3: ' + str(np.percentile(filter_list['VQF-9D'] - filter_list['RIANN-6D'], 75)))
print()

# print('difference with Xsens' + str(np.median(filter_list['Xsens-9D']) - np.median(filter_list['VQF-9D'])))
# print('difference with Xsens' + str(np.median(filter_list['Xsens-9D']) - np.median(filter_list['EKF-9D'])))
# print('difference with Xsens' + str(np.median(filter_list['Xsens-9D']) - np.median(filter_list['MAD-9D'])))
# print('difference with Xsens' + str(np.median(filter_list['Xsens-9D']) - np.median(filter_list['MAH-9D'])))
# print('difference with Xsens' + str(np.median(filter_list['Xsens-9D']) - np.median(filter_list['RIANN-6D'])))



print()
print('# Comparisons between 9D and 6D')
vqf9d_vs_vqf6d   = pg.wilcoxon(filter_list['VQF-9D'], filter_list['VQF-6D'])
ekf9d_vs_ekf6d   = pg.wilcoxon(filter_list['EKF-9D'], filter_list['EKF-6D'])
mad9d_vs_mad6d   = pg.wilcoxon(filter_list['MAD-9D'], filter_list['MAD-6D'])
mah9d_vs_mah6d   = pg.wilcoxon(filter_list['MAH-9D'], filter_list['MAH-6D'])
print('VQF-9D vs. VQF-6D: ' + str(vqf9d_vs_vqf6d['p-val'].iloc[0]))
print('EKF-9D vs. EKF-6D: ' + str(ekf9d_vs_ekf6d['p-val'].iloc[0]))
print('MAD-9D vs. MAD-6D: ' + str(mad9d_vs_mad6d['p-val'].iloc[0]))
print('MAH-9D vs. MAH-6D: ' + str(mah9d_vs_mah6d['p-val'].iloc[0]))



# bonferroni correction of p-value for statistical significance
alpha = 0.05
# n_filter_comparison = 9 # VQF with 9 other filters 
n_filter_comparison = 15
# n = 10 # we have an additional correlation test
alpha_bonf = alpha/n_filter_comparison
print()
print('alpha_bonf for filter comparison = ' + str(alpha_bonf))


print(np.median(filter_list['Xsens-9D']))
print(np.median(filter_list['VQF-9D']))

print('VQF-9D = ' + str(np.median(filter_list['VQF-9D'])) + ' vs. VQF-6D = ' + str(np.median(filter_list['VQF-6D'])))
print('-> difference = ' + str(np.median(filter_list['VQF-9D'] - filter_list['VQF-6D'])))
print('VQF-6D Q1: ' + str(np.percentile(filter_list['VQF-6D'], 25)))
print('VQF-6D Q3: ' + str(np.percentile(filter_list['VQF-6D'], 75)))
print('VQF-9D Q1: ' + str(np.percentile(filter_list['VQF-9D'], 25)))
print('VQF-9D Q3: ' + str(np.percentile(filter_list['VQF-9D'], 75)))
print('EKF-9D = ' + str(np.median(filter_list['EKF-9D'])) + ' vs. EKF-6D = ' + str(np.median(filter_list['EKF-6D'])))
print('-> difference = ' + str(np.median(filter_list['EKF-9D'] - filter_list['EKF-6D'])))
print('MAD-9D = ' + str(np.median(filter_list['MAD-9D'])) + ' vs. MAD-6D = ' + str(np.median(filter_list['MAD-6D'])))
print('-> difference = ' + str(np.median(filter_list['MAD-9D'] - filter_list['MAD-6D'])))
print('MAH-9D = ' + str(np.median(filter_list['MAH-9D'])) + ' vs. MAH-6D = ' + str(np.median(filter_list['MAH-6D'])))
print('-> difference = ' + str(np.median(filter_list['MAH-9D'] - filter_list['MAH-6D'])))


# --- Plot --- #
np.random.seed(0)
box_width = 0.2
scale = 1.3
covf = 0.7

font_size = 11
fontsize_label = 13
fontsize_stats = 10

plt.rcParams.update({'font.size': font_size})
fig = plt.figure(figsize=(10, 7.5))
gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1], width_ratios=[0.43, 0.57])

# add more space between the first and second rows
gs.update(hspace = 0.45, wspace = 0.2)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, :])

# Comparison with VQF-9D
color_similarity = "#6B4E71"
color_difference = "#414535"
plot_box(ax1, data = filter_list['Xsens-9D'], position = 1, color = color_similarity, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = filter_list['Xsens-9D'], color = color_similarity, position = 1.25)
plot_density(ax1, data = filter_list['Xsens-9D'], position = 1 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')

plot_box(ax1, data = filter_list['VQF-9D'], position = 2, color = color_similarity, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = filter_list['VQF-9D'], color = color_similarity, position = 2.25)
plot_density(ax1, data = filter_list['VQF-9D'], position = 2 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')
# label_diff(ax1, 1, 2, xsens_vs_vqf9d['p-val'].iloc[0], alpha_bonf, height = 0.1, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')
label_diff(ax1, 1, 2, vqf9d_vs_xsens['p-val'].iloc[0], alpha_bonf, height = 0.1, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

plot_box(ax1, data = filter_list['EKF-9D'], position = 3, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = filter_list['EKF-9D'], color = color_difference, position = 3.25)
plot_density(ax1, data = filter_list['EKF-9D'], position = 3 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')
# label_diff(ax1, 1, 3, xsens_vs_ekf9d['p-val'].iloc[0], alpha_bonf, height = 0.75, font_size = fontsize_stats, color = color_difference)
label_diff(ax1, 2, 3, vqf9d_vs_ekf9d['p-val'].iloc[0], alpha_bonf, height = 0.75, font_size = fontsize_stats, color = color_difference)

plot_box(ax1, data = filter_list['MAD-9D'], position = 4, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = filter_list['MAD-9D'], color = color_difference, position = 4.25)
plot_density(ax1, data = filter_list['MAD-9D'], position = 4 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')
# label_diff(ax1, 1, 4, xsens_vs_mad9d['p-val'].iloc[0], alpha_bonf, height = 0.83, font_size = fontsize_stats, color = color_difference)
label_diff(ax1, 2, 4, vqf9d_vs_mad9d['p-val'].iloc[0], alpha_bonf, height = 0.83, font_size = fontsize_stats, color = color_difference)

plot_box(ax1, data = filter_list['MAH-9D'], position = 5, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = filter_list['MAH-9D'], color = color_difference, position = 5.25)
plot_density(ax1, data = filter_list['MAH-9D'], position = 5 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')
# label_diff(ax1, 1, 5, xsens_vs_mah9d['p-val'].iloc[0], alpha_bonf, height = 0.91, font_size = fontsize_stats, color = color_difference)
label_diff(ax1, 2, 5, vqf9d_vs_mah9d['p-val'].iloc[0], alpha_bonf, height = 0.91, font_size = fontsize_stats, color = color_difference)

plot_box(ax1, data = filter_list['RIANN-6D'], position = 6, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = filter_list['RIANN-6D'], color = color_difference, position = 6.25)
plot_density(ax1, data = filter_list['RIANN-6D'], position = 6 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')
# label_diff(ax1, 1, 6, xsens_vs_riann6d['p-val'].iloc[0], alpha_bonf, height = 0.99, font_size = fontsize_stats, color = color_difference)
label_diff(ax1, 2, 6, vqf9d_vs_riann6d['p-val'].iloc[0], alpha_bonf, height = 0.99, font_size = fontsize_stats, color = color_difference)

# ax1.fill_between([0.5, 6.5], 0, 5, color = 'lightgray', facecolor = 'white', hatch = '///', alpha = 0.5, edgecolor = None, zorder = 0)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_position(('outward', 8))
ax1.spines['bottom'].set_position(('outward', 5))

ax1.set_xlim([0.5, 6.5])
ax1.set_xticks([0.5, 1, 2, 3, 4, 5, 6, 6.5])
# ax1.set_xticklabels(['', 'XKF\n(9D)', 'VQF', 'EKF', 'MAD', 'MAH', 'RIANN', ''])
ax1.set_xticklabels([])
tick_positions = [0.5, 1, 2, 3, 4, 5, 6, 6.5]
labels_top = ['', 'XKF', 'VQF', 'EKF', 'MAD', 'MAH', 'RIANN', '']
labels_bottom = ['', '(9D)', '(9D)', '(9D)', '(9D)', '(9D)', '(6D)', '']

for i, (top, bottom) in enumerate(zip(labels_top, labels_bottom)):
    ax1.text(tick_positions[i], -1.9, top, ha='center', va='center', fontsize = font_size, color='k', transform=ax1.transData)  # Top row (red)
    ax1.text(tick_positions[i], -3, bottom, ha='center', va='center', fontsize = fontsize_stats, color='gray', transform=ax1.transData)  # Bottom row (blue)

ax1.set_ylim(0, 15)
ax1.set_yticks([0, 5, 10, 15])
ax1.set_ylabel(r'Overall RMSD $(^{\circ})$', fontsize = fontsize_label)


# Comparison between 9D and 6D
plot_box(ax2, data = filter_list['VQF-9D'], position = 1, color = color_similarity, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax2, data = filter_list['VQF-9D'], color = color_similarity, position = 1.25)
plot_density(ax2, data = filter_list['VQF-9D'], position = 1 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')

plot_box(ax2, data = filter_list['VQF-6D'], position = 2, color = color_similarity, width = box_width, alpha = 0.5, side = 'left')
plot_data_point(ax2, data = filter_list['VQF-6D'], color = color_similarity, position = 1.75)
plot_density(ax2, data = filter_list['VQF-6D'], position = 2 - box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'left')
label_diff(ax2, 1, 2, vqf9d_vs_vqf6d['p-val'].iloc[0], alpha_bonf, height = 0.1, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

plot_box(ax2, data = filter_list['EKF-9D'], position = 3, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax2, data = filter_list['EKF-9D'], color = color_difference, position = 3.25)
plot_density(ax2, data = filter_list['EKF-9D'], position = 3 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')

plot_box(ax2, data = filter_list['EKF-6D'], position = 4, color = color_difference, width = box_width, alpha = 0.5, side = 'left')
plot_data_point(ax2, data = filter_list['EKF-6D'], color = color_difference, position = 3.75)
plot_density(ax2, data = filter_list['EKF-6D'], position = 4 - box_width/2, color = color_difference, scale = scale, covf = covf, side = 'left')
label_diff(ax2, 3, 4, ekf9d_vs_ekf6d['p-val'].iloc[0], alpha_bonf, height = 0.99, font_size = fontsize_stats, color = color_difference)

plot_box(ax2, data = filter_list['MAD-9D'], position = 5, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax2, data = filter_list['MAD-9D'], color = color_difference, position = 5.25)
plot_density(ax2, data = filter_list['MAD-9D'], position = 5 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')

plot_box(ax2, data = filter_list['MAD-6D'], position = 6, color = color_difference, width = box_width, alpha = 0.5, side = 'left')
plot_data_point(ax2, data = filter_list['MAD-6D'], color = color_difference, position = 5.75)
plot_density(ax2, data = filter_list['MAD-6D'], position = 6 - box_width/2, color = color_difference, scale = scale, covf = covf, side = 'left')
label_diff(ax2, 5, 6, mad9d_vs_mad6d['p-val'].iloc[0], alpha_bonf, height = 0.99, font_size = fontsize_stats, color = color_difference)

plot_box(ax2, data = filter_list['MAH-9D'], position = 7, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax2, data = filter_list['MAH-9D'], color = color_difference, position = 7.25)
plot_density(ax2, data = filter_list['MAH-9D'], position = 7 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')

plot_box(ax2, data = filter_list['MAH-6D'], position = 8, color = color_difference, width = box_width, alpha = 0.5, side = 'left')
plot_data_point(ax2, data = filter_list['MAH-6D'], color = color_difference, position = 7.75)
plot_density(ax2, data = filter_list['MAH-6D'], position = 8 - box_width/2, color = color_difference, scale = scale, covf = covf, side = 'left')
label_diff(ax2, 7, 8, mah9d_vs_mah6d['p-val'].iloc[0], alpha_bonf, height = 0.99, font_size = fontsize_stats, color = color_difference)



ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_position(('outward', 8))
ax2.spines['bottom'].set_position(('outward', 5))

ax2.set_xlim([0.5, 8.5])
ax2.set_xticks([0.5, 1, 2, 3, 4, 5, 6, 7, 8, 8.5])
ax2.set_xticklabels([])
tick_positions_top = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 8.5]
tick_positions_bottom = [1.5, 3.5, 5.5, 7.5]
labels_top = ['', '9D', '6D', '9D', '6D', '9D', '6D', '9D', '6D', '']
labels_bottom = ['(VQF)', '(EKF)', '(MAD)', '(MAH)']

for i, top in enumerate(labels_top):
    ax2.text(tick_positions_top[i], -1.9, top, ha='center', va='center', fontsize = font_size, color='gray', transform=ax2.transData)  # Top row (red)

for i, bottom in enumerate(labels_bottom):
    ax2.text(tick_positions_bottom[i], -3, bottom, ha='center', va='center', fontsize = fontsize_stats, color='k', transform=ax2.transData)  # Bottom row (blue)

ax2.set_ylim(0, 15)
ax2.set_yticks([0, 5, 10, 15])
ax2.set_yticklabels([])


# Correlation between accuracy and wall time
rmsd_list = []
rmsd_runtime_list = []

for filter_info in filter_list.keys():
    if 'Xsens' in filter_info:
        pass 
    else:
        if 'VQF' in filter_info:
            selected_color = color_similarity
        else:
            selected_color = color_difference

        # ax.scatter(runtime_list[filter_info].mean(), filter_list[filter_info].mean(), color = selected_color, label = filter_info)
        # if filter_info == 'EKF-6D':
        if filter_info == 'EKF-D': # include 6D
            pass
        else:
            # ax3.errorbar(runtime_list[filter_info].mean(), filter_list[filter_info].mean(), xerr = runtime_list[filter_info].std(), yerr = filter_list[filter_info].std(), fmt = 'o', color = selected_color, capsize = 2, capthick = 1, elinewidth = 1, alpha = 0.9)
            Q1_rmsd = np.percentile(filter_list[filter_info], 25)
            Q2_rmsd = np.percentile(filter_list[filter_info], 50)
            Q3_rmsd = np.percentile(filter_list[filter_info], 75)
            IQR_rmsd = Q3_rmsd - Q1_rmsd
            lower_whisker_rmsd = max(min(filter_list[filter_info]), Q1_rmsd - 1.5*IQR_rmsd)
            upper_whisker_rmsd = min(max(filter_list[filter_info]), Q3_rmsd + 1.5*IQR_rmsd)
            Q1_runtime = np.percentile(runtime_list[filter_info], 25)
            Q2_runtime = np.percentile(runtime_list[filter_info], 50)
            Q3_runtime = np.percentile(runtime_list[filter_info], 75)
            IQR_runtime = Q3_runtime - Q1_runtime
            lower_whisker_runtime = max(min(runtime_list[filter_info]), Q1_runtime - 1.5*IQR_runtime)
            upper_whisker_runtime = min(max(runtime_list[filter_info]), Q3_runtime + 1.5*IQR_runtime)
            ax3.errorbar(np.median(runtime_list[filter_info]), np.median(filter_list[filter_info]), 
                         xerr = [[Q2_runtime - lower_whisker_runtime], 
                                 [upper_whisker_runtime - Q2_runtime]], 
                         yerr = [[Q2_rmsd - lower_whisker_rmsd], 
                                 [upper_whisker_rmsd - Q2_rmsd]], 
                         fmt = 'o', color = selected_color, ecolor = 'k', capsize = 0.5, capthick = 0.5, elinewidth = 1, alpha = 0.5)
            ax3.scatter(runtime_list[filter_info], filter_list[filter_info], color = 'lightgray', s = 25, marker = '.', edgecolor = 'none', alpha = 0.5)
            if filter_info == 'EKF-9D':
                offset = 0.5
            elif filter_info == 'RIANN-6D':
                offset = 2
            elif filter_info == 'MAD-6D':
                offset = -3
            elif filter_info == 'MAH-6D':
                offset = 1.5
            else:
                offset = -1.5
            ax3.text(runtime_list[filter_info].mean() + 2, filter_list[filter_info].mean() + offset, filter_info, fontsize = 10, color = selected_color)

        # if filter_info == 'EKF-6D':
        if filter_info == 'EKF-D': # include 6D
            pass 
        else:
            rmsd_list.append(filter_list[filter_info].mean())
            rmsd_runtime_list.append(runtime_list[filter_info].mean())


from scipy.stats import spearmanr

from scipy.optimize import curve_fit

def f(x, A, B):
    return A*x + B

u_popt, _ = curve_fit(f, rmsd_runtime_list, rmsd_list)

# xline = np.linspace(0.8, 1.8, 100)
xline = np.linspace(20, 220, 100)
yline = f(xline, u_popt[0], u_popt[1])

ax3.plot(xline, yline, color = 'lightgray', linewidth = 6, linestyle = '--', alpha = 0.8, zorder = 0)

print('*** Correlation ***')
print('Spearman: ' + str(spearmanr(rmsd_runtime_list, rmsd_list)))
# print('Run time of most vs. least accurate filter: ' + str(np.max(rmsd_runtime_list) - np.min(rmsd_runtime_list)))
print(rmsd_runtime_list)
print(rmsd_list)
print('Run time VQF-9D compared to RIANN-6D: ' + str(rmsd_runtime_list[1] - rmsd_runtime_list[-1]))
# breakpoint()
# ax3.annotate(r'$R$ = ' + str(round(spearmanr(rmsd_runtime_list, rmsd_list)[0], 2)) + r'($*$)', xy = (0.85, 0.9), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'left', va = 'top')
ax3.annotate(r"Spearman's $\rho$ = " + str(round(spearmanr(rmsd_runtime_list, rmsd_list)[0], 2)), xy = (0.95, 0.95), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top')
ax3.annotate(r'$p$ = ' + str(round(spearmanr(rmsd_runtime_list, rmsd_list)[1], 2)), xy = (0.95, 0.87), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top', alpha = 0.7)

ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['left'].set_position(('outward', 8))
ax3.spines['bottom'].set_position(('outward', 5))

ax3.set_xlim([20, 180])
ax3.set_xticks([20, 40, 60, 80, 100, 120, 140, 160, 180])
ax3.set_xlabel(r'Wall time $(\mu s)$', fontsize = fontsize_label)

ax3.set_ylim(0, 15)
ax3.set_yticks([0, 5, 10, 15])
ax3.set_ylabel(r'Overall RMSD $(^{\circ})$', fontsize = fontsize_label)


plt.savefig('imu_benchmark/plot/benchmark_f2.svg')

plt.show()










