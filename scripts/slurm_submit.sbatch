#!/bin/bash

# For running in production mode on Perlmutter:
#SBATCH --image=docker:jchiang87/imsim-env:imSim_w_2022_49
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --time=5:00:00
#SBATCH -A m1727
#
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --array=0-19

cd /pscratch/sd/j/jchiang8/imSim/AY2022_sims/bash_level_multiproc
srun shifter ./multiproc_imsim.sh 20 $SLURM_ARRAY_TASK_ID &
wait
