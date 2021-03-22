#! /bin/bash
model=ScaleDense
test_dirpath=/home/workspace/brain_age_prediction/data/NC/combine/test
excel_dirpath=/home/workspace/brain_age_prediction/lables/combine.xls
sorter_path=./Sodeep_pretrain_weight/best_lstmla_slen_8.pth.tar
model_dirpath=./model/seconde_stage/
first_stage_net=./pretrained_model//ScaleDense_best_model.pth.tar

# ------ train and set the parameter
CUDA_VISIBLE_DEVICES=0 python prediction_second_stage.py \
--model             ${model}                             \
--batch_size        8                                   \
--num_workers       20                                   \
--output_dir        ${model_dirpath}                     \
--model_name        ${model}_best_model.pth.tar          \
--test_folder       ${test_dirpath}                      \
--excel_path        ${excel_dirpath}                     \
--npz_name          brain_age.npz                        \
--dis_range         5                                    \
--first_stage_net   ${first_stage_net}                   \
--sorter            ${sorter_path}                       \





