#! /bin/bash
model=ScaleDense
test_dirpath=/home/liuziyang/workspace/brain_age_prediction/data/NC/combine/18/test
excel_dirpath=/home/liuziyang/workspace/brain_age_prediction/lables/combine.xls

model_dirpath=./pretrained_model/ScaleDense/
sorter_path=./Sodeep_pretrain_weight/best_lstmla_slen_8.pth.tar

# ------ train and set the parameter
CUDA_VISIBLE_DEVICES=0 python prediction_first_stage.py \
--model             ${model}                            \
--batch_size        8                                   \
--num_workers       20                                  \
--output_dir        ${model_dirpath}                    \
--model_name        deploy_weight.pth.tar               \
--test_folder       ${test_dirpath}                     \
--excel_path        ${excel_dirpath}                    \
--npz_name          brain_age.npz                       \
--sorter            ${sorter_path}                      \


