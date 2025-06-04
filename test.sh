#!/bin/bash
#Set job requirements
#SBATCH -n 1
#SBATCH -t 5:00
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=e.m.biesot@student.vu.nl

python3 <<EOF
import torch
print(torch.cuda.is_available())
EOF
