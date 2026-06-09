# name: main_tuning.py
# description: run parameter tuning for filters (using data from 2 participants) with grid search


import argparse

import os, sys
sys.path.append(os.path.abspath('mocap_ref/'))

from scripts import run_mt, run_mocap
from utils.eval import run_eval
from utils.visualization import plot_eval


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--selected_setup', type = str, default = 'mm') # sensor placement, i.e., 'mm' (for main analysis), 'hh', 'll', or 'ff'

    parser.add_argument('--filter_type', type = str, default = 'VQF') # 'VQF', 'MAH', 'MAD', 'EKF', 'RIANN'
    parser.add_argument('--dim', type = str, default = '6d') # only '6d' is supported for MC10 IK

    parser.add_argument('--do_mocap', action = 'store_true') # run mocap IK for tuning)

    parser.add_argument('--do_eval', action = 'store_true') # whether to run OpenSense IK

    parser.add_argument('--check_eval', action = 'store_true') # inspect and save evaluation results (only after tuning & evaluation are done)


    args = parser.parse_args()


    if args.do_mocap:
        print('Obtain mocap IK for tuning evaluation...\n')
        run_mocap.mocap_ik(subject = None, task = None, source = 'mt', tuning = True)

    elif args.do_eval:
        print('Evaluate tuning parameters...\n')
        run_eval.evaluate(f_type = args.filter_type, dim = args.dim, subject = None, task = None, reference = 'direct', mocap_alignment = True, selected_setup = args.selected_setup, enable_opensense = False, tuning = True)

    elif args.check_eval:
        print('Inspect tunning evaluation results & save optimal parameters...\n')
        plot_eval.plot_tuning_eval(f_type = args.filter_type, dim = args.dim, subject = None, task = None)

    else:
        run_mt.mt_ik(selected_setup = args.selected_setup, f_type = args.filter_type, dim = args.dim, subject = None, task = None, source = 'mt', tuning = True, filter_params = None)


if __name__ == '__main__':
    main()















