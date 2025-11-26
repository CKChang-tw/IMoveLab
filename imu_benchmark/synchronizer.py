# name: synchronizer.py
# description: return sync indices for mocap and IMU data
# author: Vu Phan
# date: 2024/09/15


import argparse
import pickle
import pandas as pd
import quaternion

import numpy as np
from scipy.spatial.transform import Rotation as R

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt, constant_mvn
from imu_benchmark.utils import common, synchronization
from imu_benchmark.utils.mocap import preprocessing_mocap
from imu_benchmark.utils.mt import preprocessing_mt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', type = int, default = None) # subject number, if not specified, run all subjects
    parser.add_argument('--task', type = str, default = None) # task being performed, if not specified, run all tasks

    parser.add_argument('--do_mvn', action = 'store_true') # run IMU data collected from MVN instead of MTw Manager

    args = parser.parse_args()

    if args.do_mvn:
        # pass # TODO: implement this function
        subject_list = common.get_subject_list(args.subject)
        task_list    = common.get_task_list_mvn(args.task)

        for subject in subject_list:
            print('*** Subject ' + str(subject))

            for selected_task in task_list:
                print('*** TASK: ' + selected_task)

                print('- Obtain mocap data')
                data_mocap = preprocessing_mocap.get_data_mocap(subject, selected_task)
                data_mocap = data_mocap.fillna(value = constant_common.VERY_HIGH_NUMBER)
                data_mocap = preprocessing_mocap.lowpass_filter_mocap(data_mocap, constant_mocap.MOCAP_SAMPLING_RATE,
                                                                    constant_mocap.FILTER_CUTOFF_MOCAP,
                                                                    constant_mocap.FILTER_ORDER)
                if (subject == 13) and ((selected_task == 'walking_x') or (selected_task == 'running_x')):
                    pass 
                else:                                                                 
                    data_mocap = preprocessing_mocap.resample_mocap(data_mocap, constant_mvn.MVN_SAMPLING_RATE)

                sensor_name = 'pelvis'
                mvn_fn = constant_common.IN_LAB_PATH + 's' + str(subject) + '/' + constant_common.MT_PATH + constant_common.LAB_TASK_NAME_MAP[selected_task] + constant_common.MVN_EXTENSION

                print('- Obtain free acceleration of the pelvis IMU')
                dt_acc = pd.read_excel(mvn_fn, sheet_name = constant_mvn.MVN_ACCELERATION_SHEET)

                id_arr = []
                for ax in ['x', 'y', 'z']:
                    id_arr.append(constant_mvn.MVN_PLACEMENT_MAP[sensor_name] + ' ' + ax)
                free_acc = dt_acc[id_arr].to_numpy()

                print('- Obtain orientation of the pelvis IMU')
                dt_ori = pd.read_excel(mvn_fn, sheet_name = constant_mvn.MVN_ORIENTATION_SHEET)

                id_arr = []
                for q in ['q0', 'q1', 'q2', 'q3']:
                    id_arr.append(constant_mvn.MVN_PLACEMENT_MAP[sensor_name] + ' ' + q)
                orientation = quaternion.as_quat_array(dt_ori[id_arr].to_numpy())

                print('- Convert free acceleration to raw acceleration')
                for i in range(free_acc.shape[0]):
                    temp_quat = quaternion.as_float_array(orientation[i])
                    rot_mat   = R.from_quat(temp_quat).as_matrix()
                    free_acc[i] = 1*free_acc[i] + np.array([0, 0, constant_mt.EARTH_G_ACC])
                    free_acc[i] = rot_mat.T @ free_acc[i]
                    free_acc[i] *= -1

                # import matplotlib.pyplot as plt
                # breakpoint()

                print('- Obtain sync info')
                if selected_task in ['sts_x']:
                    iters = 600 
                else:
                    iters = 1500

                if (subject == 13) and ((selected_task == 'walking_x') or (selected_task == 'running_x')):
                    first_start, shifting_id = synchronization.get_sync_info(data_mocap, free_acc, fs = constant_mocap.MOCAP_SAMPLING_RATE, source = 'mvn', iters = iters)
                else:
                    first_start, shifting_id = synchronization.get_sync_info(data_mocap, free_acc, fs = constant_mvn.MVN_SAMPLING_RATE, source = 'mvn', iters = iters)

                print('\n- First start: ' + str(first_start))
                print('- Shifting ID: ' + str(shifting_id) + '\n')

                print('- Save sync info of ' + selected_task)
                sync_info = {'first_start': first_start, 'shifting_id': shifting_id}
                common.mkfolder(constant_common.OUT_SYNC_INFO)
                filename = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + selected_task + '.pkl'
                with open(filename, 'wb') as f:
                    pickle.dump(sync_info, f)

    else:
        subject_list = common.get_subject_list(args.subject)
        task_list    = common.get_task_list(args.task)

        for subject in subject_list:
            print('*** Subject ' + str(subject))

            for selected_task in task_list:
                print('*** TASK: ' + selected_task)

                # try:
                print('- Obtain mocap data')
                data_mocap = preprocessing_mocap.get_data_mocap(subject, selected_task)
                data_mocap = data_mocap.fillna(value = constant_common.VERY_HIGH_NUMBER)
                data_mocap = preprocessing_mocap.lowpass_filter_mocap(data_mocap, constant_mocap.MOCAP_SAMPLING_RATE,
                                                                    constant_mocap.FILTER_CUTOFF_MOCAP,
                                                                    constant_mocap.FILTER_ORDER) 
                data_mocap = preprocessing_mocap.resample_mocap(data_mocap, constant_mt.MT_SAMPLING_RATE)

                print('- Obtain pelvis IMU data')
                sensor_name = 'pelvis'
                sensor_id   = constant_mt.LAB_IMU_NAME_MAP[sensor_name.upper()]
                mt_fn       = preprocessing_mt.get_data_path_mt(subject, selected_task, sensor_id)
                data_mt     = preprocessing_mt.load_data_mt(mt_fn)

                print('- Obtain sync info')
                if selected_task in ['lat_step', 'step_up_down', 'drop_jump', 'cmj', 'squat', 'step_n_hold', 'sls', 'sts']:
                    iters = 600 
                else:
                    iters = 1500

                first_start, shifting_id = synchronization.get_sync_info(data_mocap, data_mt, iters = iters)
                print('\n- First start: ' + str(first_start))
                print('- Shifting ID: ' + str(shifting_id) + '\n')

                print('- Save sync info of ' + selected_task)
                sync_info = {'first_start': first_start, 'shifting_id': shifting_id}
                common.mkfolder(constant_common.OUT_SYNC_INFO)
                filename = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + selected_task + '.pkl'
                with open(filename, 'wb') as f:
                    pickle.dump(sync_info, f)
                
                # except:
                #     print('*** Error in processing ' + selected_task)


if __name__ == '__main__':
    main()



