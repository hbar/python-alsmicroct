#!/bin/bash -l
#SBATCH --partition=regular
#SBATCH --nodes=1
#SBATCH --time 20:00:00
#SBATCH --job-name=hbar_recons
#SBATCH --output hbar_recons.o%j
#SBATCH --license=SCRATCH
srun -N 1 -n 8 -c 3 python /global/homes/h/hbar/NuclearCMC_reconstruction_batch.py

