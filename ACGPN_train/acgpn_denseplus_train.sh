#!/usr/bin/env bash
#PBS -l select=1:ncpus=20:ngpus=4        
#PBS -l walltime=24:00:00                 
#PBS -j oe                                     
#PBS -N acgpn_densep_train                            
#PBS -q gpu                           

cd $PBS_O_WORKDIR                         

module purge
                
module load anaconda/3.2020.2
#module load conda-envs/pytorch/1.6.0

conda activate venv_vton
#source activate pytorch-1.6.0 

unset CUDA_VISIBLE_DEVICES

python train.py --dataroot ../../train_data/  --gpu_ids 0 --niter 10 --niter_decay 10 --name denseplus --denseplus  
