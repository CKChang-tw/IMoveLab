# name: eval_v2.py



import pickle
import os

from easydict import EasyDict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.signal import butter, filtfilt

from utils.biplane import biplane_processing
from utils.eval import sync
from constants import constant_common, constant_mc10, constant_meta
from utils.eval import alignment 


def low_pass_filter(data, cutoff = 15, fs = 100, order=4):
    
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)

    return y


dataset = 'HAKnee'
# subject = 6
test = 1

filter_type = 'riann'
dim = '6d'

for subject in constant_common.HA_SUBJECT_LIST:
# for subject in [15]:
    print(f'*** Subject {subject} ***')
    print('**************************')

    for side in ['r', 'l']:
    # for side in ['l']:

        for task in list(constant_common.HA_TASK_MAPPING.keys())[1::]:
        # for task in ['shop']:

            for trial in range(1, 4):
            # for trial in [2]:
                print(f'Processing {side} {task} trial {trial} ...')

                if constant_meta.VALID_COMPARISON[str(subject)][task][side][trial - 1]:

                    # task_static = EasyDict(side = constant_meta.STATIC_SIDE[str(subject)], trial = 1, task = 'static')
                    selected_task = EasyDict(side = side, trial = trial, task = task)


                    apply_sync = True
                    # apply_sync = False

                    apply_alignment = True
                    # apply_alignment = False



                    # --- load calculated kiinematics from different systems --- #
                    # mocap kinematics
                    mocap_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/ik/{subject}/mocap/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    with open(mocap_fn, 'rb') as f:
                        mocap_kinematics = pickle.load(f)

                    # mocap_fn_static = f'outputs/{dataset}/ik/{subject}/mocap/knee_kinematics_{task_static.side}_{task_static.task}_{task_static.trial}.pkl'
                    # with open(mocap_fn_static, 'rb') as f:
                    #     mocap_kinematics_static = pickle.load(f)

                    # breakpoint()

                    # set up NaN values to 0
                    for joint in mocap_kinematics.keys():
                        mocap_kinematics[joint] = mocap_kinematics[joint].fillna(-100)


                    # mc10 kinematics
                    mc10_fn  = f'outputs/{dataset}/bm_{filter_type}{dim}/ik/{subject}/mc10/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    with open(mc10_fn, 'rb') as f:
                        mc10_kinematics = pickle.load(f)


                    # with open(f'outputs/{dataset}/ik/{subject}/mc10/knee_kinematics_{task_static.side}_{task_static.task}_{task_static.trial}.pkl', 'rb') as f:
                    #     mc10_kinematics_static = pickle.load(f)


                    # filter MC10 kinematics a bit (due to skin motion artifacts)
                    for joint in mc10_kinematics.keys():
                        mc10_kinematics[joint] = low_pass_filter(mc10_kinematics[joint], cutoff = 15, fs = constant_mc10.PROCESSING_RATE, order=4)



                    # biplane kinematics
                    knee_kinematics = biplane_processing.get_biplane_knee_kinematics(subject, dataset, test, selected_task, ft = constant_mc10.PROCESSING_RATE)
                    # knee_kinematics_static = biplane_processing.get_biplane_knee_kinematics(subject, dataset, test, EasyDict(side = selected_task.side, trial = 1, task = 'static'), ft = constant_mc10.PROCESSING_RATE)

                    # breakpoint()



                    # --- data synchronization --- #
                    # coarse temporal sync
                    if apply_sync:

                        valid_mocap_start = np.where(mocap_kinematics[f'knee_flexion_{selected_task.side}'] > -100)[0][0]
                        valid_mocap_stop  = np.where(mocap_kinematics[f'knee_flexion_{selected_task.side}'] > -100)[0][-1]
                        print(f'Mocap valid frames: {valid_mocap_start} to {valid_mocap_stop}')
                        # start = 40
                        # stop  = 500
                        lag = sync.find_best_match(mc10_kinematics[f'knee_flexion_{selected_task.side}'], mocap_kinematics[f'knee_flexion_{selected_task.side}'][valid_mocap_start:valid_mocap_stop], nan_flag = False) - valid_mocap_start
                        # lag = sync.find_lag(mc10_kinematics[f'knee_flexion_{selected_task.side}'], mocap_kinematics[f'knee_flexion_{selected_task.side}'][200:500])
                        # trimmed_mc10_kinematics, trimmed_mocap_kinematics = sync.apply_sync(mc10_kinematics, mocap_kinematics, lag)
                        print(f'Sync lag between MC10 and Mocap: {lag} frames')


                    # trim data
                    if subject == 6 and selected_task.task == 'shop' and selected_task.side == 'r' and selected_task.trial == 2:
                        vicon_biplane_offset = 0
                    elif subject == 12 and selected_task.task == 'shop' and selected_task.side == 'l' and selected_task.trial == 3:
                        vicon_biplane_offset = 0
                    else:
                        vicon_biplane_offset = 300
                    sync_sample_window = 20

                    # valid_biplane_start = np.where(knee_kinematics[f'knee_flexion_{selected_task.side}'] > 0)[0][0]
                    # valid_biplane_stop  = np.where(knee_kinematics[f'knee_flexion_{selected_task.side}'] > 0)[0][-1]
                    # # valid_biplane_len   = valid_biplane_stop - valid_biplane_start

                    # find indices of values > 0 in the biplane kinematics
                    valid_biplane_id = np.where(knee_kinematics[f'knee_flexion_{selected_task.side}'] != 0)[0]
                    # keep only the largest continuous segment
                    diff = np.diff(valid_biplane_id)
                    split_indices = np.where(diff > 1)[0] + 1
                    segments = np.split(valid_biplane_id, split_indices)
                    largest_segment = max(segments, key=len)

                    valid_biplane_start = largest_segment[1]
                    valid_biplane_stop = largest_segment[-1]

                    # check_interp_error = abs(knee_kinematics[f'knee_flexion_{selected_task.side}'][largest_segment[0]] - 0.5*knee_kinematics[f'knee_flexion_{selected_task.side}'][largest_segment[1]])
                    # print(f'Check interp error at the start of the largest segment: {check_interp_error}')
                    # if check_interp_error <= 2:
                    #     valid_biplane_start = largest_segment[1]
                    # else:
                    #     valid_biplane_start = largest_segment[0]

                    # # print(knee_kinematics[f'knee_flexion_{selected_task.side}'][largest_segment[-2]])
                    # # print(knee_kinematics[f'knee_flexion_{selected_task.side}'][largest_segment[-1]])

                    # check_interp_error = abs(knee_kinematics[f'knee_flexion_{selected_task.side}'][largest_segment[-1]] - 0.5*knee_kinematics[f'knee_flexion_{selected_task.side}'][largest_segment[-2]])
                    # print(f'Check interp error at the end of the largest segment: {check_interp_error}')
                    # if check_interp_error <= 2:
                    #     print('here')
                    #     valid_biplane_stop = largest_segment[-1]
                    # else:
                    #     valid_biplane_stop = largest_segment[-1] + 1  # +1




                    trimmed_knee_kinematics  = {}
                    for joint in knee_kinematics.keys():
                        trimmed_knee_kinematics[joint] = 1*knee_kinematics[joint][valid_biplane_start:valid_biplane_stop]

                    trimmed_mocap_kinematics = {}
                    for joint in mocap_kinematics.keys():
                        if vicon_biplane_offset == 0:
                            trimmed_mocap_kinematics[joint] = 1*mocap_kinematics[joint][valid_biplane_start + vicon_biplane_offset:valid_biplane_stop + vicon_biplane_offset + sync_sample_window].to_numpy()
                        else:
                            trimmed_mocap_kinematics[joint] = 1*mocap_kinematics[joint][valid_biplane_start + vicon_biplane_offset - sync_sample_window:valid_biplane_stop + vicon_biplane_offset + sync_sample_window].to_numpy()

                    trimmed_mc10_kinematics  = {}
                    for joint in mc10_kinematics.keys():
                        if vicon_biplane_offset == 0:
                            trimmed_mc10_kinematics[joint] = 1*mc10_kinematics[joint][valid_biplane_start + lag + vicon_biplane_offset:valid_biplane_stop + lag + vicon_biplane_offset + sync_sample_window]
                        else:
                            trimmed_mc10_kinematics[joint] = 1*mc10_kinematics[joint][valid_biplane_start + lag + vicon_biplane_offset - sync_sample_window:valid_biplane_stop + lag + vicon_biplane_offset + sync_sample_window]


                    # finer temporal sync
                    lag_mocap_biplane = sync.find_best_match(trimmed_mocap_kinematics[f'knee_flexion_{selected_task.side}'], trimmed_knee_kinematics[f'knee_flexion_{selected_task.side}'], nan_flag = False)

                    temp  = sync.find_best_match(trimmed_mc10_kinematics[f'knee_flexion_{selected_task.side}'], trimmed_knee_kinematics[f'knee_flexion_{selected_task.side}'], nan_flag = False)
                    lag_mc10_biplane  = np.min([lag_mocap_biplane + 4, temp])

                    print(f'Sync lag between Mocap and Biplane: {lag_mocap_biplane} frames')
                    print(f'Sync lag between MC10 and Biplane: {lag_mc10_biplane} frames')

                    for joint in trimmed_knee_kinematics.keys():
                        trimmed_mocap_kinematics[joint] = trimmed_mocap_kinematics[joint][lag_mocap_biplane:lag_mocap_biplane + trimmed_knee_kinematics[joint].shape[0]]
                        trimmed_mc10_kinematics[joint]  = trimmed_mc10_kinematics[joint][lag_mc10_biplane:lag_mc10_biplane + trimmed_knee_kinematics[joint].shape[0]]


                    print(type(trimmed_mocap_kinematics[f'knee_flexion_{selected_task.side}']))
                    print(type(trimmed_mc10_kinematics[f'knee_flexion_{selected_task.side}']))
                    print(type(trimmed_knee_kinematics[f'knee_flexion_{selected_task.side}']))


                    # --- alignment --- #
                    if apply_alignment:
                        print('Applying alignment ...')

                        trimmed_mc10_kinematics  = alignment.get_ja_alignment_init(trimmed_mc10_kinematics, trimmed_knee_kinematics, selected_task.side, store_correction = False)
                        trimmed_mocap_kinematics = alignment.get_ja_alignment_init(trimmed_mocap_kinematics, trimmed_knee_kinematics, selected_task.side, store_correction = False)



                    # --- export segmented kinematics --- #
                    output_mc10_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/mc10/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    if not os.path.exists(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/mc10/'):
                        os.makedirs(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/mc10/')
                    with open(output_mc10_fn, 'wb') as f:
                        pickle.dump(trimmed_mc10_kinematics, f)

                    output_mocap_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/mocap/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    if not os.path.exists(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/mocap/'):
                        os.makedirs(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/mocap/')
                    with open(output_mocap_fn, 'wb') as f:
                        pickle.dump(trimmed_mocap_kinematics, f)

                    output_biplane_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/biplane/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    if not os.path.exists(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/biplane/'):
                        os.makedirs(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/biplane/')
                    with open(output_biplane_fn, 'wb') as f:
                        pickle.dump(trimmed_knee_kinematics, f)


                    # --- calculate RMSD --- #
                    rmsd_mc10_biplane = {}
                    rmsd_mc10_mocap  = {}
                    rmsd_mocap_biplane = {}

                    for joint in knee_kinematics.keys():
                        rmsd_mc10_biplane[joint] = np.sqrt(np.mean((trimmed_mc10_kinematics[joint] - trimmed_knee_kinematics[joint])**2))
                        rmsd_mc10_mocap[joint]  = np.sqrt(np.mean((trimmed_mc10_kinematics[joint] - trimmed_mocap_kinematics[joint])**2))
                        rmsd_mocap_biplane[joint] = np.sqrt(np.mean((trimmed_mocap_kinematics[joint] - trimmed_knee_kinematics[joint])**2))
                        print(f'RMSD {joint} - MC10: {rmsd_mc10_biplane[joint]:.2f}, Mocap: {rmsd_mocap_biplane[joint]:.2f}')
                        print(f'MC10 with Mocap: {rmsd_mc10_mocap[joint]:.2f}')
                        print('---')


                    output_rmsd_mc10_biplane_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/rmsd_mc10_biplane_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    if not os.path.exists(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/'):
                        os.makedirs(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/')
                    with open(output_rmsd_mc10_biplane_fn, 'wb') as f:
                        pickle.dump(rmsd_mc10_biplane, f)

                    output_rmsd_mc10_mocap_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/rmsd_mc10_mocap_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    if not os.path.exists(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/'):
                        os.makedirs(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/')
                    with open(output_rmsd_mc10_mocap_fn, 'wb') as f:
                        pickle.dump(rmsd_mc10_mocap, f)

                    output_rmsd_mocap_biplane_fn = f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/rmsd_mocap_biplane_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'
                    if not os.path.exists(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/'):
                        os.makedirs(f'outputs/{dataset}/bm_{filter_type}{dim}/eval/{subject}/')
                    with open(output_rmsd_mocap_biplane_fn, 'wb') as f:
                        pickle.dump(rmsd_mocap_biplane, f)





                    # # --- visualization --- #
                    # x_biplane = np.arange(0, knee_kinematics[f'knee_flexion_{selected_task.side}'].shape[0], 1)
                    # x_mocap   = np.arange(0, mocap_kinematics[f'knee_flexion_{selected_task.side}'].shape[0], 1)
                    # print(f'Length mocap: {mocap_kinematics[f"knee_flexion_{selected_task.side}"].shape[0]}')

                    # fig, ax = plt.subplots(3, 2, figsize = (12, 12))


                    # ax[0, 0].plot(x_biplane + vicon_biplane_offset + lag, knee_kinematics[f'knee_flexion_{selected_task.side}'], color = 'gray', lw = 4, linestyle = '-', label = 'Biplane')
                    # ax[0, 0].scatter(x_biplane + vicon_biplane_offset + lag, knee_kinematics[f'knee_flexion_{selected_task.side}'], color = 'green', s = 10)
                    # ax[0, 0].plot(x_mocap + lag, mocap_kinematics[f'knee_flexion_{selected_task.side}'], linestyle = ':', color = 'k', lw = 2, label = 'Mocap')
                    # ax[0, 0].plot(mc10_kinematics[f'knee_flexion_{selected_task.side}'], linestyle = '-', color = 'r', lw = 2, label = 'MC10')

                    # ax[1, 0].plot(x_biplane + vicon_biplane_offset + lag, knee_kinematics[f'knee_adduction_{selected_task.side}'], color = 'gray', lw = 4, linestyle = '-', label = 'Biplane')
                    # ax[1, 0].plot(x_mocap + lag, mocap_kinematics[f'knee_adduction_{selected_task.side}'], linestyle = ':', color = 'k', lw = 2, label = 'Mocap')
                    # ax[1, 0].plot(mc10_kinematics[f'knee_adduction_{selected_task.side}'], linestyle = '-', color = 'r', lw = 2, label = 'MC10')

                    # ax[2, 0].plot(x_biplane + vicon_biplane_offset + lag, knee_kinematics[f'knee_rotation_{selected_task.side}'], color = 'gray', lw = 4, linestyle = '-', label = 'Biplane')
                    # ax[2, 0].plot(x_mocap + lag, mocap_kinematics[f'knee_rotation_{selected_task.side}'], linestyle = ':', color = 'k', lw = 2, label = 'Mocap')
                    # ax[2, 0].plot(mc10_kinematics[f'knee_rotation_{selected_task.side}'], linestyle = '-', color = 'r', lw = 2, label = 'MC10')


                    # ax[0, 1].plot(trimmed_knee_kinematics[f'knee_flexion_{selected_task.side}'], color = 'gray', lw = 4, linestyle = '-', label = 'Biplane')
                    # ax[0, 1].plot(trimmed_mocap_kinematics[f'knee_flexion_{selected_task.side}'], linestyle = ':', color = 'k', lw = 2, label = 'Mocap')
                    # ax[0, 1].plot(trimmed_mc10_kinematics[f'knee_flexion_{selected_task.side}'], linestyle = '-', color = 'r', lw = 2, label = 'MC10')

                    # ax[1, 1].plot(trimmed_knee_kinematics[f'knee_adduction_{selected_task.side}'], color = 'gray', lw = 4, linestyle = '-')
                    # ax[1, 1].plot(trimmed_mocap_kinematics[f'knee_adduction_{selected_task.side}'], linestyle = ':', color = 'k', lw = 2)
                    # ax[1, 1].plot(trimmed_mc10_kinematics[f'knee_adduction_{selected_task.side}'], linestyle = '-', color = 'r', lw = 2)

                    # ax[2, 1].plot(trimmed_knee_kinematics[f'knee_rotation_{selected_task.side}'], color = 'gray', lw = 4, linestyle = '-')
                    # ax[2, 1].plot(trimmed_mocap_kinematics[f'knee_rotation_{selected_task.side}'], linestyle = ':', color = 'k', lw = 2)
                    # ax[2, 1].plot(trimmed_mc10_kinematics[f'knee_rotation_{selected_task.side}'], linestyle = '-', color = 'r', lw = 2)


                    # # ax.plot(x_biplane + set_offset, knee_kinematics[f'knee_flexion_{selected_task.side}'], color = 'gray', lw = 4, linestyle = '-', label = 'Biplane')
                    # # ax.plot(x_mocap, mocap_kinematics[f'knee_flexion_{selected_task.side}'], linestyle = ':', color = 'k', lw = 2, label = 'Mocap')


                    # plt.show()



                    # # breakpoint()











