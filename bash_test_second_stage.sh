#! /bin/bash
model=ScaleDense
test_dirpath=/data/NC/
excel_dirpath=/data/brain_age.xls
model_dirpath=./model/TSNA/
first_stage_net=./model/combine/

# ------ train and set the parameter
CUDA_VISIBLE_DEVICES=0 python prediction_second_stage.py \
--model             ${model}                             \
--batch_size        32                                   \
--num_workers       20                                   \
--output_dir        ${model_dirpath}                     \
--model_name        ${model}_best_model.pth.tar          \
--test_folder       ${test_dirpath}                      \
--excel_path        ${excel_dirpath}                     \
--npz_name          brain_age.npz                        \
--dis_range         5                                    \
--first_stage_net   ${first_stage_net}                   \





