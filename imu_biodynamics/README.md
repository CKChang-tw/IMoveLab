![figure [pipeline]: Overview of Experiments 1, 2, and 3](../figures/experiment_4.png)

# Experiment 4 (with Ground-Truth Biplane Fluoroscopy)

This folder contains the implementation to process data of Experiment 4.

## 💾 Data
After downloading data from FigShare, follow the directory tree in `imu_biodynamics/data/README.md` to run the code.

## 🚀 Run the Code
Run `main_mc10.py` to obtain IMU kinematics.
```
python main_mc10.py
```

Run `main_mocap.py` to obtain marker-based kinematics.
```
python main_mocap.py
```

Run `eval.py` to obtain evaluation of IMU and marker-based kinematics against ground-truth biplane fluoroscopy.
```
python eval.py
```

Outputs from running these scripts are saved in the `outputs` folder.

## 📊 Visualization

See `README.md` in the `outputs` folder to ensure to ensure that the data are formatted appropriately before plotting them.

If you do not wish obtain `outputs` from running the scripts above, you can also download the folder from FigShare and format it following the mentioned `README.md` file for visualization.

Run `plot_benchmark_f7_biplane.py` to plot the figure.
```
python plot_benchmark_f7_biplane.py
```

