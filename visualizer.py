# name: visualizer.py
# description: visualize the results
# author: Vu Phan
# date: 2024/09/22


import argparse
import pickle
import numpy as np
import matplotlib.pyplot as plt

from imu_benchmark.utils.visualization import plot


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--f_type', type = str, default = 'Xsens') # 'Xsens', 'MAH', 'VQF', 'MAD', or 'EKF'
    parser.add_argument('--dim', type = str, default = '9d') # '9d' or '6d'
    parser.add_argument('--reference', type = str, default = 'direct') # 'direct' or 'opensim
    parser.add_argument('--selected_setup', type = str, default = 'mm') # sensor placement, i.e., 'mid' (for main analysis), 'high', 'low', or 'front'

    parser.add_argument('--subject', type = int, default = None) # subject number, if not specified, run all subjects
    parser.add_argument('--task', type = str, default = None) # task being performed, if not specified, run all tasks
    parser.add_argument('--joint', type = str, default = None) # joint being evaluated, if not specified, run all joints

    parser.add_argument('--source', type = str, default = 'mt') # data source, i.e., 'mt' or 'mvn'

    parser.add_argument('--disable_offset_removal', action = 'store_false') # remove offset from the data

    parser.add_argument('--enable_segmentation', action = 'store_true') # enable segmentation

    parser.add_argument('--add_peaks', action = 'store_true') # add peaks to the plot


    args = parser.parse_args()

    if args.enable_segmentation:
        plot.plot_segmented(args.f_type, args.dim, args.subject, args.task, args.joint, args.reference, args.disable_offset_removal, args.selected_setup, args.source)

    else:
        plot.plot_raw(args.f_type, args.dim, args.subject, args.task, args.joint, args.reference, args.disable_offset_removal, args.add_peaks, args.selected_setup)


if __name__ == '__main__':
    main()



