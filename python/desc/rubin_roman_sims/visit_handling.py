import os
import glob
import json
from itertools import cycle


__all__ = ['make_visit_tranches', 'omit_existing_ccd_visits']


def omit_existing_ccd_visits(ccd_lists, output_dir):
    return {
        visit: [
            det_name
            for det_name in ccd_candidates
            if not glob.glob(
                os.path.join(output_dir, f"amp_*{visit}*{det_name}*.fits*")
            )
        ]
        for visit, ccd_candidates in ccd_lists.items()
    }

def make_visit_tranches(num_tranches, output_dir, ccd_list_file=None):
    # Read in CCD lists keyed by visit.
    if ccd_list_file is None:
        ccd_list_file = os.path.join(os.environ['RUBIN_ROMAN_SIMS_DIR'], 'data',
                                     'AY2022_sims_ccds_rw0.9_v2.99.json')

    with open(ccd_list_file) as fobj:
        ccd_lists = json.load(fobj)

    ccd_lists = omit_existing_ccd_visits(ccd_lists, output_dir)

    # Sort by number of CCDs in descending order.
    sorted_lists = sorted(ccd_lists.items(), key=lambda x: len(x[1]),
                          reverse=True)

    # Create tranches of visits by cycling through sorted_lists.
    visit_tranches = [{}] * num_tranches
    for (tranche, (visit, ccds)) in zip(cycle(visit_tranches), sorted_lists):
        tranche[visit] = ccds

    return visit_tranches
