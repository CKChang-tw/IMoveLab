![figure [pipeline]: IMU Pipeline Overview](figures/imu_pipeline_overview.png)

# Inertial Motion Tracking Matches Marker-Based Tracking Accuracy: Rethinking Modeling Approaches Towards Future Progress

[![preprint](https://img.shields.io/badge/preprint-link-red)](https://www.biorxiv.org/) <!-- update link for preprint -->
[![data1](https://img.shields.io/badge/data-IMOVE23-brightgreen)](https://sites.google.com/andrew.cmu.edu/i-move-23) 
[![data2](https://img.shields.io/badge/private_data-In_Review-yellow)](https://figshare.com/s/95a87e71c2e3f252a07f) 

**IMULab** is a benchmark of state-estimation filters for tracking and studying human movements using inertial measurement units (IMUs). *A graphical user interface associated with this platform for no-code users will be released soon*.

This platform was initially created and validated for motion tracking of the lower body, but it can also be applied to the upper- or full-body motion tracking with some modifications.

## 🚨 News
- [x] IMU data from Experiments 1, 2, and 3 are now available on the [I-MOVE-23](https://sites.google.com/andrew.cmu.edu/i-move-23) page.
- [ ] The graphical user interface for converting IMU data to lower-limb kinematics will be released soon.

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
The [I-MOVE-23](https://sites.google.com/andrew.cmu.edu/i-move-23) dataset is now available for public use. This contains the data of Experiments 1, 2, and 3 mentioned in the paper. You will need to send a request with your institutional email account to download.

> The [complete dataset](https://figshare.com/s/95a87e71c2e3f252a07f), including the validation study with biplane fluoroscopy, is shared privately with the reviewers, and will be made available upon publication of this manuscript.

See `README.md` in the `imu_benchmark` or `imu_biodynamics` folder for how to store the data.

## 🚀 Run the Code
See `README.md` in the `imu_benchmark` or `imu_biodynamics` folder for how to run the code.

## 🙏 Acknowledgements
We thank the authors of all the state-estimation filters included in this platform, for their contributions and for making their work open-sourced.

## 📄 Citation
If you use any part of the data or code, please cite [our paper]().
```
@ARTICLE{phan2025,  
title   =   {Inertial Motion Tracking Matches Marker-Based Tracking Accuracy: Rethinking Modeling Approaches Towards Future Progress},
author  =   {Phan, Vu and Li, Zhixiong and Meinders, Evy and Gale, Tom and Anderst, William and Ng-Thow-Hing, Julian and Khandan, Aminreza and Halilaj, Eni},  
journal =   {In Submission},  
year    =   {2025}  
}  
```

If you find this repository helpful, do not hesitate to give it a ⭐.

## ✉️ Contact
Please contact Vu Phan (vuphan@andrew.cmu.edu) regarding any question and feedback.



