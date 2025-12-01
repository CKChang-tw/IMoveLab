# name: biplane_processing.py


import os, sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd 

from constants import constant_common


def get_biplane_session_from_task(task, dataset = 'HAKnee'):
    ''' get the biplane session from the task information

    Args:
        task (EasyDict): task information, including side (l or r), trial number (1, 2,...), and task name (static, ddrop, sdrop, shop, run)
        dataset (str): dataset name, HAKnee or Navio

    Returns:
        session (str): biplane session (A, B, C, D)
    '''

    if dataset == 'Navio':
        
        pass # TODO: implement for Navio dataset

    elif dataset == 'HAKnee':
        
        if task.side == 'l' and task.task == 'run':
            session = 'D'
        elif task.side == 'r' and task.task == 'run':
            session = 'C'
        elif task.side == 'l' and task.task == 'ddrop':
            session = 'B'
        else:
            session = 'A'

    return session


def get_biplane_path(subject, dataset, test, task):
    ''' get path to the biplane kinematics data

    Args:
        subject (int): subject number, check the constant_common.HA_SUBJECT_LIST or constant_common.NAVIO_SUBJECT_LIST for the valid subject numbers
        dataset (str): dataset name, HAKnee or Navio
        test (int): test number (1, 2,...)
        task (EasyDict): task information, including side (l or r), trial number (1, 2,...), and task name (static, ddrop, sdrop, shop, run)

    Returns:
        path (str): path to the biplane kinematics data
    '''

    subject_str = str(subject).zfill(2) 
    test_str    = 'Test' + str(test)
    session     = get_biplane_session_from_task(task)
    task_str    = task.side.upper() + constant_common.HA_TASK_MAPPING[task.task] + str(task.trial)

    path = os.path.join(constant_common.DATA_PATH, constant_common.BIPLANE_PATH, dataset, subject_str, test_str, session, task_str, 'KinematicsMeasurementReport.csv')
    
    return path


def get_biplane_knee_kinematics(subject, dataset, test, task, ft):
    ''' get biplane knee kinematics

    Args:
        subject (int): subject number, check the constant_common.HA_SUBJECT_LIST or constant_common.NAVIO_SUBJECT_LIST for the valid subject numbers
        dataset (str): dataset name, HAKnee or Navio
        test (int): test number (1, 2,...)
        task (EasyDict): task information, including side (l or r), trial number (1, 2,...), and task name (static, ddrop, sdrop, shop, run)
        ft (int): target frequency (Hz) for resampling the biplane data

    Returns:
        knee_kinematics (dict): dictionary containing biplane knee kinematics (flexion, adduction, rotation)
    '''
    
    path = get_biplane_path(subject, dataset, test, task)
    # print(task.task)

    biplane_data = pd.read_csv(path, skiprows = 1)
    # biplane_data = biplane_data[(biplane_data.iloc[:, -3] != 0) | (biplane_data.iloc[:, -2] != 0) | (biplane_data.iloc[:, -1] != 0)].reset_index(drop = True)
    biplane_data.columns.values[0] = 'Frame'
    biplane_data.columns.values[1] = 'Time'

    start_frame = biplane_data['Frame'].to_numpy()[0]
    if start_frame > 1:
        temp_frame = pd.DataFrame(np.zeros((start_frame, biplane_data.shape[1])), columns = biplane_data.columns)
        temp_frame['Frame'] = np.arange(0, start_frame)
        temp_frame['Time']  = np.arange(0, start_frame) * (1/150) # assuming the biplane data is collected at 150 Hz
        biplane_data = pd.concat([temp_frame, biplane_data], ignore_index = True)


    if task.task == 'static':
        pass
    else:
        biplane_data = biplane_resample(biplane_data, ft)

    knee_kinematics = {}
    knee_kinematics['knee_flexion_' + task.side]   = biplane_data['Flexion'].to_numpy()
    knee_kinematics['knee_adduction_' + task.side] = biplane_data['Ab\Ad'].to_numpy()
    knee_kinematics['knee_rotation_' + task.side]  = biplane_data['Int\Ext'].to_numpy()

    return knee_kinematics


def biplane_resample(biplane_data, ft):
    ''' resample biplane data to a fixed frequency

    Args:
        biplane_data (pd.DataFrame): biplane data
        ft (int): target frequency (Hz)

    Returns:
        r_biplane_data (pd.DataFrame): resampled biplane data
    '''

    # breakpoint()

    ts = 1/ft 
    nan_id    = np.arange(biplane_data['Time'].to_numpy()[0], biplane_data['Time'].to_numpy()[-1], ts)
    nan_arr   = np.nan*np.ones(nan_id.shape[0])
    nan_frame = pd.DataFrame({'temp': nan_arr}, index = nan_id)

    temp_frame = biplane_data.set_index(biplane_data['Time']).iloc[:, 1::]
    temp_frame = temp_frame.join(nan_frame, how = 'outer')
    temp_frame = temp_frame.interpolate(method = 'linear', limit_area = 'inside')

    interp_frame = temp_frame.loc[nan_id, :]
    # interp_frame = interp_frame.iloc[1:-1, 0:-1]
    interp_frame = interp_frame.iloc[:, 0:-1]

    r_biplane_data         = 1*interp_frame.reset_index()
    r_biplane_data.columns = biplane_data.columns

    return r_biplane_data



