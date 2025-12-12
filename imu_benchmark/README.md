![figure [pipeline]: Overview of Experiments 1, 2, and 3](../figures/experiment_1_to_3.png)

# Experiments 1, 2, and 3 (with Ground-Truth Marker-Based Motion Capture)

This folder contains the benchmarking implementation using data collected from Experiments 1, 2, and 3 in [the paper]().

## 💾 Data
Data from Experiments 1, 2, and 3 can be downloaded from the [I-MOVE-23](https://sites.google.com/andrew.cmu.edu/i-move-23) webpage. 

Follow the directory tree in `imu_benchmark/data/README.md` to run the code properly.

## 🚀 Run the Code
### Set path
Set `PYTHONPATH`.
```
export PYTHONPATH=$PYTHONPATH:/path/to/imu_benchmark
```

### Synchronize data
Run `synchronizer.py` to obtain sync indices between IMU and mocap data.
```
python imu_benchmark/synchronizer.py [--subject SUBJECT] [--task TASK] [--do_mvn]
```

The code will run for all subjects (or tasks) if `subject` (or `task`) is not specified. Set `do_mvn` to process data collected with the MVN Analyze software (from **Experiment 3**).

### Get IK
Run `main_ik.py` to obtain IMU (constrained if `do_opensense` is set, otherwise direct) and marker-based kinematics (for **Experiment 1**).
```
python imu_benchmark/main_ik.py [--selected_setup SELECTED_SETUP] [--f_type F_TYPE] [--dim DIM] [--do_mocap] [--do_mvn] [--do_opensense] [--subject SUBJECT] [--task TASK]
```

- Use `mm` for mid placements of IMUs on thighs and shanks. 
- Use `vqf`, `xsens`, `ekf`, `mad`, `mah`, or `riann` for `f_type`.
- To use magnetometer information, set `9d` for `dim`, otherwise, `6d`. 
- Set `do_mocap` to get marker-based kinematics instead. Of note, no IMU kinematics will be obtained if this is set.
- Set `do_opensense` to run constrained IMU kinematics with OpenSense.

Similarly, run `main_ik_long.py` (for **Experiment 2**) and `main_ik_mvn.py` (for **Experiment 3**).

### Evaluate IK
Run `eval.py` to evaluate IMU kinematics using marker-based kinematics as the ground truth.
```
python imu_benchmark/eval.py [--f_type F_TYPE] [--dim DIM] [--reference REFERENCE] [--selected_setup SELECTED_SETUP] [--enable_opensense] [--subject SUBJECT] [--task TASK] [--enable_mocap_alignment] [--enable_psa]
```

- (Always) set `enable_mocap_alignment` to align IMU and marker-based kinematics before evaluation. 
- Set `enable_psa` to evaluate kinematics obtained from the static calibration instead of functional calibration (as default).

Similarly, run `eval_long.py` (for **Experiment 2**) and `eval_mvn.py` (for **Experiment 3**). 

## 📊 Visualization

See `README.md` in the `outputs` folder to ensure to ensure that the data are formatted appropriately before plotting them.

If you do not wish obtain `outputs` from running the scripts above, you can also download the folder from FigShare and format it following the mentioned `README.md` file for visualization.

Run `plot_benchmark_f<*>.py` files to plot figures, in which `<*>` stands for the figure index to be plotted. For example, 
```
python imu_benchmark/plot_benchmark_f3.py
```

