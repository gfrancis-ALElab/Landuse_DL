#!/usr/bin/env python
# Filename: collect_training_results 
"""
introduction: collect parameters and traning results (miou)

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 13 March, 2021
"""

import os, sys
from optparse import OptionParser

code_dir = os.path.expanduser('~/codes/PycharmProjects/Landuse_DL')
sys.path.insert(0, code_dir)

import basic_src.io_function as io_function
import parameters

import pandas as pd

# para_list = ['lr', 'iter_num', 'batch_size', 'backbone',
#              'buffer_size', 'training_data_per', 'data_augmentation','data_aug_ignore_classes']

para_ini_list = ['base_learning_rate', 'iteration_num', 'batch_size', 'network_setting_ini',
             'buffer_size', 'training_data_per', 'data_augmentation', 'data_aug_ignore_classes']


def get_miou_of_overall_and_class_1_step(work_dir,para_file,train_output):

    exp_name = parameters.get_string_parameters(os.path.join(work_dir,para_file), 'expr_name')
    miou_path = os.path.join(work_dir,exp_name,'eval','miou.txt')
    if os.path.isfile(miou_path) is False:
        print("warning, no miou.txt in %s"%work_dir)
        train_output['class_1'].append(0)
        train_output['overall'].append(0)
        train_output['step'].append(0)
        return False

    iou_dict = io_function.read_dict_from_txt_json(miou_path)
    train_output['class_1'].append(iou_dict['class_1'][-1])
    train_output['overall'].append(iou_dict['overall'][-1])
    train_output['step'].append(iou_dict['step'][-1])

    return True

def read_para_values(work_dir,para_file,train_output):

    para_path = os.path.join(work_dir,para_file)

    backbone = parameters.get_string_parameters(para_path,'network_setting_ini')
    train_output['network_setting_ini'].append(backbone)

    net_ini_path = os.path.join(work_dir,backbone)
    lr = parameters.get_digit_parameters(net_ini_path,'base_learning_rate','float')
    train_output['base_learning_rate'].append(lr)

    iter_num = parameters.get_digit_parameters(net_ini_path,'iteration_num','int')
    train_output['iteration_num'].append(iter_num)

    batch_size = parameters.get_digit_parameters(net_ini_path,'batch_size','int')
    train_output['batch_size'].append(batch_size)



    buffer_size = parameters.get_digit_parameters(para_path,'buffer_size','int')
    train_output['buffer_size'].append(buffer_size)

    training_data_per = parameters.get_digit_parameters(para_path,'training_data_per','float')
    train_output['training_data_per'].append(training_data_per)

    data_augmentation = parameters.get_string_parameters(para_path,'data_augmentation')
    train_output['data_augmentation'].append(data_augmentation)

    data_aug_ignore_classes = parameters.get_string_parameters(para_path,'data_aug_ignore_classes')
    train_output['data_aug_ignore_classes'].append(data_aug_ignore_classes)

    return True

def main(options, args):
    root_dir = args[0]
    if os.path.isdir(root_dir) is False:
        raise ValueError('%s not exists'%root_dir)

    folder_pattern = options.folder_pattern
    folder_list = io_function.get_file_list_by_pattern(root_dir,folder_pattern)
    folder_list = [item for item in folder_list if os.path.isdir(item) ]
    folder_list.sort()

    para_file = options.para_file
    output_file = options.output
    if output_file is None:
        output_file = os.path.basename(root_dir) + '.xlsx'

    train_output = {}
    train_output['folder'] = []
    for para in para_ini_list:
        train_output[para] = []

    train_output['class_1'] = []
    train_output['overall'] = []
    train_output['step'] = []

    for folder in folder_list:
        print('read parameter and results for %s'%folder)
        train_output['folder'].append(os.path.basename(folder))
        read_para_values(folder,para_file,train_output)
        get_miou_of_overall_and_class_1_step(folder, para_file, train_output)

    # save to excel file
    train_out_table_pd = pd.DataFrame(train_output)
    with pd.ExcelWriter(output_file) as writer:
        train_out_table_pd.to_excel(writer, sheet_name='training parameter and results')
        # set format
        # workbook = writer.book
        # format = workbook.add_format({'num_format': '#0.000'})
        # train_out_table_sheet = writer.sheets['training parameter and results']
        # train_out_table_sheet.set_column('G:I',None,format)



    pass

if __name__ == '__main__':
    usage = "usage: %prog [options] training_folder "
    parser = OptionParser(usage=usage, version="1.0 2021-03-13")
    parser.description = 'Introduction: collect parameters and training results (miou) '

    parser.add_option("-p", "--para_file",
                      action="store", dest="para_file",default='main_para.ini',
                      help="the parameters file")

    parser.add_option("-o", "--output",
                      action="store", dest="output", #default="accuracy_table.xlsx",
                      help="the output file path")

    parser.add_option("-f", "--folder_pattern",
                      action="store", dest="folder_pattern",default='multiArea_deeplabv3P_?????',
                      help="the pattern of training folder")

    (options, args) = parser.parse_args()
    if len(sys.argv) < 2 or len(args) < 1:
        parser.print_help()
        sys.exit(2)
    main(options, args)