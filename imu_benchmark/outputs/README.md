# Directory Tree for Outputs (Processed Data) from Experiments 1, 2, and 3

Follow the directory tree below to run the plotting code on your local machine without further modifications.

```
$ Directory tree
.
├── outputs\
    ├── acceleration_sd
    │   ├── acc_dist_s4_cmj.pkl
    │   │── acc_dist_s4_cmj_hh.pkl
    │   │── ...
    │   └── acc_dist_s25_walking_ll.pkl
    ├── exercise_index
    │   ├── s4_exercise_index.xlsx
    │   │── s5_exercise_index.xlsx
    │   │── ...
    │   └── s25_exercise_index.xlsx
    ├── joint_angles
    │   ├── mocap
    │   │   ├── ik_s4_cmj.pkl
    │   │   ├── ik_s4_drop_jump.pkl
    │   │   ├── ...
    │   │   └── ik_s25_walking_x.pkl
    │   │── mt
    │   │   ├── ik_s4_ekf_6D_cmj.pkl
    │   │   ├── ik_s4_ekf_6D_drop_jump.pkl
    │   │   ├── ...
    │   │   └── ik_s25_xsens_9D_walking_x.pkl
    │   │── mvn
    │   │   ├── ik_s4_xsens_9D_running_x.pkl
    │   │   ├── ik_s4_xsens_9D_sts_x.pkl
    │   │   ├── ...
    │   │   └── ik_s25_xsens_9D_walking_x.pkl
    │   └── opensense
    │       ├── ik_s4l_vqf_6D_long_walk1.pkl
    │       ├── ik_s4l_xsens_9D_long_walk1.pkl
    │       ├── ...
    │       └── ik_s25_xsens_9D_walking_x.pkl
    ├── magnetic_sd
    │   ├── mag_dist_s4_cmj.pkl
    │   │── mag_dist_s4_drop_jump.pkl
    │   │── ...
    │   └── mag_dist_s25_walking.pkl
    ├── new_long_walk_opensense
    │   ├── ik_s4l_vqf_6D_long_walk1.pkl
    │   │── ik_s4l_xsens_9D_long_walk1.pkl
    │   │── ...
    │   └── ik_s23l_xsens_9D_long_walk1.pkl
    ├── os_ik
    │   ├── s4_VQF_orientation.sto
    │   │── ik_s4_VQF_orientation.mot
    │   │── ...
    │   └── s13l_Xsens_orientation.sto
    ├── rmse
    │   ├── eval_s4_ekf_6D_cmj_direct_alignment_mt.pkl
    │   │── eval_s4_ekf_6D_drop_jump_direct_alignment_mt.pkl
    │   │── ...
    │   └── eval_s25_xsens_9D_walking_x_direct_mvn.pkl
    ├── rmse_long_walk
    │   ├── s4l_mad_9D_long_walk1_mt.pkl
    │   │── s4l_mad_9D_long_walk1_mt_chunk.pkl
    │   │── ...
    │   └── s23l_xsens_9D_long_walk3_os_chunk.pkl
    ├── rmse_long_walk_ik
    │   ├── s5l_long_walk1_mc_ik.mot
    │   │── s5l_long_walk2_mc_ik.mot
    │   │── ...
    │   └── s5l_xsens_9D_long_walk3_mt_ik.mot
    ├── run_time
    │   └── mt
    │       ├── ik_s4_ekf_6D_cmj.pkl
    │       ├── ik_s4_ekf_6D_drop_jump.pkl
    │       ├── ...
    │       └── ik_s25_xsens_9D_walking.pkl
    └── sync_info
        ├── sync_info_s2_long_walk.pkl
        │── sync_info_s3_long_walk.pkl
        │── ...
        └── sync_info_s25_walking_x.pkl
```




