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

root_dir='/global/cfs/cdirs/descssim/imSim'
sky_catalog_file="${root_dir}/skyCatalogs_v2/skyCatalog.yaml"
opsim_db_file="${root_dir}/lsst/data/draft2_rw0.9_v2.99_10yrs.db"
srun python ./run_imsim.py --opsim-db="$opsim_db_file" --sky-catalog="$sky_catalog_file" $SLURM_ARRAY_TASK_ID 5 &
wait
