![figure [pipeline]: Overview of Experiments 2 and 3](../assets/experiments_2_and_3.jpg)

# Experiments 2 and 3 (Drift Evaluation with Ground-Truth Marker-Based Motion Capture)

This folder contains the benchmarking implementation using data collected from Experiments 2 and 3 in [the paper]().

## 💾 Data
### Sensor Placement and Orientation

Xsens MTw Awinda inertial sensors were used for motion tracking. The sensor coordinate frames were configured as follows:
- Right Thigh & Shank: `X = Upward`, `Y = Backward`, `Z = Lateral` (Right)
- Left Thigh & Shank: `X = Upward`, `Y = Forward`, `Z = Lateral` (Left)
- Foot (Dorsal Surface): `X = Proximal`, `Y = Right`, `Z = Outward` (Dorsal Normal)
- Pelvis (Lower Back): `X = Upward`, `Y = Left`, `Z = Backward`

### Sampling Frequencies

- Experiment 2: Data collected at 40 Hz (includes additional thigh/shank sensors for placement impact analysis).
- Experiment 3: Data collected at 100 Hz.

### Data tree
After downloading data from FigShare, structuring your data folders following the directory tree in `mocap_ref/data/README.md` to run the code.

## 🚀 Run the Code

### Get kinematics
Use `main_ik.py` to obtain inertial (with biomechanical modeling if `do_constraint_feedback` or `do_opensense` is set, otherwise direct) and marker-based kinematics (for **Experiment 2**).
```
python main_ik.py 
```

The above command will do batch processing to obtain kinematics for all subjects, tasks, and filters with 9-axis IMU data. Set `--dim 6d` for batch processing with 6-axis IMU data. Options for processing data of individual trials are also available (see `main_ik.py` for more details). If `do_mocap` is set, marker-based kinematics will be estimated.

Similarly, run `main_ik_long.py` (for **Experiment 3**) to obtain inertial and marker-based kinematics of long-duration trials.

### Evaluate performance
Use `eval.py` to evaluate IMU kinematics using marker-based kinematics as the ground truth (for **Experiment 2**).
```
python eval.py --enable_mocap_alignment --enable_drift_eval
```

Add `enable_cf` or `enable_opensense` to evaluate kinematics obtained with biomechanical modeling methods.

Similarly, run `eval_long.py` (for **Experiment 3**). 
```
python eval_long.py --enable_mocap_alignment
```

### Tune filters (Optional)
We provide a script, named `main_tuning.py`, to help tune filters with grid search. For example,
```
python main_tuning.py --filter_type VQF --dim 9d
```

Different filter types can be tuned (whether with magnetometer, i.e., 9D, or not, i.e., 6D). 

Add `do_eval` to evaluate performance of different sets of parameters, and then, `check_eval` to get the parameters with the optimal performance.

This is optional, and you can always tune your filters with a different method.


## 📝 Notes on the sensor-to-segment calibration
### Functional Calibration Guidelines
Functional calibration in this pipeline relies on two main principles:
- Static tasks (e.g., static standing or static toe touching): The average 3-axis accelerometer data is used to identify the gravity vector, which may be assumed to align with a specific body axis (e.g., the proximal-distal longitudinal axis during static standing).
- Dynamic tasks (e.g., walking or squatting): principal component analysis (PCA) is applied to the 3-axis gyroscope data to identify the primary axis of motion.

Beyond the specific protocol used in this study, alternative calibration tasks following these two principles can also be applied.


### Calibration Types
This study performs full calibration for each sensor, which requires two calibration tasks (typically one static and one dynamic, two static, or two dynamic).

When only a single task (typically static standing) is available, the calibration is partial and only aligns a single axis. The common partial calibration is vertical calibration with only static standing.

