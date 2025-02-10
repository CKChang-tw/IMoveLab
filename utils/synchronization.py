# name: synchronization.py
# description: Synchronize mocap and IMU data
# author: Vu Phan
# date: 2023/06/05


import numpy as np
import pandas as pd
import quaternion
from scipy.spatial.transform import Rotation as R
from scipy.signal import find_peaks

from imu_benchmark.constants import constant_mt
from imu_benchmark.utils.eval.metrics import get_rmse


# --- Get vertical acceleration from a specific IMU --- #
def get_vertical_acc_mt(one_imu_data, source = 'mt'):
    ''' Get vertical acceleration of an IMU data
    Args:
        + one_imu_data (pd.DataFrame): data from the desired sensor

    Returns:
        + vertical_acc_mt (np.array): vertical acceleration (gravity relatively removed)
    '''
    if source == 'mt':
        vertical_acc_mt = 1*one_imu_data['Acc_X'].to_numpy()
    elif source == 'mvn':
        vertical_acc_mt = 1*one_imu_data[:, 0]

    vertical_acc_mt -= constant_mt.EARTH_G_ACC

    return vertical_acc_mt

# --- Get vertical acceleration from a spcific marker --- #
def get_vertical_acc_mocap(one_marker_data, fs = constant_mt.MT_SAMPLING_RATE):
    ''' Get vertical acceleration of a marker

    Args:
        + one_marker_data (pd.DataFrame): vertical motion of a marker in the mocap data

    Returns:
        + vertical_acc_mocap (np.array): vertical acceleration
    '''
    vertical_acc_mocap = 1*one_marker_data.to_numpy()
    vertical_acc_mocap = np.diff(vertical_acc_mocap)/(1.0/fs)
    vertical_acc_mocap = np.diff(vertical_acc_mocap)/(1.0/fs)

    # padding = np.zeros(2)
    # vertical_acc_mocap = np.concatenate((padding, vertical_acc_mocap))

    return vertical_acc_mocap

# --- Identify the hop period with mocap data --- #
def get_hop_id_mocap(one_mocap_data):
    ''' Get hop id from mocap

    Args:
        + one_marker_data (pd.DataFrame): vertical motion of a marker in the mocap data

    Returns:
        + hop_id_mocap (int): id of the mid hop
    '''    
    possible_id, _ = find_peaks(one_mocap_data, height = 5)

    hop_id_mocap = 0
    peak_count   = 0
    while hop_id_mocap < 200:
        hop_id_mocap = 1*possible_id[peak_count]
        peak_count  += 1

    return hop_id_mocap

# --- Get information for sync'ing --- #
def get_sync_info(mocap_data, pelvis_mt_data, window = 120, iters = 1500, fs = constant_mt.MT_SAMPLING_RATE, source = 'mt'):
    ''' Get information for sync'ing IMU and mocap data

    Args:
        + mocap_data (pd.DataFrame): mocap data of the selected task
        + pelvis_mt_data (np.array): pelvis IMU data of the selected task
        + window, iters (int): parameters for matching IMU and mocap data

    Returns:
        + first_start (str): 'imu' or 'mocap'
        + shifting_id (int): shifting amount for IMU or mocap to sync
    '''
    shifting_id = 0
    prev_err    = 999

    pelvis_vertical_acc_mt    = get_vertical_acc_mt(pelvis_mt_data, source)
    pelvis_vertical_acc_mocap = get_vertical_acc_mocap(mocap_data['RPS2 Y'], fs)
    hop_id_mocap              = get_hop_id_mocap(pelvis_vertical_acc_mocap[0:int(len(pelvis_vertical_acc_mocap)/2)])

    # import matplotlib.pyplot as plt
    # breakpoint()

    error = []
    for i in range(iters):
        start_mocap = hop_id_mocap - int(window/2)
        stop_mocap = hop_id_mocap + int(window/2)
        if i > start_mocap:
            break
        start_imu = start_mocap - i
        stop_imu = stop_mocap - i
        curr_err = get_rmse(pelvis_vertical_acc_mocap[start_mocap:stop_mocap], pelvis_vertical_acc_mt[start_imu:stop_imu])
        error.append(curr_err)

        if curr_err < prev_err:
            shifting_id = i + 2
            prev_err = curr_err

    mocap_error = min(error)
    mocap_shifting_id = shifting_id

    # import matplotlib.pyplot as plt
    # breakpoint()

    error = []
    for i in range(iters):
        start_mocap = hop_id_mocap - int(window/2)
        stop_mocap = hop_id_mocap + int(window/2)
        start_imu = start_mocap + i
        stop_imu = stop_mocap + i
        curr_err = get_rmse(pelvis_vertical_acc_mocap[start_mocap:stop_mocap], pelvis_vertical_acc_mt[start_imu:stop_imu])
        error.append(curr_err)

        if curr_err < prev_err:
            if i >=2:
                shifting_id = i - 2
            else:
                shifting_id = 0
            prev_err = curr_err

    mt_err = min(error)
    mt_shifting_id = shifting_id

    # breakpoint()

    if mocap_error < mt_err:
        shifting_id = mocap_shifting_id
        first_start = 'mocap'
    else:
        shifting_id = mt_shifting_id
        first_start = 'imu'

    # print(first_start)
    # print(shifting_id)

    # breakpoint()

    return first_start, shifting_id


