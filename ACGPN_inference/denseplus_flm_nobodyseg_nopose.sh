#!/usr/bin/env bash
#PBS -l select=1:ncpus=20:ngpus=4        
#PBS -l walltime=00:10:00                 
#PBS -j oe                                     
#PBS -N nopose_test                            
#PBS -q debug                         

cd $PBS_O_WORKDIR                         

module purge
                
module load anaconda/3.2020.2
#module load conda-envs/pytorch/1.6.0

conda activate venv_vton
#source activate pytorch-1.6.0 

unset CUDA_VISIBLE_DEVICES

python test.py --dataroot ../../test_data/ --checkpoints_dir ../ACGPN_train/checkpoints/  --gpu_ids 0 --denseplus --nobodyseg --landmarks --noopenpose --name denseplus_flm_nobodyseg_nopose
