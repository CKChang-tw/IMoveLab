# name: gait_event.py
# description: get gait events from IMU data
# author: Vu Phan
# date: 2024/04/19


import pandas as pd
import numpy as np
import pywt

from tqdm import tqdm
from scipy import signal, integrate, fft 
from scipy.signal import find_peaks


import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import constant_mc10


# --- Low-pass filter data before tracking heel contacts and toe-offs --- #
def filter_shank_z(shank_z):
    ''' Low-pass filter to improve find_peaks for tracking heel contacts and toe-offs

    Args:
        + shank_z (np.array): angular velocity in the sagittal plane

    Returns:
        + shank_z_filtered (np.array): filtered angular velocity in the sagittal plane
        '''

    Wn = constant_mc10.FILTER_CUTOFF_IMU*2/constant_mc10.PROCESSING_RATE
    b, a = signal.butter(constant_mc10.FILTER_ORDER, Wn, btype = 'low')

    shank_z_filtered = signal.filtfilt(b, a, shank_z)

    return shank_z_filtered


# # --- Remove noisy peaks --- #
# def remove_noisy_peaks_mt(raw_swing_index, raw_swing_value, task):
#     ''' Remove noisy peaks at the first few steps (i.e., take steady-state walking periods only)

#     Args:
#         + raw_swing_index, raw_swing_value (np.array): outputs from np.find_peaks on shank_z data

#     Returns:
#         + swing_index, swing_value (np.array): swing index and value with first and last few peaks removed
#     '''
#     if task == 'treadmill_walking':
#         threshold   = np.mean(raw_swing_value) - constants_meta.TREADMILL_WALKING_VAR*np.std(raw_swing_value)
#     elif task == 'walking':
#         threshold   = np.mean(raw_swing_value) - constants_meta.OVERGROUND_WALKING_VAR*np.std(raw_swing_value)
#     else:
#         threshold   = np.mean(raw_swing_value) - 2.5*np.std(raw_swing_value)
#     selected_id = np.where(raw_swing_value > threshold)[0]
#     swing_index = 1*raw_swing_index[selected_id]
#     swing_value = 1*raw_swing_value[selected_id]

#     return swing_index, swing_value

# --- Get DTW --- #
def get_dtw(in_signal, template, window = np.inf):
    ''' Get DTW between the input signal and the template
    Source: https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.00090/full

    Args:
        + in_signal (np.array): input signal
        + template (np.array): template signal
        + window (int): window size for DTW

    Returns:
        + dtw (float): DTW between the input signal and the template
    '''
    n1     = len(in_signal)
    n2     = len(template)
    window = np.max([window, np.abs(n1 - n2)])

    D       = np.inf*np.ones((n1 + 1, n2 + 1))
    D[0, 0] = 0

    for i in range(n1):
        for j in range(int(np.max([i - window, 0])), int(np.min([i + window, n2]))):
            cost = np.linalg.norm(in_signal[i] - template[j])
            D[i + 1, j + 1] = cost + np.min([D[i, j], D[i, j + 1], D[i + 1, j]])

    dtw = D[n1, n2]

    return dtw


# --- Segment data to gait cycles --- #
def segment_data(data, hc_index, gait_cycle_scale = False):
    ''' Segment data to gait cycles based on heel contacts

    Args:
        + data (np.array): input data
        + hc_index (np.array): heel contact indices
        + gait_cycle_scale (bool): scale the gait cycle to 100 samples
    
    Returns:
        + data_seg (np.array): segmented data
        + time_seg (np.array): number of samples per gait cycle
    '''
    data_seg = []
    time_seg = []
    for i in range(len(hc_index) - 1):
        num_sample_per_cycle = hc_index[i+1] - hc_index[i]
        if gait_cycle_scale:
            data_seg.append(np.interp(np.linspace(0, 1, 100), np.linspace(0, 1, num_sample_per_cycle), data[hc_index[i]:hc_index[i+1]]))
        else:
            data_seg.append(data[hc_index[i]:hc_index[i+1]])
        time_seg.append(num_sample_per_cycle)
    # data_seg = np.array(data_seg)

    return data_seg, time_seg


# --- Get turning angle --- #
def get_turning_angle(pelvis_y, prev_id, curr_id, fs = 100):
    ''' Get turning angle from the pelvis angular velocity data

    Args:
        + pelvis_y (np.array): angular velocity in the frontal plane
        + prev_id, curr_id (int): start and end index of the turning period
        + fs (int): sampling rate, default = 100 samples/s

    Returns:
        + turning_angle (float): turning angle in degrees
    '''
    pelvis_y_interval = pelvis_y[prev_id:curr_id]

    time_vector = np.arange(0, len(pelvis_y_interval))/fs
    pelvis_y_orientation = integrate.cumulative_trapezoid(pelvis_y_interval, time_vector, initial = 0)
    pelvis_y_orientation = np.rad2deg(pelvis_y_orientation)
    

    # import matplotlib.pyplot as plt

    # if (curr_id >= 12500) and (curr_id <= 13800):
    #     plt.plot(pelvis_y_orientation)
    #     plt.ylim([-100, 100])
    #     plt.show()


    turning_angle = np.abs(np.max(pelvis_y_orientation) - np.min(pelvis_y_orientation))

    return turning_angle


# --- Identify gait events (heel contacts and toe-offs) --- #

# --- Identify gait events (version 2 - using wavelet transform) --- #
# Find cycling frequency of the signal
def get_cycle_freq(in_signal, fs = 100):
    ''' Get cycling frequency of the signal using FFT
    Source: https://github.com/alkvi/python-imu-gait-evaluation/blob/master/gait_event_detection.py
    '''
    N = len(in_signal)

    half_idx       = int(N/2)
    f_x            = fft.fft(in_signal)/N
    freqs          = np.fft.fftfreq(N, 1/fs)
    freqs_halfside = freqs[:half_idx]

    power       = 10*np.log10(np.abs(f_x[0:half_idx]))
    max_power   = power.max()
    max_idx     = power.argmax()
    cycle_freq  = freqs_halfside[max_idx]

    if cycle_freq > 1.2:
        max_idx    = np.argsort(-1*power)[1]
        cycle_freq = freqs_halfside[max_idx]
    
    
    return cycle_freq


# Get scales for CWT
def get_scales(wavelet, cycle_freq, fs = 100):
    ''' Get scales for CWT based on the cycling frequency
    Source: https://github.com/alkvi/python-imu-gait-evaluation/blob/master/gait_event_detection.py
    '''
    fc              = pywt.central_frequency(wavelet)
    sampling_period = 1/fs
    scales          = fc/(cycle_freq*sampling_period)

    return scales

def detect_gait_events_v2(shank_z, remove = 10):
    ''' Obtain heel contact and toe-off events using CWT
    '''
    fs = 1*constant_mc10.PROCESSING_RATE
    
    # print(fs)
    
    min_peak_distance = fs*0.1
    gait_events = {'hc_index': [], 'hc_value': [], 'to_index': [], 'to_value': []}

    shank_z_detrend  = signal.detrend(shank_z)
    shank_z_filtered = filter_shank_z(shank_z_detrend)

    # mid_swing_index, mid_swing_value = find_peaks(shank_z_filtered, height = [1.5, 10], distance = min_peak_distance)
    mid_swing_index, mid_swing_value = find_peaks(shank_z_filtered, height = 1.5, distance = min_peak_distance)
    # mid_swing_index, mid_swing_value = remove_noisy_peaks_mt(mid_swing_index, mid_swing_value['peak_heights'], task)
    mid_swing_value = mid_swing_value['peak_heights']
    
    cycle_freq = get_cycle_freq(shank_z_filtered, fs = fs)
    # print('...cycling frequency: ' + str(cycle_freq))

    wavelet_to         = pywt.ContinuousWavelet('gaus3')
    scales_to          = get_scales(wavelet_to, cycle_freq, fs = fs)
    shank_z_to, _      = pywt.cwt(shank_z_filtered, scales_to, wavelet_to)
    shank_z_to         = -shank_z_to[0, :]
    shank_z_to         = np.real(shank_z_to)
    to_index, to_value = find_peaks(shank_z_to, height = 0, distance = min_peak_distance)

    wavelet_hc         = pywt.ContinuousWavelet('gaus1')
    scales_hc          = get_scales(wavelet_hc, cycle_freq, fs = fs)
    shank_z_hc, _      = pywt.cwt(shank_z_filtered, scales_hc, wavelet_hc)
    shank_z_hc         = -shank_z_hc[0, :]
    shank_z_hc         = np.real(shank_z_hc)
    hc_index, hc_value = find_peaks(-1*shank_z_hc, height = 5, distance = min_peak_distance)

    for id_ in mid_swing_index:
        try:
            temp_id = np.where(hc_index > id_)[0][0]
            if hc_index[temp_id] not in gait_events['hc_index']:
                gait_events['hc_index'].append(hc_index[temp_id])
                gait_events['hc_value'].append(shank_z_filtered[hc_index[temp_id]])

            temp_id = np.where(to_index < id_)[0][-1]
            if to_index[temp_id] not in gait_events['to_index']:
                gait_events['to_index'].append(to_index[temp_id])
                gait_events['to_value'].append(shank_z_filtered[to_index[temp_id]]) 
            
        except:
            pass

    gait_events['hc_index'] = np.array(gait_events['hc_index'])
    gait_events['hc_value'] = np.array(gait_events['hc_value'])
    gait_events['to_index'] = np.array(gait_events['to_index'])
    gait_events['to_value'] = np.array(gait_events['to_value'])
    gait_events['ms_index'] = 1*mid_swing_index
    gait_events['ms_value'] = 1*mid_swing_value


    return gait_events


def remove_turning_gait(gait_events, pelvis_data_mt):
    ''' Remove gait events (heel contacts and toe-offs) during turning gait
    '''
    pass # tbd



