# name: common.py


import numpy as np

from scipy.spatial.transform import Rotation as R


def rot_to_euler(rot_mat):
    ''' convert rotation matrix to euler angles (zxy convention)
    
    Args:
        rot_mat (np.array): rotation matrix
        
    Returns:
        euler (np.array): Euler angle with the zxy-sequence 
    '''

    euler = R.from_matrix(rot_mat).as_euler('zxy', degrees = True)

    # euler = R.from_matrix(rot_mat).as_euler('zyx', degrees = True)
    # euler = R.from_matrix(rot_mat).as_euler('xyz', degrees = True)

    return euler


def get_joint_kinematics_from_rot(proximal_segment_to_bone, proximal_lab_to_segment, distal_segment_to_bone, distal_lab_to_segment):
    ''' get joint kinematics from calibrated and oriented body segments
    
    Args:
        proximal_segment_to_bone (np.array): calibrated proximal body segment
        proximal_lab_to_segment (np.array): oriented proximal body segment
        distal_segment_to_bone (np.array): calibrated distal body segment
        distal_lab_to_segment (np.array): oriented distal body segment

    Returns:
        angles_arr (np.array): joint angles
    '''

    angles_arr = []
    
    num_samples = len(proximal_lab_to_segment)

    for i in range(num_samples):
        proximal_lab_to_bone = proximal_lab_to_segment[i] @ proximal_segment_to_bone
        distal_lab_to_bone   = distal_lab_to_segment[i] @ distal_segment_to_bone

        joint_rot   = np.linalg.inv(proximal_lab_to_bone) @ distal_lab_to_bone
        joint_euler = rot_to_euler(joint_rot[0:3, 0:3])

        angles_arr.append(joint_euler)

    return np.array(angles_arr)


def quat_to_euler(quat, to_deg = True):
    ''' convert quaternion to euler angles (zxy convention)
    
    Args:
        quat (np.array): quaternion
        to_deg (bool): convert to degrees if True

    Returns:
        euler (np.array): Euler angle with the zxy-sequence 
    '''

    r = R.from_quat(quat, scalar_first = True)

    euler = r.as_euler('zxy', degrees = to_deg)

    return euler


def get_joint_kinematics_from_quat(proximal_lab_to_bone, proximal_lab_to_segment, distal_lab_to_bone, distal_lab_to_segment):
    pass # TODO: implement this






