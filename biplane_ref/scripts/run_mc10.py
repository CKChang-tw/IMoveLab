# name: run_mc10.py
# description: run IK for the MC10 Biostamp data


import quaternion
import os 
import pickle 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from easydict import EasyDict

from utils.mc10 import mc10_processing, mc10_ik, mc10_calibration
from utils import common
from constants import constant_meta



def get_data_chunk(data, duration):

    ''' Get a chunk of data based on the specified duration (start and stop time) '''

    data_chunk = {}
    
    for sensor_name in data.keys():
        data_chunk[sensor_name] = data[sensor_name].iloc[duration[0]:duration[1]]
    
    return data_chunk


def mc10_ik_main(dataset, subject, task, trial, side, filter_type, dim, tuning = False, filter_params = None, savefig = False):

    ''' Run IK for the MC10 Biostamp data '''

    filter_type     = filter_type.upper()
    selected_filter = filter_type

    if not tuning:
        filter_params_set = [common.get_filter_params(dataset, filter_type)]
    else:
        filter_params_set = common.get_filter_params_for_tuning(filter_type)

    print('=' *50)
    print(f'Running MC10 IK with filter {selected_filter} and dim {dim} ...')
    if tuning:
        print('Tuning mode: ON')
    else:
        print('Tuning mode: OFF')
    print('=' *50)
    print()

    subject_list = common.get_subject_list(dataset, subject, tuning)
    task_list    = common.get_task_list(dataset, task)
    trial_list   = common.get_trial_list(dataset, trial)
    side_list    = common.get_side_list(dataset, side)

    for filter_params in filter_params_set:

        print(f'Filter parameters: {filter_params}\n')

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

                            initial_orientation = {}
                            for sensor_name in seg2sens.keys():
                                initial_orientation[sensor_name] = quaternion.from_rotation_matrix(np.identity(3))*quaternion.from_rotation_matrix(seg2sens[sensor_name])

                            running_orientation = mc10_ik.get_mc10_orientation(running_data, selected_filter, params = filter_params)
                            running_orientation = mc10_calibration.correct_random_6D_orientation(initial_orientation, running_orientation)

                            print('Getting MC10 knee kinematics ...')
                            knee_kinematics = mc10_ik.get_knee_kinematics_mc10(seg2sens, running_orientation)

                            if tuning:
                                # turn all elements of filter_params into string and concatenate them with '_' in between
                                filter_params_str = '_'.join([str(param) for param in filter_params])
                                output_fn = f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/tuning/p_{filter_params_str}/{subject}/mc10/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'

                                if not os.path.exists(f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/tuning/p_{filter_params_str}/{subject}/mc10/'):
                                    os.makedirs(f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/tuning/p_{filter_params_str}/{subject}/mc10/')

                            else:
                                output_fn = f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/ik/{subject}/mc10/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'

                                if not os.path.exists(f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/ik/{subject}/mc10/'):
                                    os.makedirs(f'outputs/{dataset}/bm_{filter_type.lower()}{dim.lower()}/ik/{subject}/mc10/')

                            with open(output_fn, 'wb') as f:
                                pickle.dump(knee_kinematics, f)

                            if savefig:
                                fig, ax = plt.subplots(3, 2, figsize = (10, 5), sharex = True, sharey = True)

                                ax[0, 0].plot(knee_kinematics['knee_flexion_r'])
                                ax[0, 0].set_ylabel('Knee flexion')
                                ax[0, 0].set_title('Right')
                                ax[0, 0].set_ylim(-25, 100)
                                ax[1, 0].plot(knee_kinematics['knee_adduction_r'])
                                ax[1, 0].set_ylabel('Knee adduction')
                                ax[2, 0].plot(knee_kinematics['knee_rotation_r'])
                                ax[2, 0].set_ylabel('Knee rotation')

                                ax[0, 1].plot(knee_kinematics['knee_flexion_l'])
                                ax[0, 1].set_ylabel('Knee flexion')
                                ax[0, 1].set_title('Left')
                                ax[1, 1].plot(knee_kinematics['knee_adduction_l'])
                                ax[1, 1].set_ylabel('Knee adduction')
                                ax[2, 1].plot(knee_kinematics['knee_rotation_l'])
                                ax[2, 1].set_ylabel('Knee rotation')

                                for i in range(3):
                                    for j in range(2):
                                        ax[i, j].spines['top'].set_visible(False)
                                        ax[i, j].spines['right'].set_visible(False)

                                path = f'figures/ik/mc10/{dataset}/subject{subject}/'
                                os.makedirs(path, exist_ok = True)

                                plt.savefig(path + f'{selected_task.side}_{selected_task.task}_{selected_task.trial}.png', dpi = 300)
                                plt.close()

                        except:

                            print(f'No MC10 data for subject {subject}, task {task}, trial {trial}')


















