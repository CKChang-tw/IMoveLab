# name: run_mvn.py
# description: run unconstrained IK on MVN data
# author: Vu Phan
# date: 2025/01/15


import pandas as pd 
import numpy as np 
import quaternion
import pickle
import time

from imu_benchmark.constants import constant_common, constant_mt, constant_mocap, constant_mvn
from imu_benchmark.utils import common
from imu_benchmark.utils.mt import preprocessing_mt, calibration_mt, ik_mt, preprocessing_mvn


def mvn_ik(subject, task, remove_offset):
    ''' Get joint angles from MVN data

    Args:
        + subject (int): subject number
        + task (str): task being performed
        + remove_offset (bool): remove offset from the data

    Returns:
        + NA
    '''

    subject_list = common.get_subject_list(subject)
    task_list    = common.get_task_list_mvn(task)

    for subject in subject_list:
        print('*** Subject ' + str(subject))

        selected_setup = 'mm'
        f_type         = 'Xsens'
        dim            = '9d'
        f_params       = common.get_filter_params(f_type)

        sensor_config  = {'pelvis': 'PELVIS', 
                          'foot_r': 'FOOT_R', 'shank_r': 'SHANK_R_' + selected_setup[0].upper(), 'thigh_r': 'THIGH_R_' + selected_setup[1].upper(),
                          'foot_l': 'FOOT_L', 'shank_l': 'SHANK_L_' + selected_setup[0].upper(), 'thigh_l': 'THIGH_L_' + selected_setup[1].upper()}

        print('- Find sensor-to-segment calibration')
        task_static     = 'static'
        data_static_mt  = preprocessing_mt.get_all_data_mt(subject, task_static, sensor_config)
        data_static_mt  = preprocessing_mt.match_data_mt(data_static_mt) 
        task_walking    = 'treadmill_walking' 
        data_walking_mt = preprocessing_mt.get_all_data_mt(subject, task_walking, sensor_config)
        task_jumping    = 'cmj' 
        data_jumping_mt = preprocessing_mt.get_all_data_mt(subject, task_jumping, sensor_config)
        
        walking_period = calibration_mt.get_walking_4_calib(data_walking_mt['shank_r']['Gyr_Z'].to_numpy())
        jumping_period = [0, data_jumping_mt['pelvis']['Gyr_Y'].shape[0]]

        seg2sens = calibration_mt.sensor_to_segment_mt(data_static_mt, data_walking_mt, walking_period, data_jumping_mt, jumping_period, selected_setup)
        
        if remove_offset:
            print('- Find static offsets')
            static_orientation_mt = ik_mt.get_imu_orientation_mt(data_static_mt, f_type = f_type, fs = constant_mt.MT_SAMPLING_RATE, dim = dim.upper(), params = f_params)
            static_ja_mt          = ik_mt.get_all_ja_mt(seg2sens, static_orientation_mt)
            static_offset_mt      = ik_mt.get_static_offset_mt(static_ja_mt) 


        for selected_task in task_list:
            print('*** Task ' + selected_task)
            orientation_mvn = preprocessing_mvn.get_all_data_mvn(subject, selected_task, sensor_config, sheet_name = constant_mvn.MVN_ORIENTATION_SHEET)

            print('- Estimate joint angles')
            ja_mvn = ik_mt.get_all_ja_mt(seg2sens, orientation_mvn)

            if remove_offset:
                title_offset = '_roffset'
                print('- Remove offsets') 
                for joint in ja_mvn.keys():
                    ja_mvn[joint] = ja_mvn[joint] - static_offset_mt[joint]
            else:
                title_offset = ''

            # import matplotlib.pyplot as plt
            # fig, ax = plt.subplots(5, 2, figsize = (20, 10), sharex = True, sharey = True)
            # count = 0
            # for joint in ja_mvn.keys():
            #     ax[count%5, count//5].plot(ja_mvn[joint], label = 'mvn')
            #     ax[count%5, count//5].set_title(joint)
            #     count += 1

            # # test = quaternion.as_float_array(orientation_mvn['thigh_l'])
            # # # test_old = 1*test
            # # # test[0] = quat_abs(test[0])
            # # # for i in range(1, test.shape[0]):
            # # #     if quat_dot(test[i], test[i-1]) < 0:
            # # #         test[i] = -test[i]

            # # plt.plot(test)
            # # # fig, ax = plt.subplots(2, 1, sharex = True, sharey = True)

            # # # ax[1].plot(test)
            # # # ax[1].plot(np.linalg.norm(test, axis = 1), color = 'k', linestyle = 'solid')

            # # # ax[0].plot(test_old)
            # # # ax[0].plot(np.linalg.norm(test_old, axis = 1), color = 'k', linestyle = 'solid')

            # plt.show()
            # breakpoint()

            print('- Apply synchronization')
            sync_fn = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + selected_task + '.pkl'
            with open(sync_fn, 'rb') as f:
                sync_info = pickle.load(f)

            if sync_info['first_start'] == 'imu':
                for joint in ja_mvn.keys():
                    ja_mvn[joint] = ja_mvn[joint][sync_info['shifting_id']:]

            print('- Save results of ' + selected_task)
            common.mkfolder(constant_common.OUT_MT_JA_PATH)
            if selected_setup == 'mm':
                filename = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + selected_task + title_offset + '.pkl'
            else:
                filename = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + selected_task + '_' + selected_setup + title_offset + '.pkl'
            with open(filename, 'wb') as f:
                pickle.dump(ja_mvn, f)
            











