# name: eval_utils.py
# description: utility functions for evaluation
# author: Vu Phan
# date: 2024/09/23


import pickle as pkl
import numpy as np

from scipy import signal

from imu_benchmark.utils.eval import metrics


def load_data(filename):
    ''' Load data from a pickle file '''

    with open(filename, 'rb') as f:
        data = pkl.load(f)

    return data


def save_data(data, filename):
    ''' Save data to a pickle file '''

    with open(filename, 'wb') as f:
        pkl.dump(data, f)


def find_lag(signal1, signal2):
    ''' Find the lag between two signals '''

    corr = np.correlate(signal1, signal2, mode = 'full')
    lags = signal.correlation_lags(len(signal1), len(signal2))
    lag  = lags[np.argmax(abs(corr))]

    return lag


def resync_data(ja, lag):
    ''' Resync the data based on the lag '''

    for joint in ja.keys():
        ja[joint] = ja[joint][lag:]

    return ja


def do_resync(ja_mc, ja_mt, ja_os, lag):
    ''' Resync the data based on the lag '''

    if lag > 0:
        ja_mt = resync_data(ja_mt, lag)
        ja_os = resync_data(ja_os, lag)

    elif lag < 0:
        ja_mc = resync_data(ja_mc, -lag)

    return ja_mc, ja_mt, ja_os


def do_resync_mvn(ja_mc, ja_mvn, ja_mvn_opensense, ja_mvn_biomodel, lag):
    ''' Resync the data based on the lag '''

    if lag > 0:
        ja_mvn           = resync_data(ja_mvn, lag)
        ja_mvn_opensense = resync_data(ja_mvn_opensense, lag)
        ja_mvn_biomodel  = resync_data(ja_mvn_biomodel, lag)

    elif lag < 0:
        ja_mc = resync_data(ja_mc, -lag)

    return ja_mc, ja_mvn, ja_mvn_opensense, ja_mvn_biomodel


def calculate_rmse(segment_mc, segment_imu):
    ''' Calculate the root-mean-square error (RMSE) '''

    rmse_imu = {}

    for joint in segment_mc.keys():
        rmse_imu[joint] = metrics.get_rmse(segment_mc[joint].flatten(), segment_imu[joint].flatten())
    
    return rmse_imu






