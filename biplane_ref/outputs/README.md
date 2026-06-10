# Experiment 4 Processed Data

This folder contains processed data outputted from running the code.

```
$ Directory tree
.
├── data\
    └── HAKnee
        ├── bm_ekf6d
        │   ├── eval
        │   │   ├── 1
        │   │   │   ├── biplane
        │   │   │   │   ├── knee_kinematics_l_ddrop_3.pkl
        │   │   │   │   ├── knee_kinematics_l_run_1.pkl
        │   │   │   │   ├── ...
        │   │   │   │   └── knee_kinematics_r_shop_2.pkl
        │   │   │   ├── mc10
        │   │   │   │   ├── knee_kinematics_l_ddrop_3.pkl
        │   │   │   │   ├── knee_kinematics_l_run_1.pkl
        │   │   │   │   ├── ...
        │   │   │   │   └── knee_kinematics_r_shop_2.pkl
        │   │   │   ├── mocap
        │   │   │   │   ├── knee_kinematics_l_ddrop_3.pkl
        │   │   │   │   ├── knee_kinematics_l_run_1.pkl
        │   │   │   │   ├── ...
        │   │   │   │   └── knee_kinematics_r_shop_2.pkl
        │   │   │   ├── rmsd_mc10_biplane_l_ddrop_3.pkl
        │   │   │   ├── ...
        │   │   │   └── rmsd_mocap_biplane_r_shop_2.pkl
        │   │   ├── 2
        │   │   ├── ...
        │   │   └── 18
        │   ├── eval_os
        │   │   ├── 1
        │   │   │   ├── biplane
        │   │   │   │   ├── knee_kinematics_l_ddrop_3.pkl
        │   │   │   │   ├── knee_kinematics_l_run_1.pkl
        │   │   │   │   ├── ...
        │   │   │   │   └── knee_kinematics_r_shop_2.pkl
        │   │   │   ├── mc10
        │   │   │   │   ├── knee_kinematics_l_ddrop_3.pkl
        │   │   │   │   ├── knee_kinematics_l_run_1.pkl
        │   │   │   │   ├── ...
        │   │   │   │   └── knee_kinematics_r_shop_2.pkl
        │   │   │   ├── mocap
        │   │   │   │   ├── knee_kinematics_l_ddrop_3.pkl
        │   │   │   │   ├── knee_kinematics_l_run_1.pkl
        │   │   │   │   ├── ...
        │   │   │   │   └── knee_kinematics_r_shop_2.pkl
        │   │   │   ├── rmsd_mc10_biplane_l_ddrop_3.pkl
        │   │   │   ├── ...
        │   │   │   └── rmsd_mocap_biplane_r_shop_2.pkl
        │   │   ├── 2
        │   │   ├── ...
        │   │   └── 18
        │   │──  ik
        │   │   ├── 1
        │   │   │   ├── mc10
        │   │   │   │   ├── knee_kinematics_l_ddrop_1.pkl
        │   │   │   │   ├── knee_kinematics_l_ddrop_2.pkl
        │   │   │   │   ├── ...
        │   │   │   │   └── knee_kinematics_r_shop_3.pkl
        │   │   │   └── mocap
        │   │   │       ├── knee_kinematics_l_ddrop_1.pkl
        │   │   │       ├── knee_kinematics_l_ddrop_2.pkl
        │   │   │       ├── ...
        │   │   │       └── knee_kinematics_r_shop_3.pkl
        │   │   ├── 2
        │   │   ├── ...
        │   │   └── 18
        │   └── ik_os
        │       ├── 1
        │       │   ├── mc10
        │       │   │   ├── knee_kinematics_l_ddrop_1.pkl
        │       │   │   ├── knee_kinematics_l_ddrop_2.pkl
        │       │   │   ├── ...
        │       │   │   └── knee_kinematics_r_shop_3.pkl
        │       │   └── mocap
        │       │       ├── knee_kinematics_l_ddrop_1.pkl
        │       │       ├── knee_kinematics_l_ddrop_2.pkl
        │       │       ├── ...
        │       │       └── knee_kinematics_r_shop_3.pkl
        │       ├── 2
        │       ├── ...
        │       └── 18
        ├── bm_ekf6d_constrained_90p
        ├── bm_mad6d
        ├── bm_mad6d_constrained_90p
        ├── bm_mah6d
        ├── bm_mah6d_constrained_90p
        ├── bm_vqf6d
        ├── bm_vqf6d_constrained_90p
        └── bm_riann6d
```

In this folder, each sub-folder (e.g., `bm_vqf6d`) stores kinematics and evaluation results obtained from different filters. Those with the `*_constrained_90` stores kinematics and evaluation results obtained with the IMoveLab feedback constrained method. 

