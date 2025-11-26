# name: constant_mvn.py
# description: constants for Xsens IMUs
# author: Vu Phan
# date: 2025/01/15


# Biomechanical model
MVN_SAMPLING_RATE = 60 # Hz

# Data sheets
MVN_JOINT_ANGLE_SHEET  = 'Joint Angles ZXY' # can use 'Joint Angles XZY' as an alternative
MVN_ACCELERATION_SHEET = 'Sensor Free Acceleration'
MVN_MAGNETOMETER_SHEET = 'Sensor Magnetic Field'
MVN_ORIENTATION_SHEET  = 'Sensor Orientation - Quat'

# Name mapping
# MVN_PLACEMENT_MAP = {'torso_imu': None,
#                      'pelvis_imu': 'Pelvis', 
#                      'calcn_r_imu': 'Right Foot', 'tibia_r_imu': 'Right Lower Leg', 'femur_r_imu': 'Right Upper Leg',
#                      'calcn_l_imu': 'Left Foot', 'tibia_l_imu': 'Left Lower Leg', 'femur_l_imu': 'Left Upper Leg'}
MVN_PLACEMENT_MAP = {'chest': None,
                     'pelvis': 'Pelvis', 
                     'foot_r': 'Right Foot', 'shank_r': 'Right Lower Leg', 'thigh_r': 'Right Upper Leg',
                     'foot_l': 'Left Foot', 'shank_l': 'Left Lower Leg', 'thigh_l': 'Left Upper Leg'}

MVN_JOINT_ANGLE_MAP  = {'hip_rotation_l':    'Left Hip Internal/External Rotation', 
                        'hip_flexion_l':     'Left Hip Flexion/Extension', 
                        'hip_adduction_l':   'Left Hip Abduction/Adduction', 
                        'knee_flexion_l':    'Left Knee Flexion/Extension', 
                        'knee_adduction_l':  'Left Knee Abduction/Adduction',
                        'knee_rotation_l':   'Left Knee Internal/External Rotation',
                        'ankle_flexion_l':   'Left Ankle Dorsiflexion/Plantarflexion',
                        'ankle_adduction_l': 'Left Ankle Abduction/Adduction',
                        'ankle_rotation_l':  'Left Ankle Internal/External Rotation',

                        'hip_rotation_r':    'Right Hip Internal/External Rotation', 
                        'hip_flexion_r':     'Right Hip Flexion/Extension', 
                        'hip_adduction_r':   'Right Hip Abduction/Adduction', 
                        'knee_flexion_r':    'Right Knee Flexion/Extension', 
                        'knee_adduction_r':  'Right Knee Abduction/Adduction',
                        'knee_rotation_r':   'Right Knee Internal/External Rotation',
                        'ankle_flexion_r':   'Right Ankle Dorsiflexion/Plantarflexion',
                        'ankle_adduction_r': 'Right Ankle Abduction/Adduction',
                        'ankle_rotation_r':  'Right Ankle Internal/External Rotation'}















