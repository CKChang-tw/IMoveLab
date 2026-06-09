# name: constant_common.py


# --- Data path --- #
DATA_PATH    = 'data/'
IMU_PATH     = 'IMUs/' # raw IMU data from the MC10 Biostamp system
MOCAP_PATH   = 'Vicon/' # raw mocap data from Vicon
BIPLANE_PATH = 'Kinematics/' # exported "kinematics" from the biplane data

HA_DATASET_PATH    = 'HAKnee/' # raw data from the HAKnee dataset
NAVIO_DATASET_PATH = 'Navio/' # raw data from the Navio dataset

# --- Output path --- #
OUT_MOCAP_IK_PATH = 'outputs/ik/mocap/'
OUT_IMU_IK_PATH   = 'outputs/ik/imu/'

# --- Subject list --- #
# HA_SUBJECT_LIST = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] # no IMU data for subject 7, no sync info for subject 8
HA_SUBJECT_LIST = [1, 2, 3, 4, 5, 6, 9, 10, 12, 13, 14, 15, 16, 17, 18] # no static data for subject 11 and 19

# NAVIO_SUBJECT_LIST = [201, 202, 203, 204, 205, 206, 207, 208, 209, 210]
NAVIO_SUBJECT_LIST = [201, 202, 204, 205, 206, 207, 208, 210] # no biplane data for 203 & 209

# --- Task list --- #
HA_TASK_MAPPING = {'static': 'static',      # T-pose
                   'shop':   'SHop',        # single-leg hop with 180 degrees rotation
                   'sdrop':  'SDrop',       # single-leg drop jump
                   'ddrop':  'DDrop',       # double-leg drop jump
                   'run':    'runStance',   # run
                   }

NAVIO_TASK_MAPPING = {'static':      'static',
                      'walk_swing':  'walkswing',
                      'walk_stance': 'walkstance',
                      'cr':          'cr', # chair rise
                      'sd':          'sd', # stair descent
                      'sa':          'sa', # stair ascent
                      'lunge':       'l',
                      'pr':          'pr', # pivot right
                      'pl':          'pl', # pivot left
                      }

# HA_TASK_MAPPING = {'static': 'static',      # T-pose
#                    'ddrop':  'DDrop',       # double-leg drop jump
#                    'sdrop':  'SDrop',       # single-leg drop jump
#                    'shop':   'SHop',        # single-leg hop with 180 degrees rotation
#                    'run':    'runStance',   # run
#                    }

HA_NUM_TRIALS = {'static': 1,
                 'ddrop':  3,
                 'sdrop':  3,
                 'shop':   4,
                 'run':    3}


# --- File format --- #
MOCAP_EXTENSION = '.c3d' # extension for mocap data (labelled from Vicon)
IMU_EXTENSION   = '.csv' # extension for IMU data
TT_EXTENSION    = '.xlsx' # extension for trigger times



# --- Body side --- #
BODY_RIGHT = 'R'
BODY_LEFT  = 'L'

# --- IK sign --- #
IK_SIGN = {'hip_adduction_l': -1,   'hip_rotation_l': -1,   'hip_flexion_l': 1,
           'knee_adduction_l': -1,  'knee_rotation_l': -1,  'knee_flexion_l': -1, 
           'ankle_adduction_l': -1, 'ankle_rotation_l': -1, 'ankle_flexion_l': 1, 
           'hip_adduction_r': 1,    'hip_rotation_r': 1,    'hip_flexion_r': 1,
           'knee_adduction_r': 1,   'knee_rotation_r': 1,   'knee_flexion_r': -1,
           'ankle_adduction_r': 1,  'ankle_rotation_r': 1,  'ankle_flexion_r': 1}




STATIC_STANDING_PERIOD = 1

