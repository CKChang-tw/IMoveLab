# name: eval.py
# description: evaluate kinematics compared to the mocap-based reference
# author: Vu Phan
# date: 2024/09/13


import argparse
import pickle
import numpy as np 

import matplotlib.pyplot as plt

from imu_benchmark.utils.eval.run_eval import evaluate


# TODO: get segmentattions for tasks manually (but automatically for walking and running)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--f_type', type = str, default = None) # 'Xsens', 'MAH', 'VQF', 'MAD', or 'EKF'
    parser.add_argument('--dim', type = str, default = '9d') # '9d' or '6d'
    parser.add_argument('--reference', type = str, default = 'direct') # 'direct' or 'opensim
    parser.add_argument('--selected_setup', type = str, default = 'mm') # sensor placement, i.e., 'mm' (for main analysis), 'hh', 'll', or 'ff'

    parser.add_argument('--enable_opensense', action = 'store_true') # disable OpenSense

    parser.add_argument('--subject', type = int, default = None) # subject number, if not specified, run all subjects
    parser.add_argument('--task', type = str, default = None) # task being performed, if not specified, run all tasks

    parser.add_argument('--enable_mocap_alignment', action = 'store_true') # enable mocap alignment
    parser.add_argument('--enable_psa', action = 'store_true') # to evaluate data with PSA (perfect standing assumption)


    args = parser.parse_args()

    evaluate(args.f_type, args.dim, args.subject, args.task, args.reference, args.enable_mocap_alignment, args.selected_setup, args.enable_opensense, args.enable_psa)


if __name__ == '__main__':
    main()



