# name: mocap_ik.py 


import pandas as pd
import numpy as np
import sys, os
from tqdm import tqdm
from numpy.linalg import norm, inv
from scipy import signal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import constant_common, constant_mocap
from utils import common


def get_transformation(vx, vy, vz, origin):
    ''' get transformation matrix from vx, vy, vz, origin
    
    Args:
        vx (float): x-axis vector
        vy (float): y-axis vector
        vz (float): z-axis vector
        origin (float): origin point

    Returns:
        transformation (np.array): transformation matrix
    '''
    
    fx = np.append(vx/norm(vx), 0)
    fy = np.append(vy/norm(vy), 0)
    fz = np.append(vz/norm(vz), 0)

    position = np.append(origin, 1)

    transformation = np.transpose([fx, fy, fz, position])

    return transformation


def get_femur_coords(mocap_data, side, num_samples):
    ''' get femur coordinates from mocap data
    
    Args:
        mocap_data (pd.DataFrame): mocap data
        side (str): side, l or r
        num_samples (int): number of samples

    Returns:
        lab_to_femur (np.array, 4x4): transformation matrix from lab to femur
    '''

    lab_to_femur = []

    for i in range(num_samples):
        hip    = np.array([mocap_data[side.upper() + 'GTR X'][i], mocap_data[side.upper() + 'GTR Y'][i], mocap_data[side.upper() + 'GTR Z'][i]])
        knee_l = np.array([mocap_data[side.upper() + 'LK X'][i], mocap_data[side.upper() + 'LK Y'][i], mocap_data[side.upper() + 'LK Z'][i]])
        knee_m = np.array([mocap_data[side.upper() + 'MK X'][i], mocap_data[side.upper() + 'MK Y'][i], mocap_data[side.upper() + 'MK Z'][i]])
        knee_o = (knee_l + knee_m) / 2.0

        vy      = hip - knee_o
        temp_v1 = hip - knee_l
        temp_v2 = knee_m - knee_l

        if side.upper() == constant_common.BODY_RIGHT:
            vz_temp = np.cross(temp_v2, temp_v1)
        elif side == constant_common.BODY_LEFT:
            vz_temp = np.cross(temp_v1, temp_v2)

        vz = np.cross(vz_temp, vy)
        vx = np.cross(vy, vz)

        coord = get_transformation(vx, vy, vz, knee_o)
        lab_to_femur.append(coord)

    return lab_to_femur


def get_tibia_coords(mocap_data, side, num_samples):
    ''' get tibia coordinates from mocap data (see description at get_femur_coords) '''

    lab_to_tibia = []

    for i in range(num_samples):
        knee_l = np.array([mocap_data[side.upper() + 'LK X'][i], mocap_data[side.upper() + 'LK Y'][i], mocap_data[side.upper() + 'LK Z'][i]])
        knee_m = np.array([mocap_data[side.upper() + 'MK X'][i], mocap_data[side.upper() + 'MK Y'][i], mocap_data[side.upper() + 'MK Z'][i]])
        knee_o = (knee_l + knee_m) / 2.0
        ankle_l = np.array([mocap_data[side.upper() + 'LA X'][i], mocap_data[side.upper() + 'LA Y'][i], mocap_data[side.upper() + 'LA Z'][i]])
        ankle_m = np.array([mocap_data[side.upper() + 'MA X'][i], mocap_data[side.upper() + 'MA Y'][i], mocap_data[side.upper() + 'MA Z'][i]])
        ankle_o = (ankle_l + ankle_m) / 2.0

        vy      = knee_o - ankle_o

        if side.upper() == constant_common.BODY_RIGHT:
            vz_temp_knee = knee_l - knee_m
        elif side.upper() == constant_common.BODY_LEFT:
            vz_temp_knee = knee_m - knee_l

        vx = np.cross(vy, vz_temp_knee)
        vz = np.cross(vx, vy)

        coord = get_transformation(vx, vy, vz, knee_o)
        lab_to_tibia.append(coord)

    return lab_to_tibia


def get_thigh_coords(mocap_data, side, num_samples, dataset, opt = 1):
    ''' get thigh cluster coordinates from mocap data (see description at get_femur_coords) '''

    lab_to_thigh = []

    for i in range(num_samples):

        if dataset == 'HAKnee':
            if opt == 1:
                th1 = np.array([mocap_data[side.upper() + 'TSA X'][i], mocap_data[side.upper() + 'TSA Y'][i], mocap_data[side.upper() + 'TSA Z'][i]])
                th2 = np.array([mocap_data[side.upper() + 'TIA X'][i], mocap_data[side.upper() + 'TIA Y'][i], mocap_data[side.upper() + 'TIA Z'][i]])
                th4 = np.array([mocap_data[side.upper() + 'TSP X'][i], mocap_data[side.upper() + 'TSP Y'][i], mocap_data[side.upper() + 'TSP Z'][i]])

            elif opt == 2:
                pass # TODO: implement this

        elif dataset == 'Navio':
            if opt == 1:
                th1 = np.array([mocap_data[side.upper() + 'TH1 X'][i], mocap_data[side.upper() + 'TH1 Y'][i], mocap_data[side.upper() + 'TH1 Z'][i]])
                th2 = np.array([mocap_data[side.upper() + 'TH2 X'][i], mocap_data[side.upper() + 'TH2 Y'][i], mocap_data[side.upper() + 'TH2 Z'][i]])
                th4 = np.array([mocap_data[side.upper() + 'TH4 X'][i], mocap_data[side.upper() + 'TH4 Y'][i], mocap_data[side.upper() + 'TH4 Z'][i]])

            elif opt == 2:
                pass # TODO: implement this

        vy = th1 - th2

        temp_vec = th1 - th4

        vz = np.cross(temp_vec, vy)
        vx = np.cross(vy, vz)

        coord = get_transformation(vx, vy, vz, th1)
        lab_to_thigh.append(coord)

    return lab_to_thigh


def get_shank_coords(mocap_data, side, num_samples, dataset, opt = 1):
    ''' get shank cluster coordinates from mocap data (see description at get_femur_coords) '''

    lab_to_shank = []

    for i in range(num_samples):

        if dataset == 'HAKnee':
            if dataset == 'HAKnee':
                if opt == 1:
                    sh1 = np.array([mocap_data[side.upper() + 'SSA X'][i], mocap_data[side.upper() + 'SSA Y'][i], mocap_data[side.upper() + 'SSA Z'][i]])
                    sh2 = np.array([mocap_data[side.upper() + 'SIA X'][i], mocap_data[side.upper() + 'SIA Y'][i], mocap_data[side.upper() + 'SIA Z'][i]])
                    sh4 = np.array([mocap_data[side.upper() + 'SSP X'][i], mocap_data[side.upper() + 'SSP Y'][i], mocap_data[side.upper() + 'SSP Z'][i]])

                elif opt == 2:
                    pass # TODO: implement this

            elif dataset == 'Navio':
                if opt == 1:
                    sh1 = np.array([mocap_data[side.upper() + 'SK1 X'][i], mocap_data[side.upper() + 'SK1 Y'][i], mocap_data[side.upper() + 'SK1 Z'][i]])
                    sh2 = np.array([mocap_data[side.upper() + 'SK2 X'][i], mocap_data[side.upper() + 'SK2 Y'][i], mocap_data[side.upper() + 'SK2 Z'][i]])
                    sh4 = np.array([mocap_data[side.upper() + 'SK3 X'][i], mocap_data[side.upper() + 'SK3 Y'][i], mocap_data[side.upper() + 'SK3 Z'][i]]) # no SK4 in the Navio dataset

                elif opt == 2:
                    pass # TODO: implement this

        elif dataset == 'Navio':
            pass # TODO: implement this

        vy = sh1 - sh2

        temp_vec = sh1 - sh4

        vz = np.cross(temp_vec, vy)
        vx = np.cross(vy, vz)

        coord = get_transformation(vx, vy, vz, sh1)
        lab_to_shank.append(coord)

    return lab_to_shank


def get_orientation_mocap(mocap_data, dataset = 'HAKnee', tracking = True, task = 'static', cluster_opt = 1):
    ''' get orientation from mocap data
    
    Args:
        mocap_data (pd.DataFrame): mocap data
        dataset (str): dataset name, HAKnee or Navio (NOTE: only biplane side is supported for Navio)
        tracking (bool): tracking or to use the cluster or not
        task (str): task

    Returns:
        mocap_orientation (np.array): orientation of body segments w.r.t. lab frame
    '''

    num_samples = mocap_data.shape[0]

    mocap_orientation = {}

    if tracking: # use tracking markers for IK
        if task == 'static':
            mocap_orientation['lab_to_femur_r'] = get_femur_coords(mocap_data, constant_common.BODY_RIGHT, num_samples)
            mocap_orientation['lab_to_femur_l'] = get_femur_coords(mocap_data, constant_common.BODY_LEFT, num_samples)

            mocap_orientation['lab_to_tibia_r'] = get_tibia_coords(mocap_data, constant_common.BODY_RIGHT, num_samples)
            mocap_orientation['lab_to_tibia_l'] = get_tibia_coords(mocap_data, constant_common.BODY_LEFT, num_samples)

        else:
            mocap_orientation['lab_to_femur_r'] = np.identity(4)
            mocap_orientation['lab_to_femur_l'] = np.identity(4)

            mocap_orientation['lab_to_tibia_r'] = np.identity(4)
            mocap_orientation['lab_to_tibia_l'] = np.identity(4)

        mocap_orientation['lab_to_thigh_r'] = get_thigh_coords(mocap_data, constant_common.BODY_RIGHT, num_samples, dataset, cluster_opt)
        mocap_orientation['lab_to_thigh_l'] = get_thigh_coords(mocap_data, constant_common.BODY_LEFT, num_samples, dataset, cluster_opt)

        mocap_orientation['lab_to_shank_r'] = get_shank_coords(mocap_data, constant_common.BODY_RIGHT, num_samples, dataset, cluster_opt)
        mocap_orientation['lab_to_shank_l'] = get_shank_coords(mocap_data, constant_common.BODY_LEFT, num_samples, dataset, cluster_opt)

    else: # use anatomical markers for IK
        mocap_orientation['lab_to_femur_r'] = get_femur_coords(mocap_data, constant_common.BODY_RIGHT, num_samples)
        mocap_orientation['lab_to_femur_l'] = get_femur_coords(mocap_data, constant_common.BODY_LEFT, num_samples)

        mocap_orientation['lab_to_tibia_r'] = get_tibia_coords(mocap_data, constant_common.BODY_RIGHT, num_samples)
        mocap_orientation['lab_to_tibia_l'] = get_tibia_coords(mocap_data, constant_common.BODY_LEFT, num_samples)

    return mocap_orientation


def calibrate_mocap(mocap_orientation_static, tracking = True):
    ''' calibrate mocap data
    
    Args:
        mocap_orientation_static (np.array): orientation of body segments w.r.t. lab frame
        tracking (bool): tracking or to use the cluster or not

    Returns:
        calibrated_orientation (np.array): calibrated mocap data
    '''

    calibrated_orientation = {}

    if tracking:
        calibrated_orientation['thigh_to_femur_r'] = np.linalg.inv(mocap_orientation_static['lab_to_thigh_r'][0]) @ mocap_orientation_static['lab_to_femur_r'][0]
        calibrated_orientation['thigh_to_femur_l'] = np.linalg.inv(mocap_orientation_static['lab_to_thigh_l'][0]) @ mocap_orientation_static['lab_to_femur_l'][0]
        
        calibrated_orientation['shank_to_tibia_r'] = np.linalg.inv(mocap_orientation_static['lab_to_shank_r'][0]) @ mocap_orientation_static['lab_to_tibia_r'][0]
        calibrated_orientation['shank_to_tibia_l'] = np.linalg.inv(mocap_orientation_static['lab_to_shank_l'][0]) @ mocap_orientation_static['lab_to_tibia_l'][0]
    
    else:
        calibrated_orientation['thigh_to_femur_r'] = np.identity(4)
        calibrated_orientation['thigh_to_femur_l'] = np.identity(4)
        
        calibrated_orientation['shank_to_tibia_r'] = np.identity(4)
        calibrated_orientation['shank_to_tibia_l'] = np.identity(4)

    return calibrated_orientation


def get_knee_kinematics(calibrated_orientation, mocap_orientation, tracking = True):
    ''' get knee kinematics
    
    Args:
        calibrated_orientation (np.array): calibrated orientation
        mocap_orientation (np.array): mocap orientation
        tracking (bool): tracking or to use the cluster or not
    '''

    # num_samples = mocap_orientation['lab_to_femur_r'].shape[0]
    num_samples = len(mocap_orientation)

    knee_kinematics = {}

    if tracking:
        temp_knee_r = common.get_joint_kinematics_from_rot(calibrated_orientation['thigh_to_femur_r'], mocap_orientation['lab_to_thigh_r'], calibrated_orientation['shank_to_tibia_r'], mocap_orientation['lab_to_shank_r'])
        temp_knee_l = common.get_joint_kinematics_from_rot(calibrated_orientation['thigh_to_femur_l'], mocap_orientation['lab_to_thigh_l'], calibrated_orientation['shank_to_tibia_l'], mocap_orientation['lab_to_shank_l'])

    else:
        temp_knee_r = common.get_joint_kinematics_from_rot(calibrated_orientation['thigh_to_femur_r'], mocap_orientation['lab_to_femur_r'], calibrated_orientation['shank_to_tibia_r'], mocap_orientation['lab_to_tibia_r'])
        temp_knee_l = common.get_joint_kinematics_from_rot(calibrated_orientation['thigh_to_femur_l'], mocap_orientation['lab_to_femur_l'], calibrated_orientation['shank_to_tibia_l'], mocap_orientation['lab_to_tibia_l'])

    knee_kinematics['knee_flexion_r']   = constant_common.IK_SIGN['knee_flexion_r'] * temp_knee_r[:, 0]
    knee_kinematics['knee_adduction_r'] = constant_common.IK_SIGN['knee_adduction_r'] * temp_knee_r[:, 1]
    knee_kinematics['knee_rotation_r']  = constant_common.IK_SIGN['knee_rotation_r'] * temp_knee_r[:, 2]

    knee_kinematics['knee_flexion_l']   = constant_common.IK_SIGN['knee_flexion_l'] * temp_knee_l[:, 0]
    knee_kinematics['knee_adduction_l'] = constant_common.IK_SIGN['knee_adduction_l'] * temp_knee_l[:, 1]
    knee_kinematics['knee_rotation_l']  = constant_common.IK_SIGN['knee_rotation_l'] * temp_knee_l[:, 2]

    return knee_kinematics


