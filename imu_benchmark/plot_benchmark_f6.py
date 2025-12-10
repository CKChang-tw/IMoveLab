# name: plot_benchmark_f6.py
# description: plot figure 6 for the benchmark kinematics paper
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
        askterisk_v = 0.04*(range[1] - range[0])
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


# --- Overall RMSE --- #
filter_list = {'VQF-9D': None}
reference = '_direct'
title_alignment = '_alignment'

for filter_info in filter_list.keys():
    f_type, dim = filter_info.split('-')

    print('*** Filter ' + f_type + ' ' + dim)

    subject_val = []

    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []

        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:
            if subject == 21 and task == 'treadmill_running':
                continue 

            filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + '.pkl'
            ja_mt = eval_utils.load_data(filename_mt)

            joint_val = []

            # if subject == 18:
            #     breakpoint()

            for joint in ja_mt.keys():
                if task == 'treadmill_walking' or task == 'treadmill_running':
                    if '_l' in joint:
                        continue

                joint_val.append(ja_mt[joint])

            task_val.append(np.nanmean(joint_val))

        subject_val.append(np.nanmean(task_val))
    
    filter_list[filter_info] = np.array(subject_val)

# Task data
filter_list_task = {'VQF-9D': None}

for filter_info in filter_list.keys():
    f_type, dim = filter_info.split('-')

    print('*** Filter ' + f_type + ' ' + dim)

    subject_val = []
    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []

        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:
            if subject == 21 and task == 'treadmill_running':
                continue 

            filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + '.pkl'
            
            ja_mt = eval_utils.load_data(filename_mt)

            joint_val = []

            # if subject == 18:
            #     breakpoint()

            for joint in ja_mt.keys():
                print(joint)
                # if task == 'treadmill_walking' or task == 'treadmill_running':
                #     if '_l' in joint:
                #         continue
                if '_l' in joint:
                    continue

                joint_val.append(ja_mt[joint])

            task_val.append(np.nanmean(joint_val))

        # subject_val.append(np.nanmean(task_val))
        subject_val.append(task_val)
    
    filter_list_task[filter_info] = np.array(subject_val)

with open('imu_benchmark/mt_std.pkl', 'rb') as file:
    all_mean_std = pkl.load(file)

selected_filter_info = 'VQF-9D'
# task_std = 1*all_mean_std[:, 0]
# task_std = np.array(task_std)
task_rmsd = 1*filter_list_task[selected_filter_info].mean(axis = 0)


from imu_benchmark.utils import common
task_list = common.get_task_list(None)
subject_list = common.get_subject_list(None)

task_std_all = []

for task in task_list:
    temp = []
    for subject in subject_list:
        filename_acc = constant_common.OUT_MT_ACC_DIST_PATH + 'acc_dist_s' + str(subject) + '_' + task + '.pkl'
        acc_dist = eval_utils.load_data(filename_acc)
        for sensor in acc_dist.keys():
            if '_l' in sensor:
                pass 
            else:
                temp.append(acc_dist[sensor])
    task_std_all.append(np.nanmean(temp))

task_std = np.array(task_std_all)



# speed_outcome = 1*filter_list_task[selected_filter_info]
# speed_rmsd_walking_median = np.median(speed_outcome[:, 1])
# speed_rmsd_walking_25th = np.percentile(speed_outcome[:, 1], 25)
# speed_rmsd_walking_75th = np.percentile(speed_outcome[:, 1], 75)

# speed_rmsd_snh_median = np.median(speed_outcome[:, 8])
# speed_rmsd_snh_25th = np.percentile(speed_outcome[:, 8], 25)
# speed_rmsd_snh_75th = np.percentile(speed_outcome[:, 8], 75)

# print('walking' + str(speed_rmsd_walking_median))
# print('walking' + str(speed_rmsd_walking_25th))
# print('walking' + str(speed_rmsd_walking_75th))
# print()
# print('snh' + str(speed_rmsd_snh_median))
# print('snh' + str(speed_rmsd_snh_25th))
# print('snh' + str(speed_rmsd_snh_75th))

# breakpoint()

# DoFs
dof_filter_list = {'VQF-9D': {}}

reference = '_direct'

for filter_info in dof_filter_list.keys():
    f_type, dim = filter_info.split('-')

    print('*** Filter ' + f_type + ' ' + dim)

    subject_val_hip_adduction   = []
    subject_val_hip_rotation    = []
    subject_val_hip_flexion     = []
    subject_val_knee_adduction  = []
    subject_val_knee_rotation   = []
    subject_val_knee_flexion    = []
    subject_val_ankle_adduction = []
    subject_val_ankle_rotation  = []
    subject_val_ankle_flexion   = []

    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val_hip_adduction   = []
        task_val_hip_rotation    = []
        task_val_hip_flexion     = []
        task_val_knee_adduction  = []
        task_val_knee_rotation   = []
        task_val_knee_flexion    = []
        task_val_ankle_adduction = []
        task_val_ankle_rotation  = []
        task_val_ankle_flexion   = []

        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:
            filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + '.pkl'
            
            ja_mt = eval_utils.load_data(filename_mt)

            joint_val_hip_adduction   = []
            joint_val_hip_rotation    = []
            joint_val_hip_flexion     = []
            joint_val_knee_adduction  = []
            joint_val_knee_rotation   = []
            joint_val_knee_flexion    = []
            joint_val_ankle_adduction = []
            joint_val_ankle_rotation  = []
            joint_val_ankle_flexion   = []

            for joint in ja_mt.keys():
                if '_l' in joint:
                    continue

                # joint_val.append(ja_mt[joint])
                if 'hip_adduction' in joint:
                    joint_val_hip_adduction.append(ja_mt[joint])
                elif 'hip_rotation' in joint:
                    joint_val_hip_rotation.append(ja_mt[joint])
                elif 'hip_flexion' in joint:
                    joint_val_hip_flexion.append(ja_mt[joint])
                elif 'knee_adduction' in joint:
                    joint_val_knee_adduction.append(ja_mt[joint])
                elif 'knee_rotation' in joint:
                    joint_val_knee_rotation.append(ja_mt[joint])
                elif 'knee_flexion' in joint:
                    joint_val_knee_flexion.append(ja_mt[joint])
                elif 'ankle_adduction' in joint:
                    joint_val_ankle_adduction.append(ja_mt[joint])
                elif 'ankle_rotation' in joint:
                    joint_val_ankle_rotation.append(ja_mt[joint])
                elif 'ankle_flexion' in joint:
                    joint_val_ankle_flexion.append(ja_mt[joint])

            # task_val.append(np.mean(joint_val))
            task_val_hip_adduction.append(np.mean(joint_val_hip_adduction))
            task_val_hip_rotation.append(np.mean(joint_val_hip_rotation))
            task_val_hip_flexion.append(np.mean(joint_val_hip_flexion))
            task_val_knee_adduction.append(np.mean(joint_val_knee_adduction))
            task_val_knee_rotation.append(np.mean(joint_val_knee_rotation))
            task_val_knee_flexion.append(np.mean(joint_val_knee_flexion))
            task_val_ankle_adduction.append(np.mean(joint_val_ankle_adduction))
            task_val_ankle_rotation.append(np.mean(joint_val_ankle_rotation))
            task_val_ankle_flexion.append(np.mean(joint_val_ankle_flexion))

        # subject_val.append(np.mean(task_val))
        subject_val_hip_adduction.append(np.mean(task_val_hip_adduction))
        subject_val_hip_rotation.append(np.mean(task_val_hip_rotation))
        subject_val_hip_flexion.append(np.mean(task_val_hip_flexion))
        subject_val_knee_adduction.append(np.mean(task_val_knee_adduction))
        subject_val_knee_rotation.append(np.mean(task_val_knee_rotation))
        subject_val_knee_flexion.append(np.mean(task_val_knee_flexion))
        subject_val_ankle_adduction.append(np.mean(task_val_ankle_adduction))
        subject_val_ankle_rotation.append(np.mean(task_val_ankle_rotation))
        subject_val_ankle_flexion.append(np.mean(task_val_ankle_flexion))
    
    # filter_list[filter_info] = np.array(subject_val)
    dof_filter_list[filter_info]['hip_adduction'] = np.array(subject_val_hip_adduction)
    dof_filter_list[filter_info]['hip_rotation']  = np.array(subject_val_hip_rotation)
    dof_filter_list[filter_info]['hip_flexion']   = np.array(subject_val_hip_flexion)
    dof_filter_list[filter_info]['knee_adduction'] = np.array(subject_val_knee_adduction)
    dof_filter_list[filter_info]['knee_rotation']  = np.array(subject_val_knee_rotation)
    dof_filter_list[filter_info]['knee_flexion']   = np.array(subject_val_knee_flexion)
    dof_filter_list[filter_info]['ankle_adduction'] = np.array(subject_val_ankle_adduction)
    dof_filter_list[filter_info]['ankle_rotation']  = np.array(subject_val_ankle_rotation)
    dof_filter_list[filter_info]['ankle_flexion']   = np.array(subject_val_ankle_flexion)

# Demographic data
gender = [1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0]
age    = [29, 26, 25, 53, 27, 41, 42, 37, 34, 44, 34, 36, 37, 55, 57, 30, 25, 28, 27]
weight = [66.97, 55.57, 95.55, 85.2, 52.45, 76.08, 80.25, 71.55, 62, 72.3, 120.15, 123.4, 72.87, 96.8, 67.87, 78.37, 85.77, 72.07, 51.9]
height = [181, 165, 185, 168, 158, 176, 179, 167, 162, 180, 170, 166, 169, 190, 166, 175, 180, 167, 160]
bmi    = [20.4419889502762, 20.4113865932048, 27.918188458729, 30.187074829932, 21.0102547668643, 24.5609504132231, 25.0460347679536, 25.6552762737997, 23.6244474927602, 22.3148148148148, 41.5743944636678, 44.7815357816809, 25.5138125415777, 26.814404432133, 24.6298446799245, 25.5902040816327, 26.4722222222222, 25.8417297142242, 20.2734375]
llen   = [104, 92.5, 103.5, 94, 98, 106, 107, 101, 99, 105.5, 101, 94, 99, 106, 99, 105, 99, 93, 94.5]
flen   = [30.5, 27, 32, 32, 30, 34, 33, 36, 31, 35, 33, 31, 33, 36, 32, 34, 33, 32, 28]

# Gender
selected_filter_info = 'VQF-9D'
male_rmsd = []
female_rmsd = []

for i in range(len(gender)):
    if gender[i] == 1:
        male_rmsd.append(filter_list[selected_filter_info][i])
    else:
        female_rmsd.append(filter_list[selected_filter_info][i])


# Sensor placement
# placement_list = {'hm': None, 'mm': None, 'lm': None,
#                   'hh': None, 'mh': None, 'lh': None,
#                   'hl': None, 'ml': None, 'll': None}
        
placement_list = {'hh': None, 'lh': None,
                  'hl': None, 'll': None}

f_type = 'VQF'
dim = '9d'

for placement in placement_list.keys():
    
    print('Placement: ', placement)

    subject_val = []
    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []

        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:

            if placement == 'mm':
                filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + '.pkl'
            else:
                filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + placement + reference + title_alignment + '_mt' + '.pkl'

            ja_mt = eval_utils.load_data(filename_mt)

            joint_val = []

            # if subject == 17:
            #     breakpoint()

            for joint in ja_mt.keys():

                if task == 'treadmill_walking' or task == 'treadmill_running':
                    if '_l' in joint:
                        continue

                # if 'sts' not in task:
                #     continue
                    
                # if 'treadmill_running' not in task: # only a specific task
                #     continue

                if 'knee_flexion' not in joint:
                    continue

                joint_val.append(ja_mt[joint])

            task_val.append(np.nanmean(joint_val))

        subject_val.append(np.nanmean(task_val))
    
    placement_list[placement] = np.array(subject_val)


# Sensor placement (with perfect standing assumption)
placement_psa_list = {'hl': None, 'hh': None, 'lh': None, 'll': None}

for placement in placement_psa_list.keys():
    
    print('Placement: ', placement)

    subject_val = []
    for subject in constant_common.SUBJECT_LIST:
        print(' - Subject ' + str(subject))
        
        task_val = []

        for task in list(constant_common.MAPPING_TASK_TO_ID.keys())[1::]:

            if placement == 'mm':
                filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + reference + title_alignment + '_mt' + '_psa.pkl'
            else:
                filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + placement + reference + title_alignment + '_mt' + '_psa.pkl'

            ja_mt = eval_utils.load_data(filename_mt)

            joint_val = []

            # if subject == 17:
            #     breakpoint()

            for joint in ja_mt.keys():

                if task == 'treadmill_walking' or task == 'treadmill_running':
                    if '_l' in joint:
                        continue

                # if 'sts' not in task:
                #     continue
                    
                # if 'treadmill_running' not in task: # only a specific task
                #     continue

                if 'knee_flexion' not in joint:
                    continue

                joint_val.append(ja_mt[joint])

            task_val.append(np.nanmean(joint_val))

        subject_val.append(np.nanmean(task_val))
    
    placement_psa_list[placement] = np.array(subject_val)


# --- Stats --- #
from scipy import stats
# male_vs_female = pg.wilcoxon(male_rmsd, female_rmsd)
male_vs_female = stats.mannwhitneyu(male_rmsd, female_rmsd)
print('*** Gender ***')
print(' - p = ' + str(male_vs_female))
print('male: ' + str(np.median(male_rmsd)))
print('male Q1: ' + str(np.percentile(male_rmsd, 25)))
print('male Q3: ' + str(np.percentile(male_rmsd, 75)))
print('female: ' + str(np.median(female_rmsd)))
print('female Q1: ' + str(np.percentile(female_rmsd, 25)))
print('female Q3: ' + str(np.percentile(female_rmsd, 75)))
print('difference = ' + str(np.median(male_rmsd) - np.median(female_rmsd)))
print()

# breakpoint()

age_vs_rmsd = pg.corr(age, filter_list[selected_filter_info], method = 'spearman')
print('*** Age ***')
print(age_vs_rmsd)
print()

bmi_vs_rmsd = pg.corr(bmi, filter_list[selected_filter_info], method = 'spearman')
print('*** BMI ***')
print(bmi_vs_rmsd)
print()

speed_vs_rmsd = pg.corr(task_std, task_rmsd, method = 'spearman')
print('*** Speed ***')
print(speed_vs_rmsd)
print()

# multiple wilcoxon tests for DoFs
import pandas as pd
print('*** DoFs ***')
print(pg.friedman(pd.DataFrame(dof_filter_list[selected_filter_info])))
print(pg.wilcoxon(dof_filter_list[selected_filter_info]['hip_flexion'], dof_filter_list[selected_filter_info]['hip_adduction']))
print(pg.wilcoxon(dof_filter_list[selected_filter_info]['hip_flexion'], dof_filter_list[selected_filter_info]['hip_rotation']))
print(pg.wilcoxon(dof_filter_list[selected_filter_info]['knee_flexion'], dof_filter_list[selected_filter_info]['knee_adduction']))
print(pg.wilcoxon(dof_filter_list[selected_filter_info]['knee_flexion'], dof_filter_list[selected_filter_info]['knee_rotation']))
print(pg.wilcoxon(dof_filter_list[selected_filter_info]['ankle_flexion'], dof_filter_list[selected_filter_info]['ankle_adduction']))
print(pg.wilcoxon(dof_filter_list[selected_filter_info]['ankle_flexion'], dof_filter_list[selected_filter_info]['ankle_rotation']))



# print(pd.DataFrame(placement_list))
print('*** Placement ***')
print(pg.friedman(pd.DataFrame(placement_list)))
# hl, hh, lh, ll
print(pg.wilcoxon(placement_list['hl'], placement_list['hh']))
print(pg.wilcoxon(placement_list['hl'], placement_list['lh']))
print(pg.wilcoxon(placement_list['hl'], placement_list['ll']))
print(pg.wilcoxon(placement_list['hh'], placement_list['lh']))
print(pg.wilcoxon(placement_list['hh'], placement_list['ll']))
print(pg.wilcoxon(placement_list['lh'], placement_list['ll']))

print('*** Placement (with perfect standing assumption) ***')
print(pg.friedman(pd.DataFrame(placement_psa_list)))


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



print()
print('DoFs')
print(np.median(dof_filter_list[selected_filter_info]['hip_adduction']))
print(np.median(dof_filter_list[selected_filter_info]['hip_rotation']))
print(np.median(dof_filter_list[selected_filter_info]['hip_flexion']))
print(np.median(dof_filter_list[selected_filter_info]['knee_adduction']))
print(np.median(dof_filter_list[selected_filter_info]['knee_rotation']))
print(np.median(dof_filter_list[selected_filter_info]['knee_flexion']))
print(np.median(dof_filter_list[selected_filter_info]['ankle_adduction']))
print(np.median(dof_filter_list[selected_filter_info]['ankle_rotation']))
print(np.median(dof_filter_list[selected_filter_info]['ankle_flexion']))
print()

C1 = 'hl'
C2 = 'hh'
C3 = 'lh'
C4 = 'll'

print('Placement')
# print(np.median(placement_list['mm']))
# print(np.median(placement_list['hm']))
# print(np.median(placement_list['lm']))
print(np.median(placement_list[C1]))
print('- Near Q1: ' + str(np.percentile(placement_list[C1], 25)))
print('- Near Q3: ' + str(np.percentile(placement_list[C1], 75)))
print(np.median(placement_list[C2]))
# print(np.median(placement_list['mh']))
print(np.median(placement_list[C3]))
print('- Distal Q1: ' + str(np.percentile(placement_list[C3], 25)))
print('- Distal Q3: ' + str(np.percentile(placement_list[C3], 75)))
# print(np.median(placement_list['ml']))
print(np.median(placement_list[C4]))
# print('- I2 Q1: ' + str(np.percentile(placement_list['ll'], 25)))
# print('- I2 Q3: ' + str(np.percentile(placement_list['ll'], 75)))
print()
# breakpoint()

print('Placement (with perfect standing assumption instead of functional calibration)')
print(np.median(placement_psa_list[C1]))
print(np.median(placement_psa_list[C2]))
print(np.median(placement_psa_list[C3]))
print(np.median(placement_psa_list[C4]))

# print(np.median(placement_list['mm'] - placement_list['mh']))
# print(np.percentile(placement_list['mm'] - placement_list['mh'], 25))
# print(np.percentile(placement_list['mm'] - placement_list['mh'], 75))

# print()
# print(np.median(placement_list['mm'] - placement_list['ml']))
# print(np.percentile(placement_list['mm'] - placement_list['ml'], 25))
# print(np.percentile(placement_list['mm'] - placement_list['ml'], 75))



alpha_bon = 0.05/22




# --- Plotting --- #
from scipy.stats import spearmanr
from scipy.optimize import curve_fit

def f(x, A, B):
    return A*x + B


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

y_lim_min = 0
y_lim_max = 20

plt.rcParams.update({'font.size': font_size})
fig = plt.figure(figsize=(10, 14))
gs = gridspec.GridSpec(4, 4, width_ratios=[0.25, 0.25, 0.25, 0.25])

# gs.update(wspace = 0.1, bottom = 0.17)
gs.update(hspace = 0.45, wspace = 0.3)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[0, 3])
ax5 = fig.add_subplot(gs[1, :])

# ax6 = fig.add_subplot(gs[2, 0:2])
# ax7 = fig.add_subplot(gs[2, 2:4])
ax6 = fig.add_subplot(gs[2, :]) # placement (functional calibration)
ax7 = fig.add_subplot(gs[3, :]) # placement (perfect standing assumption)

# Male vs. female
plot_box(ax1, data = male_rmsd, position = 1, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax1, data = male_rmsd, color = color_mt, position = 1.25)
plot_density(ax1, data = male_rmsd, position = 1 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')

plot_box(ax1, data = female_rmsd, position = 2, color = color_mt, width = box_width, alpha = 0.5, side = 'left')
plot_data_point(ax1, data = female_rmsd, color = color_mt, position = 1.75)
plot_density(ax1, data = female_rmsd, position = 2 - box_width/2, color = color_mt, scale = scale, covf = covf, side = 'left')
label_diff(ax1, 1, 2, male_vs_female[1], 0.05, height = 0.9, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_position(('outward', 8))
ax1.spines['bottom'].set_position(('outward', 5))

ax1.set_xlim([0.2, 2.8])
ax1.set_xticks([0.2, 1, 2, 2.8])
ax1.set_xticklabels(['', 'Male', 'Female', ''], fontsize = font_size)
# ax1.set_xticklabels([])
# tick_positions = [0.2, 1, 2, 2.8]
# labels_top = ['', 'Male', 'Female', '']
# labels_bottom = ['', '(VQF-9D)', '(VQF-9D)', '']

# for i, (top, bottom) in enumerate(zip(labels_top, labels_bottom)):
#     ax1.text(tick_positions[i], -.75, top, ha='center', va='center', fontsize = font_size, color='k', transform=ax1.transData)  # Top row (red)
#     ax1.text(tick_positions[i], -1.25, bottom, ha='center', va='center', fontsize = fontsize_stats, color='gray', transform=ax1.transData)  # Bottom row (blue)

ax1.set_ylim([y_lim_min, y_lim_max])
# ax1.set_yticks([0, 5, 10, 15])
ax1.set_ylabel(r'Overall RMSD ($^\circ$)', fontsize = fontsize_label)

ax1.set_xlabel('Sex', fontsize = font_size)

def rank(x):
    order = np.argsort(x)
    ranks = order.argsort() + 1

    return ranks

# Age
ax2.scatter(age, filter_list[selected_filter_info], color = color_mt, alpha = 0.5, s = 100, edgecolor = 'none', marker = '.')
ax2.hist(age, bins = 10, color = 'lightgray', alpha = 0.5, edgecolor = 'none', zorder = 0)
# u_popt, _ = curve_fit(f, age, filter_list[selected_filter_info])
# xline = np.linspace(20, 60, 200)
# yline = f(xline, u_popt[0], u_popt[1])
# ax2.plot(xline, yline, color = color_mt, linestyle = '--', linewidth = 4, alpha = 0.5)

# from sklearn.isotonic import IsotonicRegression
# xline = np.linspace(20, 60, 200)
# ir_age = IsotonicRegression(increasing = True)
# y_isotonic = ir_age.fit_transform(age, filter_list[selected_filter_info])
# yline = ir_age.predict(xline)


# ax2.annotate(r'$R = $' + str(np.round(spearmanr(age, filter_list[selected_filter_info])[0], 2)) + r'$(\dag)$', xy = (0.55, 0.95), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'left', va = 'top')
ax2.annotate(r"Spearman's $\rho = $" + str(np.round(spearmanr(age, filter_list[selected_filter_info])[0], 2)), xy = (0.95, 0.95), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top')
ax2.annotate(r'$p = $' + str(np.round(spearmanr(age, filter_list[selected_filter_info])[1], 2)), xy = (0.95, 0.87), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top', alpha = 0.7)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_position(('outward', 8))
ax2.spines['bottom'].set_position(('outward', 5))

ax2.set_xlim([20, 60])
ax2.set_ylim([y_lim_min, y_lim_max])
ax2.set_yticklabels([])
ax2.set_xlabel(r'Age $(years)$', fontsize = font_size)


# BMI
ax3.scatter(bmi, filter_list[selected_filter_info], color = color_mt, alpha = 0.5, s = 100, edgecolor = 'none', marker = '.')
ax3.hist(bmi, bins = 10, color = 'lightgray', alpha = 0.5, edgecolor = 'none', zorder = 0)
# u_popt, _ = curve_fit(f, bmi, filter_list[selected_filter_info])
# xline = np.linspace(10, 50, 200)
# yline = f(xline, u_popt[0], u_popt[1])
# ax3.plot(xline, yline, color = color_mt, linestyle = '--', linewidth = 4, alpha = 0.5)

ax3.annotate(r"Spearman's $\rho = $" + str(np.round(spearmanr(bmi, filter_list[selected_filter_info])[0], 2)), xy = (0.95, 0.95), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top')
ax3.annotate(r'$p = $' + str(np.round(spearmanr(bmi, filter_list[selected_filter_info])[1], 2)), xy = (0.95, 0.87), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top', alpha = 0.7)

ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['left'].set_position(('outward', 8))
ax3.spines['bottom'].set_position(('outward', 5))

ax3.set_xlim([10, 50]); ax3.set_xticks([10, 30, 50])
ax3.set_ylim([y_lim_min, y_lim_max])
ax3.set_yticklabels([])

ax3.set_xlabel(r'BMI ($kg/m^2$)', fontsize = font_size)

# breakpoint()
# Movement speed
ax4.scatter(task_std, task_rmsd, color = color_mt, alpha = 0.5, s = 100, edgecolor = 'none', marker = '.')
# ax4.scatter(rank(task_std), rank(task_rmsd), color = color_mt, alpha = 0.5, s = 100, edgecolor = 'none', marker = '.')
# u_popt, _ = curve_fit(f, task_std, task_rmsd)
# xline = np.linspace(0, 9, 200)
# yline = f(xline, u_popt[0], u_popt[1])
# ax4.plot(xline, yline, color = color_mt, linestyle = '--', linewidth = 4, alpha = 0.5)

ax4.annotate(r"Spearman's $\rho = $" + str(np.round(spearmanr(task_std, task_rmsd)[0], 2)), xy = (0.95, 0.95), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top')
ax4.annotate(r'$p = $' + str(np.round(spearmanr(task_std, task_rmsd)[1], 2)), xy = (0.95, 0.87), xycoords = 'axes fraction', fontsize = fontsize_stats, color = 'gray', ha = 'right', va = 'top', alpha = 0.7)

ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['left'].set_position(('outward', 8))
ax4.spines['bottom'].set_position(('outward', 5))

ax4.set_xlim([0, 9]); ax4.set_xticks([0, 3, 6, 9])
ax4.set_ylim([y_lim_min, y_lim_max])
ax4.set_yticklabels([])

ax4.set_xlabel(r'Accelerometry SD $(m/s^2)$', fontsize = font_size)


# DoFs
selected_filter_info = 'VQF-9D'
plot_box(ax5, data = dof_filter_list[selected_filter_info]['hip_adduction'], position = 2, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['hip_adduction'], color = color_mt, position = 2.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['hip_adduction'], position = 2 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax5, 1, 2, pg.wilcoxon(dof_filter_list[selected_filter_info]['hip_adduction'], dof_filter_list[selected_filter_info]['hip_flexion'])['p-val'].iloc[0], alpha_bon, height = 0.92, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])

plot_box(ax5, data = dof_filter_list[selected_filter_info]['hip_rotation'], position = 3, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['hip_rotation'], color = color_mt, position = 3.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['hip_rotation'], position = 3 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax5, 3, 1, pg.wilcoxon(dof_filter_list[selected_filter_info]['hip_rotation'], dof_filter_list[selected_filter_info]['hip_flexion'])['p-val'].iloc[0], alpha_bon, height = 0.99, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])

plot_box(ax5, data = dof_filter_list[selected_filter_info]['hip_flexion'], position = 1, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['hip_flexion'], color = color_mt, position = 1.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['hip_flexion'], position = 1 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')

plot_box(ax5, data = dof_filter_list[selected_filter_info]['knee_adduction'], position = 5, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['knee_adduction'], color = color_mt, position = 5.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['knee_adduction'], position = 5 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax5, 4, 5, pg.wilcoxon(dof_filter_list[selected_filter_info]['knee_adduction'], dof_filter_list[selected_filter_info]['knee_flexion'])['p-val'].iloc[0], alpha_bon, height = 0.92, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])

plot_box(ax5, data = dof_filter_list[selected_filter_info]['knee_rotation'], position = 6, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['knee_rotation'], color = color_mt, position = 6.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['knee_rotation'], position = 6 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax5, 6, 4, pg.wilcoxon(dof_filter_list[selected_filter_info]['knee_rotation'], dof_filter_list[selected_filter_info]['knee_flexion'])['p-val'].iloc[0], alpha_bon, height = 0.99, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])

plot_box(ax5, data = dof_filter_list[selected_filter_info]['knee_flexion'], position = 4, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['knee_flexion'], color = color_mt, position = 4.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['knee_flexion'], position = 4 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')

plot_box(ax5, data = dof_filter_list[selected_filter_info]['ankle_adduction'], position = 8, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['ankle_adduction'], color = color_mt, position = 8.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['ankle_adduction'], position = 8 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax5, 7, 8, pg.wilcoxon(dof_filter_list[selected_filter_info]['ankle_adduction'], dof_filter_list[selected_filter_info]['ankle_flexion'])['p-val'].iloc[0], alpha_bon, height = 0.92, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])

plot_box(ax5, data = dof_filter_list[selected_filter_info]['ankle_rotation'], position = 9, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['ankle_rotation'], color = color_mt, position = 9.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['ankle_rotation'], position = 9 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax5, 9, 7, pg.wilcoxon(dof_filter_list[selected_filter_info]['ankle_rotation'], dof_filter_list[selected_filter_info]['ankle_flexion'])['p-val'].iloc[0], alpha_bon, height = 0.99, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])

plot_box(ax5, data = dof_filter_list[selected_filter_info]['ankle_flexion'], position = 7, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax5, data = dof_filter_list[selected_filter_info]['ankle_flexion'], color = color_mt, position = 7.25)
plot_density(ax5, data = dof_filter_list[selected_filter_info]['ankle_flexion'], position = 7 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')


ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.spines['left'].set_position(('outward', 8))
ax5.spines['bottom'].set_position(('outward', 5))

ax5.set_xlim([0.2, 9.8])
ax5.set_xticks([0.2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9.8])
# ax5.set_xticklabels(['', 'HA', 'HR', 'HF', 'KA', 'KR', 'KF', 'AA', 'AR', 'AF', ''], fontsize = font_size)
# ax5.set_xticklabels(['', 'Adduction', 'Rotation', 'Flexion', 'Adduction', 'Rotation', 'Flexion', 'Adduction', 'Rotation', 'Flexion', ''], fontsize = font_size)
ax5.set_xticklabels([])
tick_top_positions = [0.2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9.8]
tick_bot_positions = [2, 5, 8]
# labels_top = ['', 'Adduction', 'Rotation', 'Flexion', 'Adduction', 'Rotation', 'Flexion', 'Adduction', 'Rotation', 'Flexion', '']
# labels_top = ['', 'Flex./Ext.', 'Add./Abd.', 'Int./Ext.', 'Flex./Ext.', 'Add./Abd.', 'Int./Ext.', 'Flex./Ext.', 'Add./Abd.', 'Int./Ext.', '']
labels_top = ['', 'F/E', 'A/A', 'I/E', 'F/E', 'A/A', 'I/E', 'F/E', 'A/A', 'I/E', '']
labels_bottom = ['Hip', 'Knee', 'Ankle']
for i, top in enumerate(labels_top):
    ax5.text(tick_top_positions[i], -2.8, top, ha='center', va='center', fontsize = fontsize_stats, color='gray', transform=ax5.transData)  # Top row (red)
for i, bottom in enumerate(labels_bottom):
    ax5.text(tick_bot_positions[i], -5, bottom, ha='center', va='center', fontsize = font_size, color='k', transform=ax5.transData)  # Bottom row (blue)

ax5.set_ylim([y_lim_min, 20])
ax5.set_ylabel(r'RMSD ($^\circ$)', fontsize = fontsize_label)


# Placements
print('corrected p = ' + str(alpha_bon))
print()

box_width = 0.1
plot_box(ax6, data = placement_list[C1], position = 1, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C1], color = color_mt, position = 1.25)
plot_density(ax6, data = placement_list[C1], position = 1 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
# label_diff(ax6, 1 + box_width/1.1, 2 - box_width/1.1, pg.wilcoxon(placement_list[C1], placement_list[C2])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.85, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
# print(' - p = ' + str(pg.wilcoxon(placement_list[C1], placement_list[C2])['p-val'].iloc[0]))
label_diff(ax6, 1 + box_width/1.1, 3 - box_width/1.1, pg.wilcoxon(placement_list[C1], placement_list[C3])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.99, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C1 vs. C3 = ' + str(pg.wilcoxon(placement_list[C1], placement_list[C3])['p-val'].iloc[0]))

plot_box(ax6, data = placement_list[C2], position = 2, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C2], color = color_mt, position = 2.25)
plot_density(ax6, data = placement_list[C2], position = 2 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax6, 2 + box_width/1.1, 3 - box_width/1.1, pg.wilcoxon(placement_list[C2], placement_list[C3])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.92, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C2 vs. C3 = ' + str(pg.wilcoxon(placement_list[C2], placement_list[C3])['p-val'].iloc[0]))

plot_box(ax6, data = placement_list[C3], position = 3, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C3], color = color_mt, position = 3.25)
plot_density(ax6, data = placement_list[C3], position = 3 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
label_diff(ax6, 3 + box_width/1.1, 4 - box_width/1.1, pg.wilcoxon(placement_list[C3], placement_list[C4])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.92, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
print(' - p C3 vs. C4 = ' + str(pg.wilcoxon(placement_list[C3], placement_list[C4])['p-val'].iloc[0]))

plot_box(ax6, data = placement_list[C4], position = 4, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax6, data = placement_list[C4], color = color_mt, position = 4.25)
plot_density(ax6, data = placement_list[C4], position = 4 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
# label_diff(ax6, 1 + box_width/1.1, 4 - box_width/1.1, pg.wilcoxon(placement_list[C1], placement_list[C4])['p-val'].iloc[0], alpha_bon = alpha_bon, height = 0.95, font_size = fontsize_stats, color = color_mt, range = [y_lim_min, y_lim_max])
# print(' - p = ' + str(pg.wilcoxon(placement_list[C1], placement_list[C4])['p-val'].iloc[0]))

print(' + p C1 vs. C2 = ' + str(pg.wilcoxon(placement_list[C1], placement_list[C2])['p-val'].iloc[0]))
print(' + p C2 vs. C4 = ' + str(pg.wilcoxon(placement_list[C2], placement_list[C4])['p-val'].iloc[0]))
print(' + p C1 vs. C4 = ' + str(pg.wilcoxon(placement_list[C1], placement_list[C4])['p-val'].iloc[0]))


ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.spines['left'].set_position(('outward', 8))
ax6.spines['bottom'].set_position(('outward', 5))

ax6.set_xlim([0.2, 4.8])
ax6.set_xticks([0.2, 1, 2, 3, 4, 4.8])
ax6.set_xticklabels(['', 'Configuration 1', 'Configuration 2', 'Configuration 3', 'Configuration 4', ''], fontsize = font_size)
ax6.set_ylim([y_lim_min, 20])

ax6.set_ylabel(r'Knee F/E RMSD ($^\circ$)', fontsize = fontsize_label)

# Placement (perfect standing assumption)
print()
plot_box(ax7, data = placement_psa_list[C1], position = 1, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax7, data = placement_psa_list[C1], color = color_mt, position = 1.25)
plot_density(ax7, data = placement_psa_list[C1], position = 1 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
print(' - p C1 vs. C3 = ' + str(pg.wilcoxon(placement_psa_list[C1], placement_psa_list[C3])['p-val'].iloc[0]))

plot_box(ax7, data = placement_psa_list[C2], position = 2, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax7, data = placement_psa_list[C2], color = color_mt, position = 2.25)
plot_density(ax7, data = placement_psa_list[C2], position = 2 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
print(' - p C2 vs. C3 = ' + str(pg.wilcoxon(placement_psa_list[C2], placement_psa_list[C3])['p-val'].iloc[0]))

plot_box(ax7, data = placement_psa_list[C3], position = 3, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax7, data = placement_psa_list[C3], color = color_mt, position = 3.25)
plot_density(ax7, data = placement_psa_list[C3], position = 3 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')
print(' - p C3 vs. C4 = ' + str(pg.wilcoxon(placement_psa_list[C3], placement_psa_list[C4])['p-val'].iloc[0]))

plot_box(ax7, data = placement_psa_list[C4], position = 4, color = color_mt, width = box_width, alpha = 0.5, side = 'right')
plot_data_point(ax7, data = placement_psa_list[C4], color = color_mt, position = 4.25)
plot_density(ax7, data = placement_psa_list[C4], position = 4 + box_width/2, color = color_mt, scale = scale, covf = covf, side = 'right')

print(' + p C1 vs. C4 = ' + str(pg.wilcoxon(placement_psa_list[C1], placement_psa_list[C4])['p-val'].iloc[0]))
print(' + p C1 vs. C2 = ' + str(pg.wilcoxon(placement_psa_list[C1], placement_psa_list[C2])['p-val'].iloc[0]))
print(' + p C2 vs. C4 = ' + str(pg.wilcoxon(placement_psa_list[C2], placement_psa_list[C4])['p-val'].iloc[0]))

ax7.spines['top'].set_visible(False)
ax7.spines['right'].set_visible(False)
ax7.spines['left'].set_position(('outward', 8))
ax7.spines['bottom'].set_position(('outward', 5))

ax7.set_xlim([0.2, 4.8])
ax7.set_xticks([0.2, 1, 2, 3, 4, 4.8])
ax7.set_xticklabels(['', 'Configuration 1', 'Configuration 2', 'Configuration 3', 'Configuration 4', ''], fontsize = font_size)
ax7.set_ylim([y_lim_min, 20])

ax7.set_ylabel(r'Knee F/E RMSD ($^\circ$)', fontsize = fontsize_label)

# # Example of placement during sit-to-stand (or sts)


# ax7.spines['top'].set_visible(False)
# ax7.spines['right'].set_visible(False)
# ax7.spines['left'].set_position(('outward', 8))
# ax7.spines['bottom'].set_position(('outward', 5))

# ax7.set_ylabel(r'Knee Flexion ($^o$)', fontsize = fontsize_label)

import os

os.makedirs('imu_benchmark/figures', exist_ok = True)

plt.savefig('imu_benchmark/figures/benchmark_f6.svg')

plt.show()

























