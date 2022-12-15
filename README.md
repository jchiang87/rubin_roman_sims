# rubin_roman_sims

This package uses [Slurm Job Arrays](https://docs.nersc.gov/jobs/examples/#job-arrays) to run imSim DC2-like 
simulations at NERSC that cover the [Roman-Rubin simulation region](https://ui.adsabs.harvard.edu/abs/2022arXiv220906829T/abstract)
at NERSC.

Assuming you have an environment in which you can run imSim, set up this package with
```
setup -r <path_to_rubin_roman_sims> -k
```
Copy `scripts/launch_imsim_jobs.sbatch` and `scripts/run_imsim.py` to a work area, and edit them
appropriately.

To submit the jobs, do
```
sbatch launch_imsim_jobs.sbatch
```
from your work directory.
