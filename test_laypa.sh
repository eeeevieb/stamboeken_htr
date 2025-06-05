#!/bin/bash
#Set job requirements
#SBATCH -N 1
#SBATCH -t 1:00:00
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=e.m.biesot@student.vu.nl
#SBATCH -p gpu_mig
#SBATCH --gpus=1

cd laypa

conda activate laypa

python train.py -c configs/config_stamboeken.yaml -t train -v val --num-gpus 1 --opts SOLVER.IMS_PER_BATCH 32 SOLVER.MAX_ITER 1




