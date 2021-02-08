#!/usr/bin/env bash
#PBS -l select=1:ncpus=2:ngpus=1        
#PBS -l walltime=00:10:00                 
#PBS -j oe                                     
#PBS -N unpair_acgpn_basln_batch_deb                            
#PBS -q debug                        

cd $PBS_O_WORKDIR                         

module purge
                
module load anaconda/3.2020.2
#module load conda-envs/pytorch/1.6.0

conda activate venv_vton
#source activate pytorch-1.6.0 

unset CUDA_VISIBLE_DEVICES

python test.py --dataroot ../../test_data/ --checkpoints_dir ../ACGPN_train/checkpoints/  --gpu_ids 0 --denseplus --clothrepG2 --nobodyseg --landmarks --name denseplus_flm_nobodyseg_g2dense 
