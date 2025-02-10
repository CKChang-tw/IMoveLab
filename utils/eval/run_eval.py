# name: run_eval.py
# description: evaluate kinematics compared to the mocap-based reference
# author: Vu Phan
# date: 2024/09/23


import numpy as np
import copy

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt
from imu_benchmark.utils import common
from imu_benchmark.utils.mocap import ik_mocap
from imu_benchmark.utils.eval import eval_utils, eval_segment


def evaluate(f_type, dim, subject, task, reference, remove_offset, selected_setup, enable_opensense):
    ''' tbd '''
    subject_list = common.get_subject_list(subject)
    task_list    = common.get_task_list(task)
    filter_list  = common.get_filter_list(f_type, dim.upper())

    for f_type in filter_list:
        print('*** Filter ' + f_type)

        for subject in subject_list:
            print('*** Subject ' + str(subject))
            print('*** Sensor axes ' + dim.upper())

            for task in task_list:
                print('*** Task ' + task)

                # try:

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
                    if enable_opensense:
                        filename_os = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
                else:
                    filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + title_offset + '.pkl'

                ja_mt = eval_utils.load_data(filename_mt)
                if enable_opensense:
                    ja_os = eval_utils.load_data(filename_os)

                print('- Resync the data if lagged')
                lag                 = eval_utils.find_lag(ja_mt['knee_flexion_r'], ja_mc['knee_flexion_r'])
                if enable_opensense:
                    ja_mc, ja_mt, ja_os = eval_utils.do_resync(ja_mc, ja_mt, ja_os, lag)
                else:
                    ja_mc, ja_mt, _ = eval_utils.do_resync(ja_mc, ja_mt, copy.deepcopy(ja_mt), lag)

                # Remove offset at the static standing at the beginning
                for key in ja_mc.keys():
                    if np.isnan(ja_mc[key]).any() or (subject == 5 and task == 'treadmill_walking') or (subject == 11 and task == 'treadmill_running'):
                        pass 
                    elif subject == 18:
                        if task == 'lat_step':
                            ja_mc[key] -= np.mean(ja_mc[key][210:220])
                            ja_mt[key] -= np.mean(ja_mt[key][210:220])
                            if selected_setup == 'mm':
                                if enable_opensense:
                                    ja_os[key] -= np.mean(ja_os[key][210:220])
                        elif task == 'walking':
                            ja_mc[key] -= np.mean(ja_mc[key][550:570])
                            ja_mt[key] -= np.mean(ja_mt[key][550:570])
                            if selected_setup == 'mm':
                                if enable_opensense:
                                    ja_os[key] -= np.mean(ja_os[key][550:570])
                        else:
                            ja_mc[key] -= np.mean(ja_mc[key][0:100])
                            ja_mt[key] -= np.mean(ja_mt[key][0:100])
                            if selected_setup == 'mm':
                                if enable_opensense:
                                    ja_os[key] -= np.mean(ja_os[key][0:100])
                    elif (subject == 7) and ('walking' in task or 'running' in task):
                        if selected_setup == 'mm':
                            if enable_opensense:
                                ja_os[key] -= np.mean(ja_os[key][0:100])
                    else:
                        ja_mc[key] -= np.mean(ja_mc[key][0:100])
                        ja_mt[key] -= np.mean(ja_mt[key][0:100])
                        if selected_setup == 'mm':
                            if enable_opensense:
                                ja_os[key] -= np.mean(ja_os[key][0:100])

                print('- Segment the data into gait cycles or exercise reps')
                event = eval_segment.get_events(subject, task, lag)
                
                segment_mc = eval_segment.get_segment(ja_mc, event, task)
                segment_mt = eval_segment.get_segment(ja_mt, event, task)
                if enable_opensense:
                    segment_os = eval_segment.get_segment(ja_os, event, task)


                # import matplotlib.pyplot as plt
                # fig, ax = plt.subplots(1, 1, figsize = (10, 5))

                # # joint = 'knee_flexion_r'
                # joint = 'hip_flexion_r'

                # ax.plot(np.mean(segment_mc[joint], axis = 0), color = 'black', linestyle = '--', label = 'Reference')
                # ax.fill_between(np.arange(segment_mc[joint].shape[1]), np.mean(segment_mc[joint], axis = 0) - np.std(segment_mc[joint], axis = 0), np.mean(segment_mc[joint], axis = 0) + np.std(segment_mc[joint], axis = 0), color = 'black', alpha = 0.2)
                # ax.plot(np.mean(segment_mt[joint], axis = 0), color = '#89A6FB', label = 'Unconstrained')
                # ax.fill_between(np.arange(segment_mt[joint].shape[1]), np.mean(segment_mt[joint], axis = 0) - np.std(segment_mt[joint], axis = 0), np.mean(segment_mt[joint], axis = 0) + np.std(segment_mt[joint], axis = 0), color = '#89A6FB', alpha = 0.2)
                # ax.plot(np.mean(segment_os[joint], axis = 0), color = '#98CE00', label = 'OpenSense')
                # ax.fill_between(np.arange(segment_os[joint].shape[1]), np.mean(segment_os[joint], axis = 0) - np.std(segment_os[joint], axis = 0), np.mean(segment_os[joint], axis = 0) + np.std(segment_os[joint], axis = 0), color = '#98CE00', alpha = 0.2)

                # ax.legend()

                # plt.show()

                print('- Evaluate the RMSE')
                rmse_mt = eval_utils.calculate_rmse(segment_mc, segment_mt)
                if enable_opensense:
                    rmse_os = eval_utils.calculate_rmse(segment_mc, segment_os)
                
                print('- Save the evaluation results')
                common.mkfolder(constant_common.OUT_RMSE_PATH)
                if selected_setup == 'mm':
                    filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '_' + reference + '_mt' + '.pkl'
                    if enable_opensense:
                        filename_os = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '_' + reference + '_os' + '.pkl'
                else:
                    filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + title_offset + '_' + reference + '_mt' + '.pkl'
                    
                eval_utils.save_data(rmse_mt, filename_mt)
                if enable_opensense:
                    print('\n\n\n')
                    eval_utils.save_data(rmse_os, filename_os)

                # except:
                #     print('*** Error in processing ' + task)












