# name: eval_utils.py
# description: utility functions for evaluation
# author: Vu Phan
# date: 2024/09/23


import pickle as pkl
import numpy as np

from scipy import signal
from scipy.spatial.transform import Rotation as R

from imu_benchmark.utils.eval import metrics
from imu_benchmark.constants import constant_common, constant_mocap, constant_mt


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


def calculate_rmse(segment_mc, segment_imu, do_biomodel = False):
    ''' Calculate the root-mean-square error (RMSE) '''

    rmse_imu = {}

    for joint in segment_mc.keys():
        if do_biomodel:
            if joint[:-2] in ['knee_adduction', 'knee_rotation', 'ankle_adduction', 'ankle_rotation']:
                continue
            else:
                rmse_imu[joint] = metrics.get_rmse(segment_mc[joint].flatten(), segment_imu[joint].flatten())
        else:
            rmse_imu[joint] = metrics.get_rmse(segment_mc[joint].flatten(), segment_imu[joint].flatten())
    
    return rmse_imu


def _to_rot_array(in_quat):
    ''' Convert quaternion to rotation array '''

    if isinstance(in_quat, dict):
        out_rot = {}
        for key in in_quat.keys():
            out_rot[key] = R.from_quat(quaternion.as_float_array(in_quat[key]), scalar_first = True).as_matrix() 
    else:
        out_rot = R.from_quat(quaternion.as_float_array(in_quat), scalar_first = True).as_matrix()

    return out_rot


def get_ja_alignment(ja_mt, ja_mc, alignment_id, task, store_correction = False):
    ''' Get the joint angles alignment '''

    aligned_ja_mt  = {}
    correction_mat = {}

    sequence = 'zxy'  # flexion, adduction, rotation

    for side in ['r', 'l']:
        for joint in ['hip', 'knee', 'ankle']:

            # print(joint + '_' + side)
            # print()

            if 'treadmill' in task and side == 'l':
                aligned_ja_mt[joint + '_flexion_' + side] = ja_mt[joint + '_flexion_' + side]
                aligned_ja_mt[joint + '_adduction_' + side] = ja_mt[joint + '_adduction_' + side]
                aligned_ja_mt[joint + '_rotation_' + side] = ja_mt[joint + '_rotation_' + side]
                
            else:
                angle_mt     = np.array([ja_mt[joint + '_flexion_' + side], 
                                        ja_mt[joint + '_adduction_' + side], 
                                        ja_mt[joint + '_rotation_' + side]]).T
                rot_angle_mt = R.from_euler(sequence, angle_mt, degrees = True).as_matrix()

                static_angle_mt     = np.array([ja_mt[joint + '_flexion_' + side][alignment_id[0]:alignment_id[1]].mean(),
                                                ja_mt[joint + '_adduction_' + side][alignment_id[0]:alignment_id[1]].mean(),
                                                ja_mt[joint + '_rotation_' + side][alignment_id[0]:alignment_id[1]].mean()]).T
                rot_static_angle_mt = R.from_euler(sequence, static_angle_mt, degrees = True).as_matrix()

                static_angle_mocap     = np.array([ja_mc[joint + '_flexion_' + side][alignment_id[0]:alignment_id[1]].mean(),
                                                    ja_mc[joint + '_adduction_' + side][alignment_id[0]:alignment_id[1]].mean(),
                                                    ja_mc[joint + '_rotation_' + side][alignment_id[0]:alignment_id[1]].mean()]).T  
                rot_static_angle_mocap = R.from_euler(sequence, static_angle_mocap, degrees = True).as_matrix()

                correction = rot_static_angle_mt.T @ rot_static_angle_mocap

                aligned_angle_mt = np.zeros(rot_angle_mt.shape)
                for i in range(rot_angle_mt.shape[0]):
                    aligned_angle_mt[i] = rot_angle_mt[i] @ correction
                
                rot_aligned_angle_mt = R.from_matrix(aligned_angle_mt).as_euler(sequence, degrees = True)
                aligned_ja_mt[joint + '_flexion_' + side] = rot_aligned_angle_mt[:, 0]
                aligned_ja_mt[joint + '_adduction_' + side] = rot_aligned_angle_mt[:, 1]
                aligned_ja_mt[joint + '_rotation_' + side] = rot_aligned_angle_mt[:, 2]

                correction_angle = R.from_matrix(correction).as_euler(sequence, degrees = True)
                correction_mat[joint + '_flexion_' + side]   = correction_angle[0]
                correction_mat[joint + '_adduction_' + side] = correction_angle[1]
                correction_mat[joint + '_rotation_' + side]  = correction_angle[2]

    if store_correction:
        return aligned_ja_mt, correction_mat
    
    else:
        return aligned_ja_mt


def get_ja_alignment_static(ja_mt, ja_mc, task, ja_mt_static, ja_mc_static, store_correction = False):
    aligned_ja_mt  = {}
    correction_mat = {}

    sequence = 'zxy'  # flexion, adduction, rotation

    for side in ['r', 'l']:

        for joint in ['hip', 'knee', 'ankle']:
            
            if 'treadmill' in task and side == 'l':
                aligned_ja_mt[joint + '_flexion_' + side] = ja_mt[joint + '_flexion_' + side]
                aligned_ja_mt[joint + '_adduction_' + side] = ja_mt[joint + '_adduction_' + side]
                aligned_ja_mt[joint + '_rotation_' + side] = ja_mt[joint + '_rotation_' + side]
                
            else:
                angle_mt     = np.array([ja_mt[joint + '_flexion_' + side], 
                                        ja_mt[joint + '_adduction_' + side], 
                                        ja_mt[joint + '_rotation_' + side]]).T
                rot_angle_mt = R.from_euler(sequence, angle_mt, degrees = True).as_matrix()
                
                static_angle_mt     = np.array([ja_mt_static[joint + '_flexion_' + side].mean(),
                                                ja_mt_static[joint + '_adduction_' + side].mean(),
                                                ja_mt_static[joint + '_rotation_' + side].mean()]).T
                rot_static_angle_mt = R.from_euler(sequence, static_angle_mt, degrees = True).as_matrix()
                static_angle_mocap     = np.array([ja_mc_static[joint + '_flexion_' + side].mean(),
                                                   ja_mc_static[joint + '_adduction_' + side].mean(),
                                                   ja_mc_static[joint + '_rotation_' + side].mean()]).T
                rot_static_angle_mocap = R.from_euler(sequence, static_angle_mocap, degrees = True).as_matrix()

                correction = rot_static_angle_mt.T @ rot_static_angle_mocap

                aligned_angle_mt = np.zeros(rot_angle_mt.shape)
                for i in range(rot_angle_mt.shape[0]):
                    aligned_angle_mt[i] = rot_angle_mt[i] @ correction

                rot_aligned_angle_mt = R.from_matrix(aligned_angle_mt).as_euler(sequence, degrees = True)
                aligned_ja_mt[joint + '_flexion_' + side] = rot_aligned_angle_mt[:, 0]
                aligned_ja_mt[joint + '_adduction_' + side] = rot_aligned_angle_mt[:, 1]
                aligned_ja_mt[joint + '_rotation_' + side] = rot_aligned_angle_mt[:, 2]

                correction_angle = R.from_matrix(correction).as_euler(sequence, degrees = True)
                correction_mat[joint + '_flexion_' + side]   = correction_angle[0]
                correction_mat[joint + '_adduction_' + side] = correction_angle[1]
                correction_mat[joint + '_rotation_' + side]  = correction_angle[2]

    if store_correction:
        return aligned_ja_mt, correction_mat
    
    else:
        return aligned_ja_mt


def get_long_trial_chunk(ja_mt, subject, trial):
    ja_mt_trial = {}
    for joint in ja_mt.keys():
        ja_mt_trial[joint] = 1*ja_mt[joint][constant_mt.LONG_TRIAL_ID[subject]['t' + str(trial)]['trial_start']:constant_mt.LONG_TRIAL_ID[subject]['t' + str(trial)]['trial_end']]

    return ja_mt_trial


def remove_bad_mocap(ja_mc, ja_mt, ja_os, subject, trial):
    for i in range(len(constant_mt.REMOVAL_OF_BAD_MOCAP[subject][trial])):
        if len(constant_mt.REMOVAL_OF_BAD_MOCAP[subject][trial][i]) > 0:
            for joint in ja_mc.keys():
                start_id = constant_mt.REMOVAL_OF_BAD_MOCAP[subject][trial][i][0]
                end_id   = constant_mt.REMOVAL_OF_BAD_MOCAP[subject][trial][i][1]
                ja_mc[joint][start_id:end_id] = np.nan
                ja_mt[joint][start_id:end_id] = np.nan
                ja_os[joint][start_id:end_id] = np.nan

    return ja_mc, ja_mt, ja_os



