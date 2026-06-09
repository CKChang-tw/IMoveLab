# name: main_mc10.py


import quaternion
import os 
import pickle 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime, timezone
from easydict import EasyDict

from utils.mc10 import mc10_processing, mc10_ik, mc10_calibration
from utils.mocap import fp_processing
from constants import constant_mocap, constant_mc10, constant_meta, constant_common

dataset = 'HAKnee'
# subject = 16

selected_filter = 'VQF'
# selected_filter = 'MAH'
# selected_filter = 'EKF'
# selected_filter = 'MAD'
# selected_filter = 'RIANN'

if selected_filter == 'VQF':
    filter_params = [2, 10] 
    # filter_params = [10, 7]  
elif selected_filter == 'MAH':
    filter_params = [0.4, 0.3]
elif selected_filter == 'MAD':
    filter_params = [0.1]
elif selected_filter == 'EKF':
    filter_params = [0.9, 0.9, 0.9]
elif selected_filter == 'RIANN':
    filter_params = None
    

for subject in constant_common.HA_SUBJECT_LIST:
# for subject in [6, 9, 10, 12, 13, 14, 15, 16, 17, 18]:

    print(f'*** Subject {subject}')
    test = 1    

    print('Getting MC10 data ...')
    mc10_data = mc10_processing.get_mc10_data(dataset, subject)


    for task in list(constant_common.HA_TASK_MAPPING.keys())[1::]:

        for trial in range(1, 4):

            # for side in ['l']:
            for side in ['r', 'l']:

                try:

                    selected_task = EasyDict(side = side, trial = trial, task = task)


                    walking_duration = constant_meta.WALKING_DURATION[str(subject)]

                    running_duration = [constant_meta.TASK_DURATION[str(subject)][selected_task.task][selected_task.side][f't{selected_task.trial}'][0],
                                        constant_meta.TASK_DURATION[str(subject)][selected_task.task][selected_task.side][f't{selected_task.trial}'][1]]
                    # static_duration  = [constant_meta.TASK_DURATION[str(subject)][selected_task.task][selected_task.side][f't{selected_task.trial}'][0],
                    #                     constant_meta.TASK_DURATION[str(subject)][selected_task.task][selected_task.side][f't{selected_task.trial}'][0] + 50]

                    static_duration = [constant_meta.STATIC_DURATION[str(subject)][constant_meta.STATIC_SIDE[str(subject)]][0],
                                       constant_meta.STATIC_DURATION[str(subject)][constant_meta.STATIC_SIDE[str(subject)]][1]]

                    def get_data_chunk(data, duration):

                        data_chunk = {}
                        
                        for sensor_name in data.keys():
                            data_chunk[sensor_name] = data[sensor_name].iloc[duration[0]:duration[1]]
                        
                        return data_chunk


                    static_data  = get_data_chunk(mc10_data, static_duration)
                    walking_data = get_data_chunk(mc10_data, walking_duration)
                    running_data = get_data_chunk(mc10_data, running_duration)

                    running_data = {sensor_name: pd.concat([static_data[sensor_name], running_data[sensor_name]], ignore_index=True) for sensor_name in mc10_data.keys()}

                    walking_period = mc10_calibration.get_walking_4_calib(walking_data['shank_r']['Gyr_Z'].to_numpy())
                    seg2sens = mc10_calibration.sensor_to_segment_mc10(static_data, walking_data, walking_period)

                    initial_orientation = {}
                    for sensor_name in seg2sens.keys():
                        initial_orientation[sensor_name] = quaternion.from_rotation_matrix(np.identity(3))*quaternion.from_rotation_matrix(seg2sens[sensor_name])

                    # breakpoint()

                    running_orientation = mc10_ik.get_mc10_orientation(running_data, selected_filter, params = filter_params)
                    running_orientation = mc10_calibration.correct_random_6D_orientation(initial_orientation, running_orientation)


                    print('Getting MC10 knee kinematics ...')
                    knee_kinematics = mc10_ik.get_knee_kinematics_mc10(seg2sens, running_orientation)


                    output_fn = f'outputs/{dataset}/ik/{subject}/mc10/knee_kinematics_{selected_task.side}_{selected_task.task}_{selected_task.trial}.pkl'

                    if not os.path.exists(f'outputs/{dataset}/ik/{subject}/mc10/'):
                        os.makedirs(f'outputs/{dataset}/ik/{subject}/mc10/')

                    with open(output_fn, 'wb') as f:
                        pickle.dump(knee_kinematics, f)

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

















