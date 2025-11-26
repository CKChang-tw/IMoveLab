# name: preprocessing_mvn.py
# description: preprocess data collected from the MVN software
# author: Vu Phan
# date: 2025/01/21


import pandas as pd 
import numpy as np 
from tqdm import tqdm 
from scipy import signal 

import quaternion

from imu_benchmark.constants import constant_common, constant_mt, constant_mvn


def quat_dot(q1, q2):
    return q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2] + q1[3]*q2[3]


def quat_abs(q):
    return -q if q[0] < 0 else q


def quat_unrolling(q_arr):
    q_arr[0] = quat_abs(q_arr[0])

    for i in range(1, q_arr.shape[0]):
        if quat_dot(q_arr[i], q_arr[i-1]) < 0:
            q_arr[i] = -q_arr[i]

    return q_arr


# TODO: interpolating missing quaternions by checking norm == 1 or not
def quat_missing_interpolation(q_arr):
    for i in range(q_arr.shape[0]):
        if np.abs(np.linalg.norm(q_arr[i]) - 1) > 0.1:
            q_arr[i] = np.nan*np.ones(4)

    nan_id  = np.arange(0, q_arr.shape[0], 1)
    q_frame = pd.DataFrame(q_arr, columns = ['q0', 'q1', 'q2', 'q3'], index = nan_id)
    q_frame = q_frame.interpolate(method = 'linear', limit_area = 'inside')

    return q_frame.to_numpy()


def get_all_data_mvn(subject, task, sensor_config, sheet_name):
    ''' Get all data from MVN

    Args:
        + subject (int): subject id
        + task (str): task being performed, e.g., static, walking, squat, etc.
        + sensor_config (dict): configuration of sensors
        + sheet_name (str): orientation, accelerometer, or kinematics from the MVN software

    Returns:
        + mvn_out (dict of pd.DataFrame): data from all sensors
    '''
    mvn_fn = constant_common.IN_LAB_PATH + 's' + str(subject) + '/' + constant_common.MT_PATH + constant_common.LAB_TASK_NAME_MAP[task] + constant_common.MVN_EXTENSION
    mvn_dt = pd.read_excel(mvn_fn, sheet_name = sheet_name)

    if sheet_name == constant_mvn.MVN_ORIENTATION_SHEET:
        mvn_out = {}
        for sensor_name in sensor_config.keys():
            id_arr = []
            for q in ['q0', 'q1', 'q2', 'q3']:
                id_arr.append(constant_mvn.MVN_PLACEMENT_MAP[sensor_name] + ' ' + q)

            # mvn_out[sensor_name] = quaternion.as_quat_array(mvn_dt[id_arr].to_numpy())
            mvn_out[sensor_name] = mvn_dt[id_arr].to_numpy()
            mvn_out[sensor_name] = quat_unrolling(mvn_out[sensor_name])
            mvn_out[sensor_name] = quat_missing_interpolation(mvn_out[sensor_name])
            mvn_out[sensor_name] = quaternion.as_quat_array(mvn_out[sensor_name])

    elif sheet_name == constant_mvn.MVN_ACCELERATION_SHEET:
        pass # TODO

    elif sheet_name == constant_mvn.MVN_JOINT_ANGLE_SHEET:
        pass # TODO

    return mvn_out













