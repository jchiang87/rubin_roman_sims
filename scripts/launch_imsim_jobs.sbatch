#!/bin/bash

## For running in production mode on Perlmutter:
##SBATCH --qos=regular
##SBATCH --constraint=cpu
##SBATCH --time=10:00:00
#
## For running tests in debug on knl:
#SBATCH --qos=debug
#SBATCH --constraint=knl
#SBATCH --time=00:30
#
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --array=0-4

srun python ./run_imsim.py $SLURM_ARRAY_TASK_ID 5 &
wait
