# name: main_ik.py
# description: main file for inverse kinematics
# author: Vu Phan
# date: 2024/09/13


import argparse

from imu_benchmark.utils import common
from imu_benchmark.scripts import run_mt_opensense, run_mt, run_mocap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selected_setup', type = str, default = 'mm') # sensor placement, i.e., 'mm' (for main analysis), 'hh', 'll', or 'ff'
    parser.add_argument('--f_type', type = str, default = None) # 'Xsens', 'MAH', 'VQF', 'MAD', or 'EKF'
    parser.add_argument('--dim', type = str, default = '9d') # '9d' or '6d'

    parser.add_argument('--do_mocap', action = 'store_true') # run mocap

    parser.add_argument('--do_mvn', action = 'store_true') # run IMU data collected from MVN instead of MTw Manager TODO: implement this function
    parser.add_argument('--do_opensense', action = 'store_true') # run OpenSense for IMU data    
    parser.add_argument('--disable_offset_removal', action = 'store_false') # remove offset from the data

    parser.add_argument('--subject', type = int, default = None) # subject number, if not specified, run all subjects
    parser.add_argument('--task', type = str, default = None) # task being performed, if not specified, run all tasks

    args = parser.parse_args()

    if args.do_mocap:
        run_mocap.mocap_ik(args.subject, args.task, args.disable_offset_removal)

    else:
        if args.f_type is None:
            filter_config_check = True
        else:
            filter_config_check, error_msg = common.check_filter_config(args.f_type, args.dim)

        if filter_config_check:
            if args.do_opensense:
                run_mt_opensense.mt_ik_opensense(args.selected_setup, args.f_type, args.dim, args.subject, args.task, args.disable_offset_removal) # TODO: implement this function

            else:
                run_mt.mt_ik(args.selected_setup, args.f_type, args.dim, args.subject, args.task, args.disable_offset_removal) 
        else:
            print(error_msg)


if __name__ == '__main__':
    main()





