![figure [pipeline]: Overview of Experiment 1](../assets/experiment_1.png)

# Experiment 1 (Accuracy Evaluation with Ground-Truth Biplane Fluoroscopy)

This folder contains the implementation to process data of Experiment 1.

## 💾 Data
After downloading data from FigShare, structuring your data folders following the directory tree in `biplane_ref/data/README.md` to run the code.

## 🚀 Run the Code

### Get kinematics
Use `main_ik.py` to obtain inertial or marker-based kinematics. For example, 
```
python main_ik.py --filter_type VQF
```

This command does batch processing for data from all available subjects, tasks, trials, and captured sides (e.g., left or right) with the `VQF` filter. If you would like to obtain inertial kinematics with different approaches, specifically, IMoveLab constraint feedback or OpenSense, simply add `--do_cf` or `--do_opensense`, respectively. 

For marker-based kinematics, run
```
python main_ik.py --do_mocap
```

Kinematics estimation for specific trials is also supported by adding details (see `main_ik.py` for more information).

Outputs from running these scripts will be saved in the `outputs` folder. See `biplane_ref/outputs/README.md` for the structure of this folder.

### Evaluate performance
Use `main_eval.py` to evaluate IMU kinematics using marker-based kinematics as the ground truth.
```
python main_eval.py 
```

Add `do_cf` or `do_opensense` to evaluate kinematics obtained with biomechanical modeling methods.

### Tune filters (optional)
We provide a script, named `main_tuning.py`, to help tune filters with grid search. For example,
```
python main_tuning.py --filter_type VQF 
```

Different filter types can be tuned. 

Add `do_eval` to evaluate performance of different sets of parameters, and then, `check_eval` to get the parameters with the optimal performance.

This is optional, and you can always tune your filters with a different method.


