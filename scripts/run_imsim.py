import os
import sys
import json
from collections import defaultdict
from desc.rubin_roman_sims import RunImSim

def make_visit_tranches(num_tranches, ccd_list_file=None):
    # Read in CCD lists keyed by visit.
    if ccd_list_file is None:
        ccd_list_file = os.path.join(os.environ['RUBIN_ROMAN_SIMS_DIR'], 'data',
                                     'AY2022_sims_ccds_rw0.9_v2.99.json')

    with open(ccd_list_file) as fobj:
        ccd_lists = json.load(fobj)

    # Sort by number of CCDs in descending order.
    sorted_lists = sorted(ccd_lists.items(), key=lambda x: len(x[1]),
                          reverse=True)

    # Create tranches of visits by cycling through sorted_lists.
    visit_tranches = defaultdict(dict)
    for i in range(0, len(sorted_lists), num_tranches):
        for j in range(num_tranches):
            index = i + j
            if index >= len(sorted_lists):
                break
            visit, ccds = sorted_lists[index]
            visit_tranches[j][visit] = ccds

    return visit_tranches


tranche = int(sys.argv[1])
num_tranches = int(sys.argv[2])
assert tranche < num_tranches
visit_tranches = make_visit_tranches(num_tranches)

#root_dir = '/global/cfs/cdirs/descssim/imSim'
#sky_catalog_file = os.path.join(root_dir, 'skyCatalogs_v2/skyCatalog.yaml')
#opsim_db_file = os.path.join(root_dir, 'lsst/data/draft2_rw0.9_v2.99_10yrs.db')
#output_dir = 'rubin_roman_sims_y1'
#run_imsim = RunImSim(sky_catalog_file, opsim_db_file, output_dir=output_dir)
#
def run_imsim(visit, ccds, nproc=1):
    """Function to use for debugging dividing ccd lists into tranches"""
    print(visit, len(ccds), nproc)

nproc = 64   # Conservative guess for running safely on Perlmutter.
for visit, ccds in visit_tranches[tranche].items():
    run_imsim(visit, ccds, nproc=nproc)
