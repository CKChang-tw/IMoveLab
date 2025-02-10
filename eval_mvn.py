# name: eval_mvn.py
# description: evaluate kinematics compared to the mocap-based reference (for the sub-experiment with the MVN data)
# author: Vu Phan
# date: 2025/01/22


import argparse
import pickle
import numpy as np 

import matplotlib.pyplot as plt

from imu_benchmark.utils.eval.run_eval_mvn import evaluate


# TODO: get segmentattions for tasks manually (but automatically for walking and running)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--reference', type = str, default = 'direct') # 'direct' or 'opensim
    parser.add_argument('--selected_setup', type = str, default = 'mm') # sensor placement, i.e., 'mm' (for main analysis), 'hh', 'll', or 'ff'

    parser.add_argument('--do_biomodel', action = 'store_true') # kinematics from the OpenSense + MVN biomechanical models

    parser.add_argument('--subject', type = int, default = None) # subject number, if not specified, run all subjects
    parser.add_argument('--task', type = str, default = None) # task being performed, if not specified, run all tasks

    parser.add_argument('--disable_offset_removal', action = 'store_false') # remove offset from the data


    args = parser.parse_args()

    evaluate(args.subject, args.task, args.reference, args.disable_offset_removal, args.selected_setup, args.do_biomodel)


if __name__ == '__main__':
    main()






