# name: plot_benchmark_f1_ik.py
# description: plot 5-dof kinematics for illustration of the benchmark pipeline
# author: Vu Phan
# date: 05/09/2025


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

import os


subject = 5
f_type  = 'VQF'
dim     = '9d'

task = 'treadmill_walking'

filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '.pkl'

ja_mt = eval_utils.load_data(filename_mt)

event = eval_segment.get_events(subject, task, 0)
segment_mt = eval_segment.get_segment(ja_mt, event, task)

fig, ax = plt.subplots(5, 1, figsize = (4, 7), sharex = True)

ax[0].plot(np.mean(segment_mt['hip_flexion_r'], axis = 0), color = '#0D3B66')
ax[0].fill_between(np.arange(segment_mt['hip_flexion_r'].shape[1]), np.mean(segment_mt['hip_flexion_r'], axis = 0) - np.std(segment_mt['hip_flexion_r'], axis = 0), np.mean(segment_mt['hip_flexion_r'], axis = 0) + np.std(segment_mt['hip_flexion_r'], axis = 0), color = '#89A6FB', alpha = 0.2)
ax[0].set_ylim(-30, 30)
ax[0].set_xlim(0, 100)
ax[0].set_yticks([-30, 0, 30])

ax[1].plot(np.mean(segment_mt['hip_adduction_r'], axis = 0), color = '#0D3B66')
ax[1].fill_between(np.arange(segment_mt['hip_adduction_r'].shape[1]), np.mean(segment_mt['hip_adduction_r'], axis = 0) - np.std(segment_mt['hip_adduction_r'], axis = 0), np.mean(segment_mt['hip_adduction_r'], axis = 0) + np.std(segment_mt['hip_adduction_r'], axis = 0), color = '#89A6FB', alpha = 0.2)
ax[1].set_ylim(-10, 15)
ax[1].set_yticks([-10, 0, 15])

ax[2].plot(np.mean(segment_mt['hip_rotation_r'], axis = 0), color = '#0D3B66')
ax[2].fill_between(np.arange(segment_mt['hip_rotation_r'].shape[1]), np.mean(segment_mt['hip_rotation_r'], axis = 0) - np.std(segment_mt['hip_rotation_r'], axis = 0), np.mean(segment_mt['hip_rotation_r'], axis = 0) + np.std(segment_mt['hip_rotation_r'], axis = 0), color = '#89A6FB', alpha = 0.2)
ax[2].set_ylim(-10, 25)
ax[2].set_yticks([-10, 0, 25])

ax[3].plot(np.mean(segment_mt['knee_flexion_r'], axis = 0), color = '#0D3B66')
ax[3].fill_between(np.arange(segment_mt['knee_flexion_r'].shape[1]), np.mean(segment_mt['knee_flexion_r'], axis = 0) - np.std(segment_mt['knee_flexion_r'], axis = 0), np.mean(segment_mt['knee_flexion_r'], axis = 0) + np.std(segment_mt['knee_flexion_r'], axis = 0), color = '#89A6FB', alpha = 0.2)
ax[3].set_ylim(-10, 70)
ax[3].set_yticks([-10, 0, 70])

ax[4].plot(np.mean(segment_mt['ankle_flexion_r'], axis = 0), color = '#0D3B66')
ax[4].fill_between(np.arange(segment_mt['ankle_flexion_r'].shape[1]), np.mean(segment_mt['ankle_flexion_r'], axis = 0) - np.std(segment_mt['ankle_flexion_r'], axis = 0), np.mean(segment_mt['ankle_flexion_r'], axis = 0) + np.std(segment_mt['ankle_flexion_r'], axis = 0), color = '#89A6FB', alpha = 0.2)
ax[4].set_ylim(-30, 20)
ax[4].set_yticks([-30, 0, 20])


for i in range(5):
    ax[i].spines['top'].set_visible(False)
    ax[i].spines['right'].set_visible(False)
    ax[i].spines['left'].set_visible(False)
    ax[i].spines['bottom'].set_visible(False)

    ax[i].set_xticks([])
    ax[i].set_yticks([])

os.makedirs('imu_benchmark/figures', exist_ok = True)

plt.savefig('imu_benchmark/figures/benchmark_f1_ik.svg')

# plt.show()



