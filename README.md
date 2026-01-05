![figure [pipeline]: IMU Pipeline Overview](figures/imu_pipeline_overview.png)

# Inertial Motion Tracking Matches Marker-Based Tracking Accuracy: Rethinking Modeling Approaches Towards Future Progress

[![preprint](https://img.shields.io/badge/preprint-link-red)]() <!-- update link for preprint -->
[![data2](https://img.shields.io/badge/private_data-In_Review-yellow)](https://figshare.com/s/95a87e71c2e3f252a07f) 

**IMULab** is a workflow for state estimation and tracking of human movements with inertial measurement units (IMUs). A web app  for users who may not wish to interact with the code is also being developed and will be released no later than the acceptance/publication of this manuscript.

## 📂 Structure
See `imu_benchmark` for the implementation associated with Experiments 1, 2, and 3 presented in the paper; `imu_biodynamics` for Experiment 4.

## ⚙️ Installation
The code is tested with `Python 3.10` on `Ubuntu 24.04` and `MacOS`. We recommend creating environments with `conda` to run the code.
```
conda create --name imu_benchmark python==3.10
conda activate imu_benchmark
```

See [AHRS](https://ahrs.readthedocs.io/en/latest/installation.html), [VQF](https://vqf.readthedocs.io/en/stable/installation.html), and [RIANN](https://github.com/daniel-om-weber/riann) to install packages for state-estimation filters.

See [Scripting in Python](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53085346/Scripting+in+Python) to install the `opensim` package for use of biomechanical modeling.

Run `python -m pip install -r requirements.txt` for other dependencies.

## 💾 Data
The [complete dataset](https://figshare.com/s/95a87e71c2e3f252a07f) is available for reviewers on FigShare, and will be published upon the acceptance/publication of the manuscript.

See `README.md` in the `imu_benchmark` or `imu_biodynamics` folder for how to store the data.

## 🚀 Run the Code
See `README.md` in the `imu_benchmark` or `imu_biodynamics` folder for how to run the code.




