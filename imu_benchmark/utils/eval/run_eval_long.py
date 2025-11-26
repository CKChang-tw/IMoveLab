# name: run_eval_long.py
# description: evaluate kinematics compared to the mocap-based reference
# author: Vu Phan
# date: 2024/09/23


import numpy as np
import pandas as pd
import copy

from imu_benchmark.constants import constant_common, constant_mocap, constant_mt
from imu_benchmark.utils import common
from imu_benchmark.utils.mocap import ik_mocap
from imu_benchmark.utils.eval import eval_utils, eval_segment
from imu_benchmark.utils.eval import metrics


def evaluate(f_type, dim, subject, reference, mocap_alignment, enable_opensense = False):
    ''' tbd '''
    print('*** Filter ' + f_type)
    print('*** Sensor axes ' + dim.upper())

    task = 'long_walk'

    subject_list = common.get_subject_list_long(subject)

    for subject in subject_list:
        print('*** Subject ' + str(subject))

        mt_fn = constant_common.OUT_MT_JA_PATH + 'ik_s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '1.pkl'
        ja_mt = eval_utils.load_data(mt_fn)

        if enable_opensense:
            os_fn = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '1.pkl'
            ja_os = eval_utils.load_data(os_fn)

            rename_keys = {'ankle_angle_r': 'ankle_flexion_r', 'ankle_angle_l': 'ankle_flexion_l'}
            for old_key, new_key in rename_keys.items():
                ja_os[new_key] = ja_os.pop(old_key)

            # XXX: hardcoded as these are not available in OpenSense outputs
            ja_os['knee_adduction_r'] = np.zeros(ja_os['knee_flexion_r'].shape)
            ja_os['knee_adduction_l'] = np.zeros(ja_os['knee_flexion_l'].shape)
            ja_os['knee_rotation_r'] = np.zeros(ja_os['knee_flexion_r'].shape)
            ja_os['knee_rotation_l'] = np.zeros(ja_os['knee_flexion_l'].shape)
            ja_os['ankle_adduction_r'] = np.zeros(ja_os['ankle_flexion_r'].shape)
            ja_os['ankle_adduction_l'] = np.zeros(ja_os['ankle_flexion_l'].shape)
            ja_os['ankle_rotation_r'] = np.zeros(ja_os['ankle_flexion_r'].shape)
            ja_os['ankle_rotation_l'] = np.zeros(ja_os['ankle_flexion_l'].shape)

        mocap_t1_fn = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + subject + '_' + task + '1.pkl'
        mocap_t2_fn = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + subject + '_' + task + '2.pkl'
        mocap_t3_fn = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + subject + '_' + task + '3.pkl'
        
        ja_mc_trial       = {}
        ja_mc_trial['t1'] = eval_utils.load_data(mocap_t1_fn)
        ja_mc_trial['t2'] = eval_utils.load_data(mocap_t2_fn)
        ja_mc_trial['t3'] = eval_utils.load_data(mocap_t3_fn)


        if mocap_alignment:
            title_alignment = '_alignment'

            if subject in list(constant_common.ISOLATED_CASES.keys()):
                if task in constant_common.ISOLATED_CASES[subject].keys():
                    alignment_id = [constant_common.ISOLATED_CASES[subject][task][0], constant_common.ISOLATED_CASES[subject][task][1]]
                else:
                    alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]

            else:
                alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]
            
            ja_mt = eval_utils.get_ja_alignment(ja_mt, ja_mc_trial['t1'], alignment_id, task)

            if enable_opensense:
                ja_os = eval_utils.get_ja_alignment(ja_os, ja_mc_trial['t1'], alignment_id, task)
        
        else:
            title_alignment = ''

        ja_mt_trial       = {}
        ja_mt_trial['t1'] = eval_utils.get_long_trial_chunk(ja_mt, subject, 1)
        ja_mt_trial['t2'] = eval_utils.get_long_trial_chunk(ja_mt, subject, 2)
        ja_mt_trial['t3'] = eval_utils.get_long_trial_chunk(ja_mt, subject, 3)

        if enable_opensense:
            ja_os_trial       = {}
            ja_os_trial['t1'] = eval_utils.get_long_trial_chunk(ja_os, subject, 1)
            ja_os_trial['t2'] = eval_utils.get_long_trial_chunk(ja_os, subject, 2)
            ja_os_trial['t3'] = eval_utils.get_long_trial_chunk(ja_os, subject, 3)

        for trial in ['t1', 't2', 't3']:
            # print('- Trial ' + str(trial))

            lag = eval_utils.find_lag(ja_mt_trial[trial]['knee_flexion_r'], ja_mc_trial[trial]['knee_flexion_r'])
        
            if enable_opensense:
                ja_mc_trial[trial], ja_mt_trial[trial], ja_os_trial[trial] = eval_utils.do_resync(ja_mc_trial[trial], ja_mt_trial[trial], ja_os_trial[trial], lag)
                ja_mc_trial[trial], ja_mt_trial[trial], ja_os_trial[trial] = eval_utils.remove_bad_mocap(ja_mc_trial[trial], ja_mt_trial[trial], ja_os_trial[trial], subject, trial) # --> disable this when outputing motion files
            else:
                ja_mc_trial[trial], ja_mt_trial[trial], _ = eval_utils.do_resync(ja_mc_trial[trial], ja_mt_trial[trial], copy.deepcopy(ja_mt_trial[trial]), lag)
                ja_mc_trial[trial], ja_mt_trial[trial], _ = eval_utils.remove_bad_mocap(ja_mc_trial[trial], ja_mt_trial[trial], copy.deepcopy(ja_mt_trial[trial]), subject, trial) # --> disable this when outputing motion files


        # # TODO: need to work more on removing bad mocap data from subject 5 (trial 1)
        # import matplotlib.pyplot as plt
        # fig, ax = plt.subplots(3, 3, sharex = True, sharey = True)
        # ax[0, 0].plot(ja_mc_trial['t1']['hip_flexion_r'], color = 'k')
        # ax[1, 0].plot(ja_mc_trial['t1']['hip_adduction_r'], color = 'k')
        # ax[2, 0].plot(ja_mc_trial['t1']['hip_rotation_r'], color = 'k')
        # ax[0, 1].plot(ja_mc_trial['t1']['knee_flexion_r'], color = 'k')
        # ax[1, 1].plot(ja_mc_trial['t1']['knee_adduction_r'], color = 'k')
        # ax[2, 1].plot(ja_mc_trial['t1']['knee_rotation_r'], color = 'k')
        # ax[0, 2].plot(ja_mc_trial['t1']['ankle_flexion_r'], color = 'k')
        # ax[1, 2].plot(ja_mc_trial['t1']['ankle_adduction_r'], color = 'k')
        # ax[2, 2].plot(ja_mc_trial['t1']['ankle_rotation_r'], color = 'k')

        # ax[0, 0].plot(ja_mt['hip_flexion_r'], color = 'r')
        # ax[1, 0].plot(ja_mt['hip_adduction_r'], color = 'r')
        # ax[2, 0].plot(ja_mt['hip_rotation_r'], color = 'r')
        # ax[0, 1].plot(ja_mt['knee_flexion_r'], color = 'r')
        # ax[1, 1].plot(ja_mt['knee_adduction_r'], color = 'r')
        # ax[2, 1].plot(ja_mt['knee_rotation_r'], color = 'r')
        # ax[0, 2].plot(ja_mt['ankle_flexion_r'], color = 'r')
        # ax[1, 2].plot(ja_mt['ankle_adduction_r'], color = 'r')
        # ax[2, 2].plot(ja_mt['ankle_rotation_r'], color = 'r')

        # plt.show()
            




        # 1. Get RMSDs of three trials
        for trial in ['t1', 't2', 't3']:
            event = eval_segment.get_events(subject, task + str(trial[-1]), lag, fs = constant_mocap.MOCAP_SAMPLING_RATE, source = 'mt_long')
            for side in event.keys():
                id = np.where(event[side] < constant_mt.LONG_TRIAL_ID[subject][trial]['sitting_start'])[0]
                event[side] = event[side][id]

            segment_mc = eval_segment.get_segment(ja_mc_trial[trial], event, task + str(trial[-1]), fs = constant_mocap.MOCAP_SAMPLING_RATE)
            segment_mt = eval_segment.get_segment(ja_mt_trial[trial], event, task + str(trial[-1]), fs = constant_mocap.MOCAP_SAMPLING_RATE)
            if enable_opensense:
                segment_os = eval_segment.get_segment(ja_os_trial[trial], event, task + str(trial[-1]), fs = constant_mocap.MOCAP_SAMPLING_RATE)

            rmsd_mt = eval_utils.calculate_rmse(segment_mc, segment_mt)
            print(rmsd_mt)
            if enable_opensense:
                rmsd_os = eval_utils.calculate_rmse(segment_mc, segment_os)
                print(rmsd_os)

            filename = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial[-1]) + '_mt.pkl'
            print(filename)
            eval_utils.save_data(rmsd_mt, filename)
            if enable_opensense:
                print('OpenSense enabled')
                filename_os = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial[-1]) + '_os.pkl'
                print(filename_os)
                eval_utils.save_data(rmsd_os, filename_os)

            print('DONE')


        # # 2. Get the cumulative RMSDs (to show drifting)
        # for trial in ['t1', 't2', 't3']:
        #     print('- Trial ' + str(trial))
        #     event = eval_segment.get_events(subject, task + str(trial[-1]), lag, fs = constant_mocap.MOCAP_SAMPLING_RATE, source = 'mt_long')
        #     for side in event.keys():
        #         id = np.where(event[side] < constant_mt.LONG_TRIAL_ID[subject][trial]['sitting_start'])[0]
        #         event[side] = event[side][id]

        #     rmsd_mt = {}
        #     if enable_opensense:
        #         rmsd_os = {}
        #     for joint in ja_mt_trial[trial].keys():
        #         rmsd_mt[joint] = []
        #         if enable_opensense:
        #             rmsd_os[joint] = []

        #         if '_r' in joint:
        #             start_id = event['r'][0]
        #             end_id   = event['r'][-1]
        #         else:
        #             start_id = event['l'][0]
        #             end_id   = event['l'][-1]
                
        #         chunk = 1*start_id
        #         while (chunk < end_id) and (chunk < 60000):
        #             if chunk + 6000 < end_id:
        #                 rmsd_mt[joint].append(metrics.get_rmse(ja_mc_trial[trial][joint][chunk:chunk + 6000], ja_mt_trial[trial][joint][chunk:chunk + 6000]))
        #                 if enable_opensense:
        #                     rmsd_os[joint].append(metrics.get_rmse(ja_mc_trial[trial][joint][chunk:chunk + 6000], ja_os_trial[trial][joint][chunk:chunk + 6000]))
        #             else:
        #                 if end_id > 60000:
        #                     rmsd_mt[joint].append(metrics.get_rmse(ja_mc_trial[trial][joint][chunk:60000], ja_mt_trial[trial][joint][chunk:60000]))
        #                     if enable_opensense:
        #                         rmsd_os[joint].append(metrics.get_rmse(ja_mc_trial[trial][joint][chunk:60000], ja_os_trial[trial][joint][chunk:60000]))
        #                 else:
        #                     rmsd_mt[joint].append(metrics.get_rmse(ja_mc_trial[trial][joint][chunk:end_id], ja_mt_trial[trial][joint][chunk:end_id]))
        #                     if enable_opensense:
        #                         rmsd_os[joint].append(metrics.get_rmse(ja_mc_trial[trial][joint][chunk:end_id], ja_os_trial[trial][joint][chunk:end_id]))

        #             chunk += 6000

        #     print(rmsd_mt)
        #     filename = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial[-1]) + '_mt_chunk.pkl'
        #     # print(filename)
        #     eval_utils.save_data(rmsd_mt, filename)
        #     if enable_opensense:
        #         print('OpenSense enabled for chunk')
        #         filename_os = 'imu_benchmark/outputs/rmse_longwalk/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial[-1]) + '_os_chunk.pkl'
        #         # print(filename_os)
        #         eval_utils.save_data(rmsd_os, filename_os)
        #     print('DONE')
            
        
        # # 3. Get IK for OpenSense
        # for trial in ['t1', 't2', 't3']:
        #     print('- Trial ' + str(trial))

        #     time_id = np.arange(0, len(ja_mt_trial[trial]['knee_flexion_r']), 1)/constant_mocap.MOCAP_SAMPLING_RATE
        #     # time_id = np.arange(0, len(ja_mc_trial[trial]['knee_flexion_r']), 1)/constant_mocap.MOCAP_SAMPLING_RATE

        #     output = pd.DataFrame()
        #     output['time'] = time_id
            
        #     output['hip_adduction_r'] = 0.1*ja_mt_trial[trial]['hip_adduction_r']
        #     output['hip_rotation_r']  = ja_mt_trial[trial]['hip_rotation_r']
        #     output['hip_flexion_r']   = ja_mt_trial[trial]['hip_flexion_r']
        #     output['knee_angle_r']    = ja_mt_trial[trial]['knee_flexion_r']
        #     output['ankle_angle_r']   = ja_mt_trial[trial]['ankle_flexion_r']

        #     output['hip_adduction_l'] = 0.1*ja_mt_trial[trial]['hip_adduction_l']
        #     output['hip_rotation_l']  = ja_mt_trial[trial]['hip_rotation_l']
        #     output['hip_flexion_l']   = ja_mt_trial[trial]['hip_flexion_l']
        #     output['knee_angle_l']    = ja_mt_trial[trial]['knee_flexion_l']
        #     output['ankle_angle_l']   = ja_mt_trial[trial]['ankle_flexion_l']

        #     # output['hip_adduction_r'] = 0.1*ja_mc_trial[trial]['hip_adduction_r']
        #     # output['hip_rotation_r']  = ja_mc_trial[trial]['hip_rotation_r']
        #     # output['hip_flexion_r']   = ja_mc_trial[trial]['hip_flexion_r']
        #     # output['knee_angle_r']    = ja_mc_trial[trial]['knee_flexion_r']
        #     # output['ankle_angle_r']   = ja_mc_trial[trial]['ankle_flexion_r']

        #     # output['hip_adduction_l'] = 0.1*ja_mc_trial[trial]['hip_adduction_l']
        #     # output['hip_rotation_l']  = ja_mc_trial[trial]['hip_rotation_l']
        #     # output['hip_flexion_l']   = ja_mc_trial[trial]['hip_flexion_l']
        #     # output['knee_angle_l']    = ja_mc_trial[trial]['knee_flexion_l']
        #     # output['ankle_angle_l']   = ja_mc_trial[trial]['ankle_flexion_l']

        #     out_fn = 'imu_benchmark/outputs/rmse_longwalk_ik/s' + subject + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + str(trial[-1]) + '_mt_ik.mot'
        #     # out_fn = 'imu_benchmark/outputs/rmse_longwalk_ik/s' + subject + '_' + task + str(trial[-1]) + '_mc_ik.mot'
        #     prefix = 'inDegrees=yes\n'
        #     prefix += 'name=ik_imu_orientation\n'
        #     prefix += 'DataType=double\n'
        #     prefix += 'version=3\n'
        #     prefix += 'OpenSimVersion=4.5-2023-11-26-efcdfd3eb\n'
        #     prefix += 'endheader\n'

        #     output.to_csv(out_fn, sep = '\t', index = False)
        #     with open(out_fn, 'r') as original: data = original.read()
        #     with open(out_fn, 'w') as modified: modified.write(prefix + data)

        # print('DONE')















        

        # for trial in range(0, 3):
        #     print('*** Task ' + task)

        #     if reference == 'direct':
        #         filename_mc = constant_common.OUT_MOCAP_JA_PATH + 'ik_s' + str(subject) + '_' + task + '.pkl'
        #         ja_mc = eval_utils.load_data(filename_mc)
        #     else:
        #         filename_mc = constant_common.IN_LAB_PATH + 's' + str(subject) + '/' + constant_common.MOCAP_OPENSIM_PATH  + constant_common.LAB_TASK_NAME_MAP[task] + '/ik.mot'
        #         ja_mc = ik_mocap.get_all_ja_os(filename_mc, constant_mt.MT_SAMPLING_RATE)
                
        #         sync_fn   = constant_common.OUT_SYNC_INFO + 'sync_info_s' + str(subject) + '_' + task + '.pkl'
        #         sync_info = eval_utils.load_data(sync_fn)

        #         if sync_info['first_start'] == 'mocap':
        #             shifting_id = sync_info['shifting_id']
        #             ja_mc = eval_utils.resync_data(ja_mc, shifting_id)

        #     if selected_setup == 'mm':
        #         filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '.pkl'
        #         if enable_opensense:
        #             filename_os = constant_common.OUT_OPENSENSE_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '.pkl'
        #     else:
        #         filename_mt = constant_common.OUT_MT_JA_PATH + 'ik_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + '.pkl'

        #     ja_mt = eval_utils.load_data(filename_mt)
        #     if enable_opensense:
        #         ja_os = eval_utils.load_data(filename_os)

        #         rename_keys = {'ankle_angle_r': 'ankle_flexion_r', 'ankle_angle_l': 'ankle_flexion_l'}
        #         for old_key, new_key in rename_keys.items():
        #             ja_os[new_key] = ja_os.pop(old_key)

        #         # XXX: hardcoded as these are not available in OpenSense outputs
        #         ja_os['knee_adduction_r'] = np.zeros(ja_os['knee_flexion_r'].shape)
        #         ja_os['knee_adduction_l'] = np.zeros(ja_os['knee_flexion_l'].shape)
        #         ja_os['knee_rotation_r'] = np.zeros(ja_os['knee_flexion_r'].shape)
        #         ja_os['knee_rotation_l'] = np.zeros(ja_os['knee_flexion_l'].shape)
        #         ja_os['ankle_adduction_r'] = np.zeros(ja_os['ankle_flexion_r'].shape)
        #         ja_os['ankle_adduction_l'] = np.zeros(ja_os['ankle_flexion_l'].shape)
        #         ja_os['ankle_rotation_r'] = np.zeros(ja_os['ankle_flexion_r'].shape)
        #         ja_os['ankle_rotation_l'] = np.zeros(ja_os['ankle_flexion_l'].shape)


        #     print('- Resync the data if lagged')
        #     lag                 = eval_utils.find_lag(ja_mt['knee_flexion_r'], ja_mc['knee_flexion_r'])
        #     if enable_opensense:
        #         ja_mc, ja_mt, ja_os = eval_utils.do_resync(ja_mc, ja_mt, ja_os, lag)
        #     else:
        #         ja_mc, ja_mt, _ = eval_utils.do_resync(ja_mc, ja_mt, copy.deepcopy(ja_mt), lag)

            
        #     if mocap_alignment:
        #         title_alignment = '_alignment'

        #         if subject in list(constant_common.ISOLATED_CASES.keys()):
        #             if task in constant_common.ISOLATED_CASES[subject].keys():
        #                 alignment_id = [constant_common.ISOLATED_CASES[subject][task][0], constant_common.ISOLATED_CASES[subject][task][1]]
        #             else:
        #                 alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]

        #         else:
        #             alignment_id = [constant_common.ALIGNMENT_PERIOD[0], constant_common.ALIGNMENT_PERIOD[1]]
                
        #         ja_mt = eval_utils.get_ja_alignment(ja_mt, ja_mc, alignment_id, task)

        #         # import matplotlib.pyplot as plt
        #         # fig, ax = plt.subplots(3, 3, sharex = True, sharey = True)
        #         # ax[0, 0].plot(ja_mc['hip_flexion_r'], color = 'k')
        #         # ax[1, 0].plot(ja_mc['hip_adduction_r'], color = 'k')
        #         # ax[2, 0].plot(ja_mc['hip_rotation_r'], color = 'k')
        #         # ax[0, 1].plot(ja_mc['knee_flexion_r'], color = 'k')
        #         # ax[1, 1].plot(ja_mc['knee_adduction_r'], color = 'k')
        #         # ax[2, 1].plot(ja_mc['knee_rotation_r'], color = 'k')
        #         # ax[0, 2].plot(ja_mc['ankle_flexion_r'], color = 'k')
        #         # ax[1, 2].plot(ja_mc['ankle_adduction_r'], color = 'k')
        #         # ax[2, 2].plot(ja_mc['ankle_rotation_r'], color = 'k')

        #         # ax[0, 0].plot(ja_mt['hip_flexion_r'], color = 'r')
        #         # ax[1, 0].plot(ja_mt['hip_adduction_r'], color = 'r')
        #         # ax[2, 0].plot(ja_mt['hip_rotation_r'], color = 'r')
        #         # ax[0, 1].plot(ja_mt['knee_flexion_r'], color = 'r')
        #         # ax[1, 1].plot(ja_mt['knee_adduction_r'], color = 'r')
        #         # ax[2, 1].plot(ja_mt['knee_rotation_r'], color = 'r')
        #         # ax[0, 2].plot(ja_mt['ankle_flexion_r'], color = 'r')
        #         # ax[1, 2].plot(ja_mt['ankle_adduction_r'], color = 'r')
        #         # ax[2, 2].plot(ja_mt['ankle_rotation_r'], color = 'r')

        #         # plt.show()

        #         if enable_opensense:
        #             ja_os = eval_utils.get_ja_alignment(ja_os, ja_mc, alignment_id, task)
            
        #     else:
        #         title_alignment = ''


        #     print('- Segment the data into gait cycles or exercise reps')
        #     event = eval_segment.get_events(subject, task, lag)
            
        #     segment_mc = eval_segment.get_segment(ja_mc, event, task)
        #     segment_mt = eval_segment.get_segment(ja_mt, event, task)
        #     if enable_opensense:
        #         segment_os = eval_segment.get_segment(ja_os, event, task)


        #     print('- Evaluate the RMSE')
        #     rmse_mt = eval_utils.calculate_rmse(segment_mc, segment_mt)
        #     print(rmse_mt)
        #     if enable_opensense:
        #         rmse_os = eval_utils.calculate_rmse(segment_mc, segment_os)
            
        #     print('- Save the evaluation results')
        #     common.mkfolder(constant_common.OUT_RMSE_PATH)
        #     if selected_setup == 'mm':
        #         filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + reference + title_alignment + '_mt' + '.pkl'
        #         if enable_opensense:
        #             filename_os = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + reference + title_alignment + '_os' + '.pkl'
        #     else:
        #         filename_mt = constant_common.OUT_RMSE_PATH + 'eval_s' + str(subject) + '_' + f_type.lower() + '_' + dim.upper() + '_' + task + '_' + selected_setup + '_' + reference + title_alignment + '_mt' + '.pkl'
                
        #     eval_utils.save_data(rmse_mt, filename_mt)
        #     if enable_opensense:
        #         print('\n\n\n')
        #         eval_utils.save_data(rmse_os, filename_os)












