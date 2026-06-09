# name: fp_processing.py


import c3d
import ezc3d

import pandas as pd
import numpy as np
import scipy.signal as signal

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import constant_common, constant_mocap

from utils.mocap import mocap_processing



def get_fp_data(dataset, subject, test, task):
    ''' get fp data from c3d file
    
    Args:
        dataset (str): dataset name, HAKnee or Navio
        subject (int): subject number, check the constant_common.HA_SUBJECT_LIST or constant_common.NAVIO_SUBJECT_LIST for the valid subject numbers
        test (int): test number (1, 2,...)
        task (EasyDict): task information, including side (l or r), trial number (1, 2,...), and task name (static, ddrop, sdrop, shop, run)
    
    Returns:
        fp_data (pd.DataFrame): fp data
    '''
    
    path = mocap_processing.get_mocap_path(dataset, subject, test, task)

    c3d_data = ezc3d.c3d(path)

    fp_data = {}

    fp_list          = c3d_data['parameters']['ANALOG']['LABELS']['value']
    selected_fp_list = [marker for marker in fp_list if "Force" in marker]

    # get sampling rate
    fs = c3d_data['parameters']['ANALOG']['RATE']['value'][0]
    print(f'FP sampling rate: {fs} Hz')

    for fp in selected_fp_list:
        fp_data[fp] = (-1) * c3d_data['data']['analogs'][:, fp_list.index(fp), :].T

        fp_data[fp] = pd.DataFrame(
            fp_data[fp], 
            columns=[f"{fp.split('.')[1]}"]
        )
        # fp_data[fp].drop(columns = ['1'], inplace = True) # drop the constant column

    fp_data = pd.concat(fp_data.values(), axis = 1)

    num_frames = fp_data.shape[0]
    # time       = np.arange(0, num_frames/constant_mocap.FP_SAMPLING_RATE, 1/constant_mocap.FP_SAMPLING_RATE)
    time       = np.arange(0, num_frames/fs, 1/fs)
    time       = pd.DataFrame(time, columns = ['Time'])

    fp_data = pd.concat([time, fp_data], axis = 1)

    return fp_data

    # breakpoint()
    # print(selected_fp_list)
    



















