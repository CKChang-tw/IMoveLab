# name: run_eval.py
# description: evaluate kinematics compared to the mocap-based reference
# author: Vu Phan
# date: 2024/09/23


import numpy as np
import copy
import quaternion

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt
from imu_benchmark.utils import common
from imu_benchmark.utils.mocap import ik_mocap
from imu_benchmark.utils.eval import eval_utils, eval_segment
from imu_benchmark.utils.mt import preprocessing_mt, calibration_mt, ik_mt
from imu_benchmark.utils.mocap import preprocessing_mocap


def evaluate(f_type, dim, subject, task, reference, mocap_alignment, selected_setup, enable_opensense, enable_psa):
    ''' tbd '''
    subject_list = common.get_subject_list(subject)
    task_list    = common.get_task_list(task)
    filter_list  = common.get_filter_list(f_type, dim.upper())

    if enable_psa:
        psa_str = '_psa'
    else:
        psa_str = ''

    for f_type in filter_list:
        print('*** Filter ' + f_type)

        for subject in subject_list:
            print('*** Subject ' + str(subject))
            print('*** Sensor axes ' + dim.upper())

            for task in task_list:
                print('*** Task ' + task)

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

                if selected_setup == 'mm':
                    filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + psa_str + '.pkl'
                    if enable_opensense:
                        filename_os = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '.pkl'
                else:
                    filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + psa_str + '.pkl'

                ja_mt = eval_utils.load_data(filename_mt)
                if enable_opensense:
                    ja_os = eval_utils.load_data(filename_os)

                    rename_keys = {'ankle_angle_r': 'ankle_flexion_r', 'ankle_angle_l': 'ankle_flexion_l'}
                    for old_key, new_key in rename_keys.items():
                        ja_os[new_key] = ja_os.pop(old_key)

                    # XXX: hardcoded as these are not available in OpenSense outputs
                    ja_os['knee_adduction_r'] = np.zeros(ja_os['knee_flexion_r'].shape)
                    ja_os['knee_adduction_l'] = np.zeros(ja_os['knee_flexion_l'].shape)
                    ja_os['knee_rotation_r'] = np.zeros(ja_os['knee_flexion_r'].shape)
                    ja_os['knee_rotation_l'] = np.zeros(ja_os['knee_flexion_l'].shape)
                    ja_os['ankle_adduction_r'] = np.zeros(ja_os['ankle_flexion_r'].shape)
                    ja_os['ankle_adduction_l'] = np.zeros(ja_os['ankle_flexion_l'].shape)
                    ja_os['ankle_rotation_r'] = np.zeros(ja_os['ankle_flexion_r'].shape)
                    ja_os['ankle_rotation_l'] = np.zeros(ja_os['ankle_flexion_l'].shape)


                print('- Resync the data if lagged')
                lag                 = eval_utils.find_lag(ja_mt['knee_flexion_r'], ja_mc['knee_flexion_r'])
                if enable_opensense:
                    ja_mc, ja_mt, ja_os = eval_utils.do_resync(ja_mc, ja_mt, ja_os, lag)
                else:
                    ja_mc, ja_mt, _ = eval_utils.do_resync(ja_mc, ja_mt, copy.deepcopy(ja_mt), lag)

                
                if mocap_alignment:
                    title_alignment = '_alignment'

                    if subject in list(constant_common.ISOLATED_CASES.keys()):
                        if task in constant_common.ISOLATED_CASES[subject].keys():
                            alignment_id = [constant_common.ISOLATED_CASES[subject][task][0], constant_common.ISOLATED_CASES[subject][task][1]]
                        else:
                            alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]

                    else:
                        alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]
                    
                    ja_mt = eval_utils.get_ja_alignment(ja_mt, ja_mc, alignment_id, task)

                    if enable_opensense:
                        ja_os = eval_utils.get_ja_alignment(ja_os, ja_mc, alignment_id, task)

                    # f_params = common.get_filter_params(f_type)

                    # sensor_config  = {'pelvis': 'PELVIS', 
                    #                   'foot_r': 'FOOT_R', 'shank_r': 'SHANK_R_' + selected_setup[0].upper(), 'thigh_r': 'THIGH_R_' + selected_setup[1].upper(),
                    #                   'foot_l': 'FOOT_L', 'shank_l': 'SHANK_L_' + selected_setup[0].upper(), 'thigh_l': 'THIGH_L_' + selected_setup[1].upper()}

                    # task_static     = 'static'
                    # data_static_mt  = preprocessing_mt.get_all_data_mt(subject, task_static, sensor_config)
                    # data_static_mt  = preprocessing_mt.match_data_mt(data_static_mt) 
                    # task_walking    = 'treadmill_walking' 
                    # data_walking_mt = preprocessing_mt.get_all_data_mt(subject, task_walking, sensor_config)
                    # task_jumping    = 'cmj' 
                    # data_jumping_mt = preprocessing_mt.get_all_data_mt(subject, task_jumping, sensor_config)

                    # if selected_setup[0].upper() == 'F':
                    #     walking_period = calibration_mt.get_walking_4_calib(data_walking_mt['shank_r']['Gyr_Y'].to_numpy())
                    # else:
                    #     walking_period = calibration_mt.get_walking_4_calib(data_walking_mt['shank_r']['Gyr_Z'].to_numpy())
                    
                    # jumping_period = [0, data_jumping_mt['pelvis']['Gyr_Y'].shape[0]]

                    # seg2sens = calibration_mt.sensor_to_segment_mt(data_static_mt, data_walking_mt, walking_period, data_jumping_mt, jumping_period, selected_setup)

                    # if dim.upper() == '6D':
                    #     print('(Perfect standing assumption for 6D filters)')
                    #     initial_orientation = {}
                    #     for sensor_name in seg2sens.keys():
                    #         initial_orientation[sensor_name] = quaternion.from_rotation_matrix(np.identity(3))*quaternion.from_rotation_matrix(seg2sens[sensor_name])

                    # static_orientation_mt = ik_mt.get_imu_orientation_mt(data_static_mt, f_type = f_type, fs = constant_mt.MT_SAMPLING_RATE, dim = dim.upper(), params = f_params)
                    # if dim.upper() == '6D':
                    #     static_orientation_mt = calibration_mt.correct_random_6D_orientation(initial_orientation, static_orientation_mt)
                        
                    # ja_mt_static = ik_mt.get_all_ja_mt(seg2sens, static_orientation_mt)

                    # data_static_mocap     = preprocessing_mocap.get_data_mocap(subject, task_static)
                    # data_static_mocap     = data_static_mocap.interpolate(method = 'cubic')
                    # data_static_mocap     = data_static_mocap.fillna(value = constant_common.VERY_HIGH_NUMBER)
                    # data_static_mocap_avg = preprocessing_mocap.get_avg_data(data_static_mocap)

                    # print('- Calibrate mocap')
                    # static_orientation_mocap_avg = ik_mocap.get_orientation_mocap(data_static_mocap_avg, cluster_use = True, task = task_static)
                    # static_orientation_mocap     = ik_mocap.get_orientation_mocap(data_static_mocap, cluster_use = True, task = task_static)
                    # cal_orientation_mocap        = ik_mocap.calibration_mocap(static_orientation_mocap_avg, cluster_use = True)
                    # ja_mc_static                 = ik_mocap.get_all_ja_mocap(cal_orientation_mocap, static_orientation_mocap, cluster_use = True)

                    # ja_mt = eval_utils.get_ja_alignment_static(ja_mt, ja_mc, task, ja_mt_static, ja_mc_static, store_correction = False)
                
                else:
                    title_alignment = ''


                print('- Segment the data into gait cycles or exercise reps')
                event = eval_segment.get_events(subject, task, lag)
                
                segment_mc = eval_segment.get_segment(ja_mc, event, task)
                segment_mt = eval_segment.get_segment(ja_mt, event, task)
                if enable_opensense:
                    segment_os = eval_segment.get_segment(ja_os, event, task)


                print('- Evaluate the RMSE')
                rmse_mt = eval_utils.calculate_rmse(segment_mc, segment_mt)
                print(rmse_mt)
                if enable_opensense:
                    rmse_os = eval_utils.calculate_rmse(segment_mc, segment_os)
                
                print('- Save the evaluation results')
                common.mkfolder(constant_common.OUT_RMSE_PATH)
                if selected_setup == 'mm':
                    filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + reference + title_alignment + '_mt' + psa_str + '.pkl'
                    if enable_opensense:
                        filename_os = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + reference + title_alignment + '_os' + '.pkl'
                else:
                    filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + '_' + reference + title_alignment + '_mt' + psa_str + '.pkl'
                    
                eval_utils.save_data(rmse_mt, filename_mt)
                if enable_opensense:
                    print('\n\n\n')
                    eval_utils.save_data(rmse_os, filename_os)













