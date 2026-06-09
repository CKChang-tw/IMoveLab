# name: constant_mc10.py


# Physics
GRAV_ACC = 9.81 # m/s^2

# Experimental setup
DATA_SAMPLING_RATE = 250 # Hz
PROCESSING_RATE    = 100 # Hz (resampled to 100 Hz)
# PROCESSING_RATE    = 150 # Hz (resampled to 100 Hz)

# Processing setup
FILTER_CUTOFF_IMU = 20 # Hz
FILTER_ORDER = 4

# Mapping for sensor name (BioStampRC MC10)
SENSOR_NAME_MAP = {'thigh_r': 'lateral_thigh_right',
                   'thigh_l': 'lateral_thigh_left',
                   'shank_r': 'lateral_shank_right',
                   'shank_l': 'lateral_shank_left'}

# Data headers
IMU_DATA_HEADERS = ['Timestamp', 'Acc_X', 'Acc_Y', 'Acc_Z', 'Gyr_X', 'Gyr_Y', 'Gyr_Z']

# Conversion
MILI_TO_MICRO = 1e3
TO_MICRO      = 1e6

# Indices
META_START_ID = 0
META_STOP_ID = 1












