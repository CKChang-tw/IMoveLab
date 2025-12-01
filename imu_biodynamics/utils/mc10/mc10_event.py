# name: mc10_event.py


import numpy as np
import pandas as pd

from scipy import signal


# --- Filter data before identifying gait cycles or exercise repetitions --- #
def filter_signal(input_signal, fs, cutoff = 15):
    ''' Filter data before identifying gait cycles or exercise repetitions

    Args:
        + input_signal (np.array): angular velocity or linear acceleration in one axis
        + fs (float): sampling rate
        + cutoff (float): cut-off frequency 

    Returns:
        + filtered_series (np.array): filtered data
    '''
    Wn   = cutoff*2/fs 
    b, a = signal.butter(4, Wn, btype = 'low')

    filtered_signal = signal.filtfilt(b, a, input_signal)

    return filtered_signal


# --- Detect gait events during walking --- #
def detect_gait_events(lateral_shank_vel, fs = 100):
    ''' Obtain gait events, including heel contact, toe off, and mid swing from IMU data

    Args:
        + lateral_shank_vel (np.array): angular velocity in the sagittal plane
        + fs (float): sampling rate, default = 100 Hz

    Returns:
        + gait_events (dict of np.array): index and value arrays of gait events
    '''
    min_peak_distance = 0.5*fs 
    
    filtered_lateral_shank_vel = filter_signal(lateral_shank_vel, fs)

    mid_swing_index, mid_swing_value = signal.find_peaks(filtered_lateral_shank_vel, height = [2, 10], distance = min_peak_distance)
    mid_swing_value                  = mid_swing_value['peak_heights']
    # stance_index, stance_value       = signal.find_peaks(-1*filtered_lateral_shank_vel, height = -1)

    # gait_events = {'hc_index': [], 'hc_value': [], 'to_index': [], 'to_value': []}

    # for id in mid_swing_index:
    #     temp_id = np.where(stance_index > id)[0][0]
    #     gait_events['hc_index'].append(stance_index[temp_id])
    #     gait_events['hc_value'].append(-1*stance_value['peak_heights'][temp_id])

    #     temp_id = np.where(stance_index < id)[0][-1]
    #     if stance_value['peak_heights'][temp_id-1] > stance_value['peak_heights'][temp_id]:
    #         if (stance_index[temp_id] - stance_index[temp_id - 1]) < 0.25*fs:
    #             temp_id = temp_id - 1
    #     gait_events['to_index'].append(stance_index[temp_id])
    #     gait_events['to_value'].append(-1*stance_value['peak_heights'][temp_id])

    # gait_events['hc_index'] = np.array(gait_events['hc_index'])
    # gait_events['hc_value'] = np.array(gait_events['hc_value'])
    # gait_events['to_index'] = np.array(gait_events['to_index'])
    # gait_events['to_value'] = np.array(gait_events['to_value'])

    gait_events = {}
    gait_events['ms_index'] = 1*mid_swing_index
    gait_events['ms_value'] = 1*mid_swing_value
    
    return gait_events











