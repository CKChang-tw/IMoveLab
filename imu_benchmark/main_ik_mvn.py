# name: main_ik_mvn.py
# description: IMU-based IK for MVN data collected from a sub-experiment
# author: Vu Phan
# date: 2025/01/16


import argparse

from imu_benchmark.utils import common
from imu_benchmark.scripts import run_mvn, run_mocap, run_mvn_opensense, run_mvn_biomodel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--do_mocap', action = 'store_true') # run mocap
    parser.add_argument('--mvn_orientation', action = 'store_true') # do IK using Xsens orientation data
    parser.add_argument('--mvn_opensense', action = 'store_true') # do IK by applying OpenSense on Xsens orientation data
    parser.add_argument('--mvn_biomodel', action = 'store_true') # get IK results from the MVN biomechanical model
    
    parser.add_argument('--disable_offset_removal', action = 'store_false') # remove offset from the data

    parser.add_argument('--subject', type = int, default = None) # subject number, if not specified, run all subjects
    parser.add_argument('--task', type = str, default = None) # task being performed, if not specified, run all tasks

    args = parser.parse_args()

    if args.do_mocap:
        run_mocap.mocap_ik(args.subject, args.task, args.disable_offset_removal, source = 'mvn')

    elif args.mvn_orientation:
        run_mvn.mvn_ik(args.subject, args.task, args.disable_offset_removal)
        
    elif args.mvn_opensense:
        run_mvn_opensense.mvn_ik_opensense(args.subject, args.task, args.disable_offset_removal)

    elif args.mvn_biomodel:
        run_mvn_biomodel.mvn_ik_biomodel(args.subject, args.task, args.disable_offset_removal)
    
    else:
        print('Please specify the data source for the IK analysis')


if __name__ == '__main__':
    main()










