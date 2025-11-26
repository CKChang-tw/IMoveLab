# name: plot.py
# description: plot the results
# author: Vu Phan
# date: 2024/09/23


import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

import copy

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt, constant_mvn
from imu_benchmark.utils.eval import eval_utils
from imu_benchmark.utils.mocap import ik_mocap
from imu_benchmark.utils.eval import eval_segment


def plot_raw(f_type, dim, subject, task, joint, reference, remove_offset, add_peaks, selected_setup = 'mm', source = 'mt'):

    print('*** Subject ' + str(subject))

    if remove_offset:
        title_offset = '_roffset'
    else:
        title_offset = ''

    if reference == 'direct':
        filename_mc = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + str(subject) + '_' + task + title_offset + '.pkl'
        ja_mc = eval_utils.load_data(filename_mc)
        
    else:
        filename_mc = constant_common.IN_LAB_PATH + 's' + str(subject) + '/' + constant_common.MOCAP_OPENSIM_PATH  + constant_common.LAB_TASK_NAME_MAP[task] + '/ik.mot'
        ja_mc = ik_mocap.get_all_ja_os(filename_mc, constant_mt.MT_SAMPLING_RATE)

        sync_fn   = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + task + '.pkl'
        sync_info = eval_utils.load_data(sync_fn)

        if sync_info['first_start'] == 'mocap':
            shifting_id = sync_info['shifting_id']
            ja_mc = eval_utils.resync_data(ja_mc, shifting_id)

    if selected_setup == 'mm':
        filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
        filename_os = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
    else:
        filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + title_offset + '.pkl'
        # filename_os = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + title_offset + '.pkl'

    ja_mt = eval_utils.load_data(filename_mt)
    if selected_setup == 'mm':
        ja_os = eval_utils.load_data(filename_os)

    print('- Resync the data if lagged')
    lag                 = eval_utils.find_lag(ja_mt['knee_flexion_r'], ja_mc['knee_flexion_r'])
    print('lag: ', lag)
    if selected_setup == 'mm':
        ja_mc, ja_mt, ja_os = eval_utils.do_resync(ja_mc, ja_mt, ja_os, lag)
    else:
        ja_mc, ja_mt, _ = eval_utils.do_resync(ja_mc, ja_mt, copy.deepcopy(ja_mt), lag)


    # # TODO: remove the offset
    # for key in ja_mc.keys():
    #     if task == 'sts_x':
    #         ja_mc[key] -= np.mean(ja_mc[key][0:100])
    #         ja_mt[key] -= np.mean(ja_mt[key][0:100])
    #         # if selected_setup == 'mm':
    #         #     ja_os[key] -= np.mean(ja_os[key][0:100])
    #     else:
    #         if np.isnan(ja_mc[key]).any() or (subject == 5 and task == 'treadmill_walking') or (subject == 11 and task == 'treadmill_running'):
    #             pass 
    #         elif subject == 18:
    #             if task == 'lat_step':
    #                 ja_mc[key] -= np.mean(ja_mc[key][210:220])
    #                 ja_mt[key] -= np.mean(ja_mt[key][210:220])
    #                 # if selected_setup == 'mm':
    #                 #     ja_os[key] -= np.mean(ja_os[key][210:220])
    #             elif task == 'walking':
    #                 ja_mc[key] -= np.mean(ja_mc[key][550:570])
    #                 ja_mt[key] -= np.mean(ja_mt[key][550:570])
    #                 # if selected_setup == 'mm':
    #                 #     ja_os[key] -= np.mean(ja_os[key][550:570])
    #             else:
    #                 ja_mc[key] -= np.mean(ja_mc[key][0:100])
    #                 ja_mt[key] -= np.mean(ja_mt[key][0:100])
    #                 # if selected_setup == 'mm':
    #                 #     ja_os[key] -= np.mean(ja_os[key][0:100])
    #         elif (subject == 7) and ('walking' in task or 'running' in task):
    #             ja_os[key] -= np.mean(ja_os[key][0:100])
    #         else:
    #             ja_mc[key] -= np.mean(ja_mc[key][0:100])
    #             ja_mt[key] -= np.mean(ja_mt[key][0:100])
    #             # if selected_setup == 'mm':
    #             #     ja_os[key] -= np.mean(ja_os[key][0:100])

    
    fig, ax = plt.subplots(1, 1, figsize = (10, 5))

    ax.plot(ja_mc[joint], color = 'black', linestyle = '-', label = joint)
    if joint == 'knee_flexion_r':
        ax.plot(ja_mc['knee_flexion_l'], color = 'lightgray', linestyle = '-', label = 'knee_flexion_l')
    else:
        ax.plot(ja_mc['knee_flexion_r'], color = 'lightgray', linestyle = '-', label = 'knee_flexion_r')
    ax.plot(ja_mt[joint], label = 'mt', color = '#89A6FB')
    # if selected_setup == 'mm':
    #     ax.plot(ja_os[joint], label = 'os', color = '#98CE00')

    if add_peaks:
        peaks, _ = find_peaks(-1*ja_mc[joint], height = -50)
        ax.plot(peaks, ja_mc[joint][peaks], "x", color = 'r', label = 'mocap peaks')


    # XXX
    if source == 'mt':
        event = eval_segment.get_events(subject, task, lag)
    else:
        event = eval_segment.get_events(subject, task, lag, fs = constant_mvn.MVN_SAMPLING_RATE)

    # breakpoint()
    ax.plot(event[joint[-1]], ja_mc[joint][event[joint[-1]]], 'o', color = 'r', label = 'start')
    
    
    ax.legend()

    plt.show()



def plot_segmented(f_type, dim, subject, task, joint, reference, remove_offset, selected_setup = 'mm', source = 'mt'):
    
    if remove_offset:
        title_offset = '_roffset'
    else:
        title_offset = ''

    if reference == 'direct':
        filename_mc = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + str(subject) + '_' + task + title_offset + '.pkl'
        ja_mc = eval_utils.load_data(filename_mc)

    else:
        filename_mc = constant_common.IN_LAB_PATH + 's' + str(subject) + '/' + constant_common.MOCAP_OPENSIM_PATH  + constant_common.LAB_TASK_NAME_MAP[task] + '/ik.mot'
        ja_mc = ik_mocap.get_all_ja_os(filename_mc, constant_mt.MT_SAMPLING_RATE)

        sync_fn   = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + task + '.pkl'
        sync_info = eval_utils.load_data(sync_fn)

        if sync_info['first_start'] == 'mocap':
            shifting_id = sync_info['shifting_id']
            ja_mc = eval_utils.resync_data(ja_mc, shifting_id)

    if selected_setup == 'mm':
        filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
        filename_os = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
    else:
        filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + title_offset + '.pkl'
        # filename_os = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + title_offset + '.pkl'

    ja_mt = eval_utils.load_data(filename_mt)
    if selected_setup == 'mm':
        ja_os = eval_utils.load_data(filename_os)

    print('- Resync the data if lagged')
    lag                 = eval_utils.find_lag(ja_mt['knee_flexion_r'], ja_mc['knee_flexion_r'])
    # print('lag: ', lag)
    if selected_setup == 'mm':
        ja_mc, ja_mt, ja_os = eval_utils.do_resync(ja_mc, ja_mt, ja_os, lag)
    else:
        ja_mc, ja_mt, _ = eval_utils.do_resync(ja_mc, ja_mt, copy.deepcopy(ja_mt), lag)


    # # TODO: remove the offset
    # for key in ja_mc.keys():
    #     if np.isnan(ja_mc[key]).any() or (subject == 5 and task == 'treadmill_walking') or (subject == 11 and task == 'treadmill_running'):
    #         pass 
    #     elif (subject == 18 and task == 'lat_step'):
    #         ja_mc[key] -= np.mean(ja_mc[key][210:220])
    #         ja_mt[key] -= np.mean(ja_mt[key][210:220])
    #         # if selected_setup == 'mm':
    #         #     ja_os[key] -= np.mean(ja_os[key][210:220])
    #     else:
    #         ja_mc[key] -= np.mean(ja_mc[key][0:100])
    #         ja_mt[key] -= np.mean(ja_mt[key][0:100])
    #         # if selected_setup == 'mm':
    #         #     ja_os[key] -= np.mean(ja_os[key][0:100])


    if source == 'mt':
        event = eval_segment.get_events(subject, task, lag)
    else:
        event = eval_segment.get_events(subject, task, lag, fs = constant_mvn.MVN_SAMPLING_RATE)

    # import matplotlib.pyplot as plt
    # breakpoint()

    if source == 'mt':
        segment_mc = eval_segment.get_segment(ja_mc, event, task)
        segment_mt = eval_segment.get_segment(ja_mt, event, task)
        # if selected_setup == 'mm':
        #     segment_os = eval_segment.get_segment(ja_os, event, task)
    else:
        segment_mc = eval_segment.get_segment(ja_mc, event, task, fs = constant_mvn.MVN_SAMPLING_RATE)
        segment_mt = eval_segment.get_segment(ja_mt, event, task, fs = constant_mvn.MVN_SAMPLING_RATE)
        # segment_os = eval_segment.get_segment(ja_os, event, task, fs = constant_mvn.MVN_SAMPLING_RATE)

    # breakpoint()

    fig, ax = plt.subplots(1, 1, figsize = (10, 5))

    ax.plot(np.mean(segment_mc[joint], axis = 0), color = 'black', linestyle = '--', label = 'Reference')
    ax.fill_between(np.arange(segment_mc[joint].shape[1]), np.mean(segment_mc[joint], axis = 0) - np.std(segment_mc[joint], axis = 0), np.mean(segment_mc[joint], axis = 0) + np.std(segment_mc[joint], axis = 0), color = 'black', alpha = 0.2)
    ax.plot(np.mean(segment_mt[joint], axis = 0), color = '#89A6FB', label = 'Unconstrained')
    ax.fill_between(np.arange(segment_mt[joint].shape[1]), np.mean(segment_mt[joint], axis = 0) - np.std(segment_mt[joint], axis = 0), np.mean(segment_mt[joint], axis = 0) + np.std(segment_mt[joint], axis = 0), color = '#89A6FB', alpha = 0.2)
    # if selected_setup == 'mm':
    #     ax.plot(np.mean(segment_os[joint], axis = 0), color = '#98CE00', label = 'OpenSense')
    #     ax.fill_between(np.arange(segment_os[joint].shape[1]), np.mean(segment_os[joint], axis = 0) - np.std(segment_os[joint], axis = 0), np.mean(segment_os[joint], axis = 0) + np.std(segment_os[joint], axis = 0), color = '#98CE00', alpha = 0.2)

    ax.legend()

    plt.show()




