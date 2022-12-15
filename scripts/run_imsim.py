import os
import sys
import glob
import json
from collections import defaultdict
from desc.rubin_roman_sims import RunImSim, make_visit_tranches



#root_dir = '/global/cfs/cdirs/descssim/imSim'
#sky_catalog_file = os.path.join(root_dir, 'skyCatalogs_v2/skyCatalog.yaml')
#opsim_db_file = os.path.join(root_dir, 'lsst/data/draft2_rw0.9_v2.99_10yrs.db')
output_dir = 'rubin_roman_sims_y1'

#run_imsim = RunImSim(sky_catalog_file, opsim_db_file, output_dir=output_dir)

def run_imsim(visit, ccds, nproc=1):
    """Function to use for debugging division of ccd lists into tranches"""
    print(visit, len(ccds), nproc)

tranche = int(sys.argv[1])
num_tranches = int(sys.argv[2])
assert tranche < num_tranches

visit_tranches = make_visit_tranches(num_tranches, output_dir)

nproc = 64   # Conservative guess for running safely on Perlmutter.
for visit, ccds in visit_tranches[tranche].items():
    run_imsim(visit, ccds, nproc=nproc)
