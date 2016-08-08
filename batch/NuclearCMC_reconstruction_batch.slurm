#!/bin/bash -l
#SBATCH --partition=regular
#SBATCH --nodes=1
#SBATCH --time 20:00:00
#SBATCH --job-name=hbar_recons
#SBATCH --output hbar_recons.o%j
#SBATCH --license=SCRATCH
srun -n 1 -c 24 python /global/homes/h/hbar/NuclearCMC_reconstruction_batch.py

