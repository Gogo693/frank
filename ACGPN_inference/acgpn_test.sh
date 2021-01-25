#!/usr/bin/env bash
#PBS -l select=1:ncpus=20:ngpus=4        
#PBS -l walltime=01:00:00                 
#PBS -j oe                                     
#PBS -N acgpn_base_test                           
#PBS -q gpu                          

cd $PBS_O_WORKDIR                         

module purge
                
module load anaconda/3.2020.2
#module load conda-envs/pytorch/1.6.0

conda activate venv_vton
#source activate pytorch-1.6.0 

unset CUDA_VISIBLE_DEVICES

python test.py --dataroot ../../Data_preprocessing/  --gpu_ids 0
