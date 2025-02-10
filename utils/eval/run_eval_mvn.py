# name: run_eval_mvn.py
# description: evaluate kinematics compared to the mocap-based reference (for the sub-experiment with the MVN data)
# author: Vu Phan
# date: 2025/01/22


import numpy as np

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt, constant_mvn
from imu_benchmark.utils import common
from imu_benchmark.utils.mocap import ik_mocap
from imu_benchmark.utils.eval import eval_utils, eval_segment


def evaluate(subject, task, reference, remove_offset, selected_setup, do_biomodel):
    ''' tbd '''
    subject_list = common.get_subject_list(subject)
    task_list    = common.get_task_list_mvn(task)

    f_type = 'Xsens'
    dim    = '9D'

    for subject in subject_list:
        print('*** Subject ' + str(subject))
        print('*** Sensor axes ' + dim.upper())

        for task in task_list:
            print('*** Task ' + task)

            if remove_offset:
                title_offset = '_roffset'
            else:
                title_offset = ''

            if reference == 'direct':
                filename_mc = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + str(subject) + '_' + task + title_offset + '.pkl'
                ja_mc = eval_utils.load_data(filename_mc)
            else:
                filename_mc = constant_common.IN_LAB_PATH + 's' + str(subject) + '/' + constant_common.MOCAP_OPENSIM_PATH  + constant_common.LAB_TASK_NAME_MAP[task] + '/ik.mot'
                ja_mc = ik_mocap.get_all_ja_os(filename_mc, constant_mvn.MVN_SAMPLING_RATE)
                
                sync_fn   = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + task + '.pkl'
                sync_info = eval_utils.load_data(sync_fn)

                if sync_info['first_start'] == 'mocap':
                    shifting_id = sync_info['shifting_id']
                    ja_mc = eval_utils.resync_data(ja_mc, shifting_id)

            if selected_setup == 'mm':
                filename_mvn = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
                if do_biomodel:
                    filename_os           = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
                    filename_mvn_biomodel = constant_common.OUT_MVN_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '.pkl'
            else:
                filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + title_offset + '.pkl'

            ja_mvn = eval_utils.load_data(filename_mvn)
            if do_biomodel:
                ja_mvn_opensense = eval_utils.load_data(filename_os)
                ja_mvn_biomodel  = eval_utils.load_data(filename_mvn_biomodel)

            print('- Resync the data if lagged')
            lag = eval_utils.find_lag(ja_mvn['knee_flexion_r'], ja_mc['knee_flexion_r'])
            if do_biomodel:
                ja_mc, ja_mvn, ja_mvn_opensense, ja_mvn_biomodel = eval_utils.do_resync_mvn(ja_mc, ja_mvn, ja_mvn_opensense, ja_mvn_biomodel, lag)
            else:
                ja_mc, ja_mvn, _ = eval_utils.do_resync(ja_mc, ja_mvn, ja_mvn, lag)

            # Remove offset at the static standing at the beginning
            for key in ja_mc.keys():
                ja_mc[key] -= np.mean(ja_mc[key][0:100])
                ja_mvn[key] -= np.mean(ja_mvn[key][0:100])
                if do_biomodel:
                    ja_mvn_opensense[key] -= np.mean(ja_mvn_opensense[key][0:100])
                    ja_mvn_biomodel[key]  -= np.mean(ja_mvn_biomodel[key][0:100])

            print('- Segment the data into gait cycles or exercise reps')
            event = eval_segment.get_events(subject, task, lag, fs = constant_mvn.MVN_SAMPLING_RATE)
            
            segment_mc  = eval_segment.get_segment(ja_mc, event, task, fs = constant_mvn.MVN_SAMPLING_RATE)
            segment_mvn = eval_segment.get_segment(ja_mvn, event, task, fs = constant_mvn.MVN_SAMPLING_RATE)
            if do_biomodel:
                segment_mvn_opensense = eval_segment.get_segment(ja_mvn_opensense, event, task, fs = constant_mvn.MVN_SAMPLING_RATE)
                segment_mvn_biomodel  = eval_segment.get_segment(ja_mvn_biomodel, event, task, fs = constant_mvn.MVN_SAMPLING_RATE)

            print('- Evaluate the RMSE')
            rmse_mvn = eval_utils.calculate_rmse(segment_mc, segment_mvn)
            if do_biomodel:
                rmse_mvn_opensense = eval_utils.calculate_rmse(segment_mc, segment_mvn_opensense)
                rmse_mvn_biomodel  = eval_utils.calculate_rmse(segment_mc, segment_mvn_biomodel)
            
            print('- Save the evaluation results')
            common.mkfolder(constant_common.OUT_RMSE_PATH)
            filename_mvn = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '_' + reference + '_mvn' + '.pkl'
            if do_biomodel:
                filename_mvn_opensense = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '_' + reference + '_mvn_opensense' + '.pkl'
                filename_mvn_biomodel  = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + title_offset + '_' + reference + '_mvn_biomodel' + '.pkl'
          
            eval_utils.save_data(rmse_mvn, filename_mvn)
            if do_biomodel:
                print('\n\n\n')
                eval_utils.save_data(rmse_mvn_opensense, filename_mvn_opensense)
                eval_utils.save_data(rmse_mvn_biomodel, filename_mvn_biomodel)


            # import matplotlib.pyplot as plt
            # joint = 'hip_adduction_l'
            # print('RMSE (unconstrained)' + joint + ' ' + str(np.round(rmse_mvn[joint], 2)))
            # print('RMSE (OpenSense)' + joint + ' ' + str(np.round(rmse_mvn_opensense[joint], 2)))
            # print('RMSE (MVN)' + joint + ' ' + str(np.round(rmse_mvn_biomodel[joint], 2)))

            # fig, ax = plt.subplots(1, 1, figsize = (10, 5))

            # ax.plot(np.mean(segment_mc[joint], axis = 0), color = 'black', linestyle = '--', label = 'Reference')
            # ax.fill_between(np.arange(segment_mc[joint].shape[1]), np.mean(segment_mc[joint], axis = 0) - np.std(segment_mc[joint], axis = 0), np.mean(segment_mc[joint], axis = 0) + np.std(segment_mc[joint], axis = 0), color = 'black', alpha = 0.2)
            # ax.plot(np.mean(segment_mvn[joint], axis = 0), color = '#89A6FB', label = 'Unconstrained')
            # ax.fill_between(np.arange(segment_mvn[joint].shape[1]), np.mean(segment_mvn[joint], axis = 0) - np.std(segment_mvn[joint], axis = 0), np.mean(segment_mvn[joint], axis = 0) + np.std(segment_mvn[joint], axis = 0), color = '#89A6FB', alpha = 0.2)
 
            # ax.plot(np.mean(segment_mvn_opensense[joint], axis = 0), color = '#98CE00', label = 'OpenSense')
            # ax.fill_between(np.arange(segment_mvn_opensense[joint].shape[1]), np.mean(segment_mvn_opensense[joint], axis = 0) - np.std(segment_mvn_opensense[joint], axis = 0), np.mean(segment_mvn_opensense[joint], axis = 0) + np.std(segment_mvn_opensense[joint], axis = 0), color = '#98CE00', alpha = 0.2)

            # ax.plot(np.mean(segment_mvn_biomodel[joint], axis = 0), color = '#FF8000', label = 'MVN')
            # ax.fill_between(np.arange(segment_mvn_biomodel[joint].shape[1]), np.mean(segment_mvn_biomodel[joint], axis = 0) - np.std(segment_mvn_biomodel[joint], axis = 0), np.mean(segment_mvn_biomodel[joint], axis = 0) + np.std(segment_mvn_biomodel[joint], axis = 0), color = '#FF8000', alpha = 0.2)

            # ax.legend()

            # plt.show()

            # breakpoint()





