# name: main_tuning.py
# description: filter tuning with grid search


import argparse

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt

from scripts import run_mc10, run_eval
from utils.visualization import plot_eval



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset', type = str, default = 'HAKnee')

    parser.add_argument('--filter_type', type = str, default = 'VQF') # 'VQF', 'MAH', 'MAD', 'EKF', 'RIANN'
    parser.add_argument('--dim', type = str, default = '6d') # only '6d' is supported for MC10 IK

    parser.add_argument('--do_eval', action = 'store_true') # get error for tuning parameters

    parser.add_argument('--check_eval', action = 'store_true') # inspect and save evaluation results (only after tuning & evaluation are done)


    args = parser.parse_args()


    if args.do_eval:
        print('Tuning evaluation...\n')
        run_eval.eval_main(dataset = args.dataset, subject = None, task = None, trial = None, side = None, filter_type = args.filter_type, dim = args.dim, tuning = True)

    elif args.check_eval:
        plot_eval.plot_tuning_eval(dataset = args.dataset, subject = None, task = None, trial = None, side = None, filter_type = args.filter_type, dim = args.dim, tuning = True)

    else:
        print('Tuning IK...\n')
        run_mc10.mc10_ik_main(args.dataset, subject = None, task = None, trial = None, side = None, filter_type = args.filter_type, dim = args.dim, tuning = True, filter_params = None)



if __name__ == '__main__':
    main()










