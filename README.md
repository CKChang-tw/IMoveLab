# Inertial Motion Tracking Now Matches Marker-Based Tracking Accuracy: Rethinking Modeling Approaches Towards Future Progress

[![preprint](https://img.shields.io/badge/preprint-link-red)](https://www.biorxiv.org/) <!-- update link for preprint -->
[![data](https://img.shields.io/badge/data-IMOVE23-brightgreen)](https://sites.google.com/andrew.cmu.edu/i-move-23) <!-- update link for data -->
[![license](https://img.shields.io/badge/license-TBD-yellow)](https://www.biorxiv.org/) <!-- update link for license -->

IMULab is a benchmark of state-estimation filters for tracking and studying human movements using inertial measurement units (IMUs). A graphical user interface associated with this platform for non-code users can also be found at this [link](https://www.biorxiv.org/).

This platform was initially created and validated for motion tracking of the lower body, but it can also be applied to the upper- or full-body motion tracking with some modifications.


## ⚙️ Installation
The code is fully tested with `Python 3.10` on `Ubuntu 24.04`. We recommend creating environments with `conda` to run the code.
```
conda create --name imu_benchmark python==3.10
conda activate imu_benchmark
```

See [AHRS](https://ahrs.readthedocs.io/en/latest/installation.html), [VQF](https://vqf.readthedocs.io/en/stable/installation.html), and [RIANN](https://github.com/daniel-om-weber/riann) to install packages for state-estimation filters.

See [Scripting in Python](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53085346/Scripting+in+Python) to install the `opensim` package for use of biomechanical modeling.

Run `python -m pip install -r requirements.txt` for other dependencies.

## 💾 Data
You will need to send a request with your institutional email account to download:
- the [I-MOVE-23](https://sites.google.com/andrew.cmu.edu/i-move-23) dataset, and
- the [HAKnee]() dataset.

See `README.md` in the `imu_benchmark` or `imu_biodynamics` folder for how to store the data.

## 🚀 Demo
See `README.md` in the `imu_benchmark` or `imu_biodynamics` folder for how to run the code.

## 🙏 Acknowledgements
We thank the authors of all the state-estimation filters included in this platform, not only for their novel contributions but also for their open sources for public use.

## 📄 Citation
If you use any part of the data or code, please cite [our paper]().
```
@InProceedings{phan2025,  
title={Inertial Motion Tracking Now Matches Marker-Based Tracking Accuracy: Rethinking Modeling Approaches Towards Future Progress},
author={Phan, Vu and Li, Zhixiong and Meinders, Evy and Gale, tom and Anderst, William and Ng-Thow-Hing, Julian and Khandan, Aminreza and Halilaj, Eni},  
booktitle={in submission},  
year={2025}  
}  
```

If find this repository helpful for your research, please give it a ⭐.

## ⚖️ License 
*(To be defined)*.

## ✉️ Contact
Please contact Vu Phan (vuphan@andrew.cmu.edu) regarding any question and feedback.



