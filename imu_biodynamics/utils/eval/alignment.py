# name: alignment.py


import numpy as np

from scipy import signal
from scipy.spatial.transform import Rotation as R


def get_ja_alignment(knee_measurements, knee_measurements_static, knee_kinematics_static, side, store_correction = False):
    ''' Get the joint angles alignment 
    
    Args:
        knee_measurements (dict): Joint angles from measurements (MC10 or mocap)
        knee_kinematics (dict): Joint angles from biplane
        task (str): Task name
        store_correction (bool): Whether to return the correction matrix

    Returns:
        dict: Aligned joint angles
        dict: Correction matrix (if store_correction is True)
    '''

    aligned_knee_measurements  = {}
    correction_mat = {}

    joint = 'knee'
    # sequence = 'ZYX'  # Z: flexion/extension, Y: adduction/abduction, X: rotation
    sequence = 'zyx'

    angle_knee_measurements     = np.array([knee_measurements[joint + '_flexion_' + side],
                                            knee_measurements[joint + '_adduction_' + side],
                                            knee_measurements[joint + '_rotation_' + side]]).T
    rot_angle_knee_measurements = R.from_euler(sequence, angle_knee_measurements, degrees = True).as_matrix()

    init_knee_measurements = np.array([knee_measurements_static[joint + '_flexion_' + side].mean(),
                                        knee_measurements_static[joint + '_adduction_' + side].mean(),
                                        knee_measurements_static[joint + '_rotation_' + side].mean()]).T

    init_knee_kinematics   = np.array([knee_kinematics_static[joint + '_flexion_' + side].mean(),
                                        knee_kinematics_static[joint + '_adduction_' + side].mean(),
                                        knee_kinematics_static[joint + '_rotation_' + side].mean()]).T
        
    rot_init_knee_measurements = R.from_euler(sequence, init_knee_measurements, degrees = True).as_matrix()
    rot_init_knee_kinematics   = R.from_euler(sequence, init_knee_kinematics, degrees = True).as_matrix()

    correction = rot_init_knee_measurements.T @ rot_init_knee_kinematics

    aligned_angle_knee_measurements = np.zeros(rot_angle_knee_measurements.shape)
    for i in range(rot_angle_knee_measurements.shape[0]):
        aligned_angle_knee_measurements[i] = rot_angle_knee_measurements[i] @ correction
    
    # breakpoint()

    rot_aligned_knee_measurements = R.from_matrix(aligned_angle_knee_measurements).as_euler(sequence, degrees = True)
    aligned_knee_measurements[joint + '_flexion_' + side] = rot_aligned_knee_measurements[:, 0]
    aligned_knee_measurements[joint + '_adduction_' + side] = rot_aligned_knee_measurements[:, 1]
    aligned_knee_measurements[joint + '_rotation_' + side] = rot_aligned_knee_measurements[:, 2]

    correction_angle = R.from_matrix(correction).as_euler(sequence, degrees = True)
    correction_mat[joint + '_flexion_' + side]   = correction_angle[0]
    correction_mat[joint + '_adduction_' + side] = correction_angle[1]
    correction_mat[joint + '_rotation_' + side]  = correction_angle[2]

    if store_correction:
        return aligned_knee_measurements, correction_mat
    
    else:
        return aligned_knee_measurements


def get_ja_alignment_init(knee_measurements, knee_kinematics, side, store_correction = False):
    ''' Get the joint angles alignment 
    
    Args:
        knee_measurements (dict): Joint angles from measurements (MC10 or mocap)
        knee_kinematics (dict): Joint angles from biplane
        task (str): Task name
        store_correction (bool): Whether to return the correction matrix

    Returns:
        dict: Aligned joint angles
        dict: Correction matrix (if store_correction is True)
    '''

    aligned_knee_measurements  = {}
    correction_mat = {}

    joint = 'knee'
    # sequence = 'ZYX'  # Z: flexion/extension, Y: adduction/abduction, X: rotation
    sequence = 'zyx'

    angle_knee_measurements     = np.array([knee_measurements[joint + '_flexion_' + side],
                                            knee_measurements[joint + '_adduction_' + side],
                                            knee_measurements[joint + '_rotation_' + side]]).T
    rot_angle_knee_measurements = R.from_euler(sequence, angle_knee_measurements, degrees = True).as_matrix()

    init_knee_measurements = np.array([knee_measurements[joint + '_flexion_' + side][0],
                                        knee_measurements[joint + '_adduction_' + side][0],
                                        knee_measurements[joint + '_rotation_' + side][0]]).T

    init_knee_kinematics   = np.array([knee_kinematics[joint + '_flexion_' + side][0],
                                        knee_kinematics[joint + '_adduction_' + side][0],
                                        knee_kinematics[joint + '_rotation_' + side][0]]).T
    # print(init_knee_kinematics)

    rot_init_knee_measurements = R.from_euler(sequence, init_knee_measurements, degrees = True).as_matrix()
    rot_init_knee_kinematics   = R.from_euler(sequence, init_knee_kinematics, degrees = True).as_matrix()

    correction = rot_init_knee_measurements.T @ rot_init_knee_kinematics

    aligned_angle_knee_measurements = np.zeros(rot_angle_knee_measurements.shape)
    for i in range(rot_angle_knee_measurements.shape[0]):
        aligned_angle_knee_measurements[i] = rot_angle_knee_measurements[i] @ correction
    
    # breakpoint()

    rot_aligned_knee_measurements = R.from_matrix(aligned_angle_knee_measurements).as_euler(sequence, degrees = True)
    aligned_knee_measurements[joint + '_flexion_' + side] = rot_aligned_knee_measurements[:, 0]
    aligned_knee_measurements[joint + '_adduction_' + side] = rot_aligned_knee_measurements[:, 1]
    aligned_knee_measurements[joint + '_rotation_' + side] = rot_aligned_knee_measurements[:, 2]

    correction_angle = R.from_matrix(correction).as_euler(sequence, degrees = True)
    correction_mat[joint + '_flexion_' + side]   = correction_angle[0]
    correction_mat[joint + '_adduction_' + side] = correction_angle[1]
    correction_mat[joint + '_rotation_' + side]  = correction_angle[2]

    if store_correction:
        return aligned_knee_measurements, correction_mat
    
    else:
        return aligned_knee_measurements



# def get_ja_alignment(knee_measurements, knee_kinematics, side, store_correction = False):
#     ''' Get the joint angles alignment 
    
#     Args:
#         knee_measurements (dict): Joint angles from measurements (MC10 or mocap)
#         knee_kinematics (dict): Joint angles from biplane
#         task (str): Task name
#         store_correction (bool): Whether to return the correction matrix

#     Returns:
#         dict: Aligned joint angles
#         dict: Correction matrix (if store_correction is True)
#     '''

#     aligned_knee_measurements  = {}
#     correction_mat = {}

#     joint = 'knee'

#     angle_knee_measurements     = np.array([knee_measurements[joint + '_flexion_' + side],
#                                             knee_measurements[joint + '_adduction_' + side],
#                                             knee_measurements[joint + '_rotation_' + side]]).T
#     rot_angle_knee_measurements = R.from_euler('ZYX', angle_knee_measurements, degrees = True).as_matrix()

#     init_knee_measurements     = np.array([knee_measurements[joint + '_flexion_' + side][0],
#                                     knee_measurements[joint + '_adduction_' + side][0],
#                                     knee_measurements[joint + '_rotation_' + side][0]]).T
#     rot_init_knee_measurements = R.from_euler('ZYX', init_knee_measurements, degrees = True).as_matrix()

#     init_knee_kinematics     = np.array([knee_kinematics[joint + '_flexion_' + side][0],
#                                         knee_kinematics[joint + '_adduction_' + side][0],
#                                         knee_kinematics[joint + '_rotation_' + side][0]]).T
#     rot_init_knee_kinematics = R.from_euler('ZYX', init_knee_kinematics, degrees = True).as_matrix()

#     correction = rot_init_knee_measurements.T @ rot_init_knee_kinematics

#     aligned_angle_knee_measurements = np.zeros(rot_angle_knee_measurements.shape)
#     for i in range(rot_angle_knee_measurements.shape[0]):
#         aligned_angle_knee_measurements[i] = rot_angle_knee_measurements[i] @ correction

#     rot_aligned_knee_measurements = R.from_matrix(aligned_angle_knee_measurements).as_euler('ZYX', degrees = True)
#     aligned_knee_measurements[joint + '_flexion_' + side] = rot_aligned_knee_measurements[:, 0]
#     aligned_knee_measurements[joint + '_adduction_' + side] = rot_aligned_knee_measurements[:, 1]
#     aligned_knee_measurements[joint + '_rotation_' + side] = rot_aligned_knee_measurements[:, 2]

#     correction_angle = R.from_matrix(correction).as_euler('ZYX', degrees = True)
#     correction_mat[joint + '_flexion_' + side]   = correction_angle[0]
#     correction_mat[joint + '_adduction_' + side] = correction_angle[1]
#     correction_mat[joint + '_rotation_' + side]  = correction_angle[2]

#     if store_correction:
#         return aligned_knee_measurements, correction_mat
    
#     else:
#         return aligned_knee_measurements






# def get_ja_alignment(knee_measurements, knee_kinematics, side, store_correction = False):

#     offset_flexion   = knee_kinematics['knee_flexion_' + side][0] - knee_measurements['knee_flexion_' + side][0]
#     offset_adduction = knee_kinematics['knee_adduction_' + side][0] - knee_measurements['knee_adduction_' + side][0]
#     offset_rotation  = knee_kinematics['knee_rotation_' + side][0] - knee_measurements['knee_rotation_' + side][0]

#     aligned_knee_measurements  = {}

#     aligned_knee_measurements['knee_flexion_' + side]   = knee_measurements['knee_flexion_' + side] + offset_flexion
#     aligned_knee_measurements['knee_adduction_' + side] = knee_measurements['knee_adduction_' + side] + offset_adduction
#     aligned_knee_measurements['knee_rotation_' + side]  = knee_measurements['knee_rotation_' + side] + offset_rotation

#     return aligned_knee_measurements
















