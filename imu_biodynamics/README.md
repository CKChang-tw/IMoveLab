![figure [pipeline]: Overview of Experiments 1, 2, and 3](../figures/experiment_4.png)

# Experiments 4 (with Ground-Truth Biplane Fluoroscopy)

This folder contains the benchmarking implementation using data collected from Experiment 4 in [the paper]().

## 💾 Data
Data from Experiment 4 can be downloaded from the [HAKnee]() webpage. 

Follow the directory tree in `imu_biodynamics/data/README.md` to run the code properly.

## 🚀 Run the Code
Run `main_mc10.py` to obtain IMU kinematics.
```
python main_mc10.py
```

Run `main_mocap.py` to obtain marker-based kinematics.
```
python main_mocap.py
```

Run `eval.py` to obtain evaluation, but now both IMU and marker-based kinematics comparing to the ground-truth biplane fluoroscopy.
```
python eval.py
```

## 📊 Visualization

See `README.md` in the `outputs` folder to ensure the correct format of the processed data before plotting.

Run `plot_benchmark_f7_biplane.py` files to plot figures.

