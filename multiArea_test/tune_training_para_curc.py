#!/usr/bin/env python
# Filename: hyper_para_ray 
"""
introduction: conduct hyper-parameter training on curc GPUs

run in :

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 12 March, 2021
"""

import os,sys
code_dir = os.path.expanduser('~/codes/PycharmProjects/Landuse_DL')

from datetime import datetime
# import pandas as pd
import time

sys.path.insert(0, os.path.expanduser('~/codes/PycharmProjects/DeeplabforRS'))
import slurm_utility
import basic_src.io_function as io_function

from sklearn.model_selection import ParameterGrid

# backbones = ['deeplabv3plus_xception65.ini','deeplabv3plus_xception41.ini','deeplabv3plus_xception71.ini',
#             'deeplabv3plus_resnet_v1_50_beta.ini','deeplabv3plus_resnet_v1_101_beta.ini',
#             'deeplabv3plus_mobilenetv2_coco_voc_trainval.ini','deeplabv3plus_mobilenetv3_large_cityscapes_trainfine.ini',
#             'deeplabv3plus_mobilenetv3_small_cityscapes_trainfine.ini','deeplabv3plus_EdgeTPU-DeepLab.ini']

backbones = ['deeplabv3plus_xception65.ini']

area_ini_list = ['area_Willow_River.ini', 'area_Banks_east.ini', 'area_Ellesmere_Island.ini',
                 'area_Willow_River_nirGB.ini','area_Banks_east_nirGB.ini','area_Ellesmere_Island_nirGB.ini']


# template para (contain para_files)
ini_dir=os.path.expanduser('~/Data/Arctic/canada_arctic/autoMapping/ini_files')
root_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/autoMapping/tune_training')    # run in this folder, like ray_results
jobsh_dir = os.path.expanduser('~/Data/Arctic/canada_arctic/autoMapping/job_sh_files')

from hyper_para_ray import modify_parameter
# from hyper_para_ray import get_total_F1score

def working_dir_string(trial_id, root=None):
    if root is not None:
        return os.path.join('multiArea_deeplabv3P' + str(trial_id).zfill(trial_id))
    else:
        return 'multiArea_deeplabv3P' + str(trial_id).zfill(trial_id)

def get_overall_miou(miou_path):
    # exp8/eval/miou.txt
    iou_dict = io_function.read_dict_from_txt_json(miou_path)
    return iou_dict['overall'][-1]

def copy_ini_files(ini_dir, work_dir, para_file, area_ini_list,backbone):

    ini_list = [para_file, backbone]
    ini_list.extend(area_ini_list)
    for ini in ini_list:
        io_function.copy_file_to_dst(os.path.join(ini_dir, ini ), os.path.join(work_dir,ini), overwrite=True)

def copy_curc_job_files(sh_dir, work_dir):
    sh_list = ['exe.sh','job_tf_GPU.sh','run_INsingularity_curc_GPU_tf.sh']
    for sh in sh_list:
        io_function.copy_file_to_dst(os.path.join(sh_dir, sh), os.path.join(work_dir, sh)) #, overwrite=True

def objective_overall_miou(idx, lr, iter_num,batch_size,backbone,buffer_size,training_data_per,data_augmentation,data_aug_ignore_classes):

    sys.path.insert(0, code_dir)
    import basic_src.io_function as io_function
    import parameters
    import workflow.whole_procedure as whole_procedure


    para_file = 'main_para_exp9.ini'
    work_dir = working_dir_string(idx, root=root_dir)
    if os.path.isdir(work_dir):
        io_function.mkdir(work_dir)
    os.chdir(work_dir)

    # create a training folder
    copy_ini_files(ini_dir,work_dir,para_file,area_ini_list,backbone)

    exp_name = parameters.get_string_parameters(para_file,'expr_name')

    # change para_file
    modify_parameter(os.path.join(work_dir, para_file),'network_setting_ini',backbone)
    modify_parameter(os.path.join(work_dir, backbone),'base_learning_rate',lr)
    modify_parameter(os.path.join(work_dir, backbone),'batch_size',batch_size)
    modify_parameter(os.path.join(work_dir, backbone),'iteration_num',iter_num)

    modify_parameter(os.path.join(work_dir, para_file),'buffer_size',buffer_size)
    modify_parameter(os.path.join(work_dir, para_file),'training_data_per',training_data_per)
    modify_parameter(os.path.join(work_dir, para_file),'data_augmentation',data_augmentation)
    modify_parameter(os.path.join(work_dir, para_file),'data_aug_ignore_classes',data_aug_ignore_classes)

    # run training
    # whole_procedure.run_whole_procedure(para_file, b_train_only=True)
    # copy job.sh exe.sh and other, run submit jobs
    copy_curc_job_files(jobsh_dir,work_dir)
    slurm_utility.modify_slurm_job_sh('job_tf_GPU.sh', 'job-name', 'tune%d'%idx)

    while True:
        job_count = slurm_utility.get_submit_job_count('lihu9680')
        if job_count >= 5:
            print(datetime.now(),'You have sumitted five or more jobs, wait ')
            time.sleep(60) #
            continue
        break

    # submit the job
    res = os.system( 'sbatch job_tf_GPU.sh' )
    if res != 0:
        sys.exit()

    # remove files to save storage
    os.system('rm -rf %s/exp*/init_models'%work_dir)
    os.system('rm -rf %s/exp*/eval/events.out.tfevents*'%work_dir) # don't remove miou.txt
    # os.system('rm -rf %s/exp*/train'%work_dir)
    os.system('rm -rf %s/exp*/vis'%work_dir)           # don't remove the export folder (for prediction)

    os.system('rm -rf %s/multi_inf_results'%work_dir)
    os.system('rm -rf %s/split*'%work_dir)
    os.system('rm -rf %s/sub*'%work_dir)
    os.system('rm -rf %s/tfrecord*'%work_dir)

    iou_path = os.path.join(work_dir,exp_name,'eval','miou.txt')
    overall_miou = get_overall_miou(iou_path)

    os.chdir(curr_dir_before_start)

    return overall_miou


def training_function(idx, config, checkpoint_dir=None):
    # Hyperparameters
    lr, iter_num,batch_size,backbone,buffer_size,training_data_per,data_augmentation,data_aug_ignore_classes = \
        config["lr"], config["iter_num"],config["batch_size"],config["backbone"],config['buffer_size'],\
        config['training_data_per'],config['data_augmentation'],config['data_aug_ignore_classes']

    overall_miou = objective_overall_miou(idx,lr, iter_num,batch_size,backbone,buffer_size,training_data_per,data_augmentation,data_aug_ignore_classes)

    return overall_miou

def get_para_list_from_grid_serach(para_config):

    para_combinations = list(ParameterGrid(para_config))
    # print out for checking
    # for idx,para in enumerate(para_combinations):
    #     # print(idx+1,para)
    #     print_str = "%d "%(idx+1)
    #     for key in para.keys():
    #         print_str += str(para[key]) + '\t'
    #     print(print_str)
    return para_combinations

def main():


    para_config = {
            "lr": [0.007, 0.014],   # ,0.007, 0.014, 0.028,0.056
            "iter_num": [30000, 60000], # , 60000,90000
            "batch_size": [8,16], # 16, 32, 64, 128
            "backbone": backbones,
            "buffer_size": [600],     # 300,600
            "training_data_per": [0.9],   #, 0.8
            "data_augmentation": ['scale, bright, contrast, noise'],
            'data_aug_ignore_classes':['']  # 'class_0',
    }

    para_com_list = get_para_list_from_grid_serach(para_config)
    for idx, config in enumerate(para_com_list):
        training_function(idx, config)

    # # Get a dataframe for analyzing trial results.
    # df = analysis.results_df
    #
    # output_file = 'training_miou_ray_tune_%s.xlsx'%(datetime.now().strftime("%Y%m%d_%H%M%S"))
    # with pd.ExcelWriter(output_file) as writer:
    #     df.to_excel(writer)         # , sheet_name='accuracy table'
    #     # set format
    #     # workbook = writer.book
    #     # format = workbook.add_format({'num_format': '#0.000'})
    #     # acc_talbe_sheet = writer.sheets['accuracy table']
    #     # acc_talbe_sheet.set_column('G:I',None,format)
    #     print('write trial results to %s' % output_file)



if __name__ == '__main__':
    
    curr_dir_before_start = os.getcwd()
    print('\n\ncurrent folder before ray tune: ', curr_dir_before_start, '\n\n')
    main()

