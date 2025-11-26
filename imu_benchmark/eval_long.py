# name: eval_long.py
# description: evaluate kinematics compared to the mocap-based reference during hour-long trials
# author: Vu Phan
# date: 2025/05/08


import argparse
import pickle
import numpy as np 

import matplotlib.pyplot as plt

from imu_benchmark.utils.eval.run_eval_long import evaluate


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--f_type', type = str, default = 'VQF') # 'Xsens', 'MAH', 'VQF', 'MAD', or 'EKF'
    parser.add_argument('--dim', type = str, default = '9d') # '9d' or '6d'
    parser.add_argument('--reference', type = str, default = 'direct') # 'direct' or 'opensim

    parser.add_argument('--subject', type = str, default = None) # subject number, if not specified, run all subjects

    parser.add_argument('--enable_mocap_alignment', action = 'store_true') # enable mocap alignment
    parser.add_argument('--enable_opensense', action = 'store_true') # disable OpenSense


    args = parser.parse_args()

    evaluate(args.f_type, args.dim, args.subject, args.reference, args.enable_mocap_alignment, args.enable_opensense)


if __name__ == '__main__':
    main()




