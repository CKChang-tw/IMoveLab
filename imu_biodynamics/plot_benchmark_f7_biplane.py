# name: plot_benchmark_f7_biplane.py


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import pickle
from scipy.stats import shapiro, wilcoxon
import pingouin as pg

from constants import constant_common, constant_meta
from utils.visualization import plot_utils


def get_rmsd_data(filter_type, dim, dataset):
    mc10_rmsd_arr  = {'flexion': [], 'adduction': [], 'rotation': [], 'overall': []}
    mocap_rmsd_arr = {'flexion': [], 'adduction': [], 'rotation': [], 'overall': []}
    mc10_vs_mocap  = {'flexion': [], 'adduction': [], 'rotation': [], 'overall': []}

    # # side = 'r'
    # side = 'l'
    for subject in constant_common.HA_SUBJECT_LIST:
    # for subject in [1, 2, 3, 4, 5, 6, 9, 10, 12, 13, 14, 15]:

        mc10_row          = {'flexion': [], 'adduction': [], 'rotation': [], 'overall': []}
        mocap_row         = {'flexion': [], 'adduction': [], 'rotation': [], 'overall': []}
        mc10_vs_mocap_row = {'flexion': [], 'adduction': [], 'rotation': [], 'overall': []}
        # for task in list(constant_common.HA_TASK_MAPPING.keys())[1::]:
        for side in ['r', 'l']:

            # for task in ['run']:
            # for task in ['shop']:
            # for task in ['sdrop']:
            # for task in ['ddrop']:
            for task in list(constant_common.HA_TASK_MAPPING.keys())[1::]:

                for trial in range(3):

                    if constant_meta.VALID_COMPARISON[str(subject)][task][side][trial]:
                        # row.append(constant_meta.VALID_COMPARISON[str(subject)][task][side][trial])
                        mc10_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/rmsd_mc10_biplane_{side}_{task}_{trial+1}.pkl'
                        # mc10_fn = f'outputs/{dataset}/eval/{subject}/rmsd_mc10_biplane_reset_{side}_{task}_{trial+1}.pkl' # for reset strategy (only for running)
                        with open(mc10_fn, 'rb') as f:
                            mc10_data = pickle.load(f)

                        mc10_row['flexion'].append(mc10_data['knee_flexion_' + side])
                        mc10_row['adduction'].append(mc10_data['knee_adduction_' + side])
                        mc10_row['rotation'].append(mc10_data['knee_rotation_' + side])
                        mc10_row['overall'] += [mc10_data['knee_flexion_' + side], mc10_data['knee_adduction_' + side], mc10_data['knee_rotation_' + side]]

                        mocap_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/rmsd_mocap_biplane_{side}_{task}_{trial+1}.pkl'
                        with open(mocap_fn, 'rb') as f:
                            mocap_data = pickle.load(f)

                        mocap_row['flexion'].append(mocap_data['knee_flexion_' + side])
                        mocap_row['adduction'].append(mocap_data['knee_adduction_' + side])
                        mocap_row['rotation'].append(mocap_data['knee_rotation_' + side])
                        mocap_row['overall'] += [mocap_data['knee_flexion_' + side], mocap_data['knee_adduction_' + side], mocap_data['knee_rotation_' + side]]

                        mc10_mocap_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/rmsd_mc10_mocap_{side}_{task}_{trial+1}.pkl'
                        with open(mc10_mocap_fn, 'rb') as f:
                            mc10_vs_mocap_data = pickle.load(f)

                        mc10_vs_mocap_row['flexion'].append(mc10_vs_mocap_data['knee_flexion_' + side])
                        mc10_vs_mocap_row['adduction'].append(mc10_vs_mocap_data['knee_adduction_' + side])
                        mc10_vs_mocap_row['rotation'].append(mc10_vs_mocap_data['knee_rotation_' + side])
                        mc10_vs_mocap_row['overall'] += [mc10_vs_mocap_data['knee_flexion_' + side], mc10_vs_mocap_data['knee_adduction_' + side], mc10_vs_mocap_data['knee_rotation_' + side]]

        mc10_rmsd_arr['flexion'].append(np.array(mc10_row['flexion']).mean())
        mc10_rmsd_arr['adduction'].append(np.array(mc10_row['adduction']).mean())
        mc10_rmsd_arr['rotation'].append(np.array(mc10_row['rotation']).mean())
        mc10_rmsd_arr['overall'].append(np.array(mc10_row['overall']).mean())

        mocap_rmsd_arr['flexion'].append(np.array(mocap_row['flexion']).mean())
        mocap_rmsd_arr['adduction'].append(np.array(mocap_row['adduction']).mean())
        mocap_rmsd_arr['rotation'].append(np.array(mocap_row['rotation']).mean())
        mocap_rmsd_arr['overall'].append(np.array(mocap_row['overall']).mean())

        mc10_vs_mocap['flexion'].append(np.array(mc10_vs_mocap_row['flexion']).mean())
        mc10_vs_mocap['adduction'].append(np.array(mc10_vs_mocap_row['adduction']).mean())
        mc10_vs_mocap['rotation'].append(np.array(mc10_vs_mocap_row['rotation']).mean())
        mc10_vs_mocap['overall'].append(np.array(mc10_vs_mocap_row['overall']).mean())

    return mc10_rmsd_arr, mocap_rmsd_arr, mc10_vs_mocap



dataset = 'HAKnee'

dim         = '6d'

vqf_rmsd_arr, mocap_rmsd_arr, _ = get_rmsd_data('vqf', dim, dataset)
ekf_rmsd_arr, _, _              = get_rmsd_data('ekf', dim, dataset)
mad_rmsd_arr, _, _              = get_rmsd_data('mad', dim, dataset)
mah_rmsd_arr, _, _              = get_rmsd_data('mah', dim, dataset)
riann_rmsd_arr, _, _            = get_rmsd_data('riann', dim, dataset)




# --- Stats --- #
# vqf vs. mocap
vqf_vs_mocap_overall   = pg.wilcoxon(vqf_rmsd_arr['overall'], mocap_rmsd_arr['overall'])
vqf_vs_mocap_flexion   = pg.wilcoxon(vqf_rmsd_arr['flexion'], mocap_rmsd_arr['flexion'])
vqf_vs_mocap_adduction = pg.wilcoxon(vqf_rmsd_arr['adduction'], mocap_rmsd_arr['adduction'])
vqf_vs_mocap_rotation  = pg.wilcoxon(vqf_rmsd_arr['rotation'], mocap_rmsd_arr['rotation'])

print('VQF vs. Mocap:')
print('VQF RMSD Overall:', np.median(vqf_rmsd_arr['overall']))
print(np.percentile(vqf_rmsd_arr['overall'], 25))
print(np.percentile(vqf_rmsd_arr['overall'], 75))
print('Mocap RMSD Overall:', np.median(mocap_rmsd_arr['overall']))
print(np.percentile(mocap_rmsd_arr['overall'], 25))
print(np.percentile(mocap_rmsd_arr['overall'], 75))
print()
print('VQF RMSD Adduction:', np.median(vqf_rmsd_arr['adduction']))
print(np.percentile(vqf_rmsd_arr['adduction'], 25))
print(np.percentile(vqf_rmsd_arr['adduction'], 75))
print('Mocap RMSD Adduction:', np.median(mocap_rmsd_arr['adduction']))
print(np.percentile(mocap_rmsd_arr['adduction'], 25))
print(np.percentile(mocap_rmsd_arr['adduction'], 75))
print()
print('VQF RMSD Flexion:', np.median(vqf_rmsd_arr['flexion']))
print('Mocap RMSD Flexion:', np.median(mocap_rmsd_arr['flexion']))
print()
print('VQF RMSD Rotation:', np.median(vqf_rmsd_arr['rotation']))
print('Mocap RMSD Rotation:', np.median(mocap_rmsd_arr['rotation']))
print('Overall:', vqf_vs_mocap_overall['p-val'].iloc[0])
print('Flexion:', vqf_vs_mocap_flexion['p-val'].iloc[0])
print('Adduction:', vqf_vs_mocap_adduction['p-val'].iloc[0])
print('Rotation:', vqf_vs_mocap_rotation['p-val'].iloc[0])
print()

# different filters
vqf_vs_ekf_overall   = pg.wilcoxon(vqf_rmsd_arr['overall'], ekf_rmsd_arr['overall'])
vqf_vs_mad_overall   = pg.wilcoxon(vqf_rmsd_arr['overall'], mad_rmsd_arr['overall'])
vqf_vs_mah_overall   = pg.wilcoxon(vqf_rmsd_arr['overall'], mah_rmsd_arr['overall'])
vqf_vs_riann_overall = pg.wilcoxon(vqf_rmsd_arr['overall'], riann_rmsd_arr['overall'])

print('VQF vs. other filters:')
print('EKF Overall:', vqf_vs_ekf_overall['p-val'].iloc[0])
print('MAD Overall:', vqf_vs_mad_overall['p-val'].iloc[0])
print('MAD RMSD Overall:', np.median(mad_rmsd_arr['overall']))
print(np.median(np.array(vqf_rmsd_arr['overall']) - np.array(mad_rmsd_arr['overall'])))
print('MAH Overall:', vqf_vs_mah_overall['p-val'].iloc[0])
print('MAH RMSD Overall:', np.median(mah_rmsd_arr['overall']))
print(np.median(np.array(vqf_rmsd_arr['overall']) - np.array(mah_rmsd_arr['overall'])))
print('RIANN Overall:', vqf_vs_riann_overall['p-val'].iloc[0])
print()

# --- Post hoc ---#
print('Mean of differences:' + str(np.mean(np.array(vqf_rmsd_arr['overall']) - np.array(mocap_rmsd_arr['overall']))))
print('Std of differences:' + str(np.std(np.array(vqf_rmsd_arr['overall']) - np.array(mocap_rmsd_arr['overall']))))



# --- Plotting --- #
np.random.seed(0)
box_width = 0.23
scale = 1.7
covf = 0.7

font_size = 11
fontsize_label = 13
fontsize_stats = 10

color_similarity = "#6B4E71"
color_difference = "#414535"
color_mocap      = '#7E7F9A'
# color_mocap      = 'gray'

plt.rcParams.update({'font.size': font_size})
fig = plt.figure(figsize=(10, 4))
gs = gridspec.GridSpec(1, 3, height_ratios=[1], width_ratios=[0.15, 0.45, 0.4])

gs.update(hspace = 0.3, wspace = 0.17)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])


# Overall comparison between VQF and Mocap
plot_utils.plot_box(ax1, vqf_rmsd_arr['overall'], position = 1, color = color_similarity, width = box_width, alpha = 0.8, side = 'right')
plot_utils.plot_data_point(ax1, vqf_rmsd_arr['overall'], color = color_similarity, position = 1.25)
plot_utils.plot_density(ax1, vqf_rmsd_arr['overall'], position = 1 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')

plot_utils.plot_box(ax1, mocap_rmsd_arr['overall'], position = 2, color = color_mocap, width = box_width, alpha = 0.6, side = 'left')
plot_utils.plot_data_point(ax1, mocap_rmsd_arr['overall'], color = color_mocap, position = 1.75)
plot_utils.plot_density(ax1, mocap_rmsd_arr['overall'], position = 2 - box_width/2, color = color_mocap, scale = scale, covf = covf, side = 'left')
plot_utils.label_diff(ax1, 1, 2, vqf_vs_mocap_overall['p-val'].iloc[0], 0.05/4, height = 0.08, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

# ax1.set_ylim([0, 15])
# ax1.set_yticks([0, 5, 10, 15])
ax1.set_ylim([0, 16])
ax1.set_yticks([0, 4, 8, 12, 16])

ax1.set_xlim([0.5, 2.5])
# ax1.set_xticks([0.5, 1, 2, 2.5])
# ax1.set_xticklabels(['', 'VQF', 'Mocap', ''])
ax1.set_xticks([0.5, 1.5, 2.5])
ax1.set_xticklabels(['', 'Overall', ''])

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_position(('outward', 8))
ax1.spines['bottom'].set_position(('outward', 5))

ax1.set_ylabel(r'RMSD $(^{\circ})$', fontsize = fontsize_label)


# Detailed DoFs comparison between VQF and Mocap
plot_utils.plot_box(ax2, vqf_rmsd_arr['flexion'], position = 1, color = color_similarity, width = box_width, alpha = 0.8, side = 'right')
plot_utils.plot_data_point(ax2, vqf_rmsd_arr['flexion'], color = color_similarity, position = 1.25)
plot_utils.plot_density(ax2, vqf_rmsd_arr['flexion'], position = 1 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')

plot_utils.plot_box(ax2, mocap_rmsd_arr['flexion'], position = 2, color = color_mocap, width = box_width, alpha = 0.6, side = 'left')
plot_utils.plot_data_point(ax2, mocap_rmsd_arr['flexion'], color = color_mocap, position = 1.75)
plot_utils.plot_density(ax2, mocap_rmsd_arr['flexion'], position = 2 - box_width/2, color = color_mocap, scale = scale, covf = covf, side = 'left')
plot_utils.label_diff(ax2, 1, 2, vqf_vs_mocap_flexion['p-val'].iloc[0], 0.05/4, height = 0.002, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

plot_utils.plot_box(ax2, vqf_rmsd_arr['adduction'], position = 3, color = color_similarity, width = box_width, alpha = 0.8, side = 'right')
plot_utils.plot_data_point(ax2, vqf_rmsd_arr['adduction'], color = color_similarity, position = 3.25)
plot_utils.plot_density(ax2, vqf_rmsd_arr['adduction'], position = 3 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')

plot_utils.plot_box(ax2, mocap_rmsd_arr['adduction'], position = 4, color = color_mocap, width = box_width, alpha = 0.6, side = 'left')
plot_utils.plot_data_point(ax2, mocap_rmsd_arr['adduction'], color = color_mocap, position = 3.75)
plot_utils.plot_density(ax2, mocap_rmsd_arr['adduction'], position = 4 - box_width/2, color = color_mocap, scale = scale, covf = covf, side = 'left')
plot_utils.label_diff(ax2, 3, 4, vqf_vs_mocap_adduction['p-val'].iloc[0], 0.05/4, height = 0.002, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

plot_utils.plot_box(ax2, vqf_rmsd_arr['rotation'], position = 5, color = color_similarity, width = box_width, alpha = 0.8, side = 'right')
plot_utils.plot_data_point(ax2, vqf_rmsd_arr['rotation'], color = color_similarity, position = 5.25)
plot_utils.plot_density(ax2, vqf_rmsd_arr['rotation'], position = 5 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')

plot_utils.plot_box(ax2, mocap_rmsd_arr['rotation'], position = 6, color = color_mocap, width = box_width, alpha = 0.6, side = 'left')
plot_utils.plot_data_point(ax2, mocap_rmsd_arr['rotation'], color = color_mocap, position = 5.75)
plot_utils.plot_density(ax2, mocap_rmsd_arr['rotation'], position = 6 - box_width/2, color = color_mocap, scale = scale, covf = covf, side = 'left')
plot_utils.label_diff(ax2, 5, 6, vqf_vs_mocap_rotation['p-val'].iloc[0], 0.05/4, height = 0.1, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

# ax2.set_ylim([0, 15])
# ax2.set_yticks([0, 5, 10, 15])
ax2.set_ylim([0, 16])
ax2.set_yticks([0, 4, 8, 12, 16])
ax2.set_yticklabels([])

ax2.set_xlim([0.5, 6.5])
ax2.set_xticks([0.5, 1.5, 3.5, 5.5, 6.5])
ax2.set_xticklabels(['', 'Flexion', 'Adduction', 'Rotation', ''])

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_position(('outward', 8))
ax2.spines['bottom'].set_position(('outward', 5))


# Comparisons across filters
plot_utils.plot_box(ax3, vqf_rmsd_arr['overall'], position = 1, color = color_similarity, width = box_width, alpha = 0.8, side = 'right')
plot_utils.plot_data_point(ax3, vqf_rmsd_arr['overall'], color = color_similarity, position = 1.25)
plot_utils.plot_density(ax3, vqf_rmsd_arr['overall'], position = 1 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')

plot_utils.plot_box(ax3, ekf_rmsd_arr['overall'], position = 2, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_utils.plot_data_point(ax3, ekf_rmsd_arr['overall'], color = color_difference, position = 2.25)
plot_utils.plot_density(ax3, ekf_rmsd_arr['overall'], position = 2 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')
plot_utils.label_diff(ax3, 1, 2, vqf_vs_ekf_overall['p-val'].iloc[0], 0.05/4, height = 0.94, font_size = fontsize_stats, color = color_similarity, s_pos = 'top')

plot_utils.plot_box(ax3, mad_rmsd_arr['overall'], position = 3, color = color_similarity, width = box_width, alpha = 0.8, side = 'right')
plot_utils.plot_data_point(ax3, mad_rmsd_arr['overall'], color = color_similarity, position = 3.25)
plot_utils.plot_density(ax3, mad_rmsd_arr['overall'], position = 3 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')
plot_utils.label_diff(ax3, 1, 3, vqf_vs_mad_overall['p-val'].iloc[0], 0.05/4, height = 0.07, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

plot_utils.plot_box(ax3, mah_rmsd_arr['overall'], position = 4, color = color_similarity, width = box_width, alpha = 0.8, side = 'right')
plot_utils.plot_data_point(ax3, mah_rmsd_arr['overall'], color = color_similarity, position = 4.25)
plot_utils.plot_density(ax3, mah_rmsd_arr['overall'], position = 4 + box_width/2, color = color_similarity, scale = scale, covf = covf, side = 'right')
plot_utils.label_diff(ax3, 1, 4, vqf_vs_mah_overall['p-val'].iloc[0], 0.05/4, height = 0.002, font_size = fontsize_stats, color = color_similarity, s_pos = 'bottom')

plot_utils.plot_box(ax3, riann_rmsd_arr['overall'], position = 5, color = color_difference, width = box_width, alpha = 0.5, side = 'right')
plot_utils.plot_data_point(ax3, riann_rmsd_arr['overall'], color = color_difference, position = 5.25)
plot_utils.plot_density(ax3, riann_rmsd_arr['overall'], position = 5 + box_width/2, color = color_difference, scale = scale, covf = covf, side = 'right')
plot_utils.label_diff(ax3, 1, 5, vqf_vs_riann_overall['p-val'].iloc[0], 0.05/4, height = 1, font_size = fontsize_stats, color = color_similarity, s_pos = 'top')


# ax3.set_ylim([0, 15])
# ax3.set_yticks([0, 5, 10, 15])
ax3.set_ylim([0, 16])
ax3.set_yticks([0, 4, 8, 12, 16])
ax3.set_yticklabels([])

ax3.set_xlim([0.5, 5.5])
ax3.set_xticks([0.5, 1, 2, 3, 4, 5, 5.5])
ax3.set_xticklabels(['', 'VQF', 'EKF', 'MAD', 'MAH', 'RIANN', ''])

ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['left'].set_position(('outward', 8))
ax3.spines['bottom'].set_position(('outward', 5))


plt.savefig('figures/benchmark_f7.svg')


plt.show()


