# name: run_mc10_opensense.py
# description: run OpenSense IK for the MC10 Biostamp data


import quaternion
import os 
import pickle 

import numpy as np
import pandas as pd
from easydict import EasyDict

from utils.mc10 import mc10_processing, mc10_ik, mc10_calibration, mc10_ik_os
from utils import common
from constants import constant_mc10, constant_meta



def get_data_chunk(data, duration):

    ''' Get a chunk of data based on the specified duration (start and stop time) '''

    data_chunk = {}
    
    for sensor_name in data.keys():
        data_chunk[sensor_name] = data[sensor_name].iloc[duration[0]:duration[1]]
    
    return data_chunk


def mc10_opensense_ik_main(dataset, subject, task, trial, side, filter_type, dim):

    ''' OpenSense IK for the MC10 Biostamp data '''

    selected_filter = filter_type
    filter_params = common.get_filter_params(dataset, filter_type)

    print('=' *50)
    print(f'Running MC10 IK with filter {selected_filter} and dim {dim} ...')
    print(f'Filter parameters: {filter_params}\n')
    print('=' *50)
    print()

    subject_list = common.get_subject_list(dataset, subject)
    task_list    = common.get_task_list(dataset, task)
    trial_list   = common.get_trial_list(dataset, trial)
    side_list    = common.get_side_list(dataset, side)

    for subject in subject_list:

        print(f'*** Subject {subject}')
        test = 1    

        print('Getting MC10 data ...')
        mc10_data = mc10_processing.get_mc10_data(dataset, subject)

        for task in task_list:

            for trial in trial_list:

                for side in side_list:

                    try:

                        selected_task = EasyDict(side = side, trial = trial, task = task)


                        walking_duration = constant_meta.WALKING_DURATION[str(subject)]

                        running_duration = [constant_meta.TASK_DURATION[str(subject)][selected_task.task][selected_task.side][f't{selected_task.trial}'][0],
                                            constant_meta.TASK_DURATION[str(subject)][selected_task.task][selected_task.side][f't{selected_task.trial}'][1]]

                        static_duration = [constant_meta.STATIC_DURATION[str(subject)][constant_meta.STATIC_SIDE[str(subject)]][0],
                                        constant_meta.STATIC_DURATION[str(subject)][constant_meta.STATIC_SIDE[str(subject)]][1]]

            
                        static_data  = get_data_chunk(mc10_data, static_duration)
                        walking_data = get_data_chunk(mc10_data, walking_duration)
                        running_data = get_data_chunk(mc10_data, running_duration)

                        running_data = {sensor_name: pd.concat([static_data[sensor_name], running_data[sensor_name]], ignore_index=True) for sensor_name in mc10_data.keys()}

                        walking_period = mc10_calibration.get_walking_4_calib(walking_data['shank_r']['Gyr_Z'].to_numpy())
                        seg2sens = mc10_calibration.sensor_to_segment_mc10(static_data, walking_data, walking_period)


                        os_model = 'Rajagopal_2015'
                        print('- Apply the customized sensor-to-segment calibration to the OpenSim model: ' + os_model)
                        mc10_ik_os.os_calibration_customized(seg2sens, os_model)

                        initial_orientation = {}
                        for sensor_name in seg2sens.keys():
                            initial_orientation[sensor_name] = quaternion.from_rotation_matrix(np.identity(3))*quaternion.from_rotation_matrix(seg2sens[sensor_name])

                        running_orientation = mc10_ik.get_mc10_orientation(running_data, selected_filter.upper(), params = filter_params)
                        running_orientation = mc10_calibration.correct_random_6D_orientation(initial_orientation, running_orientation)

                        print('- Convert IMU orientation to OpenSim format ...')
                        mc10_ik_os.convert_imu_orientation_to_os(subject, selected_filter, running_orientation, fs = constant_mc10.PROCESSING_RATE, stat_flag = False)

                        print('- Run OpenSense IK ...')
                        orientation_fn = 's' + str(subject) + '_' + selected_filter + '_orientation.sto' 
                        mc10_ik_os.os_ik(orientation_fn, os_model, False) 

                        print('- Extract knee kinematics from the IK results ...')
                        ik_fn     = 'ik_s' + str(subject) + '_' + selected_filter + '_orientation.mot'
                        knee_kinematics = mc10_ik_os.get_all_ja_os(ik_fn, os_model) 

                        output_fn = f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/ik_os/{subject}/mc10/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'

                        if not os.path.exists(f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/ik_os/{subject}/mc10/'):
                            os.makedirs(f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/ik_os/{subject}/mc10/')

                        with open(output_fn, 'wb') as f:
                            pickle.dump(knee_kinematics, f)


                    except:

                        print(f'No MC10 data for subject {subject}, task {task}, trial {trial}')













