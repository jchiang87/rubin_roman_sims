import os
import glob
import json
from collections import defaultdict


__all__ = ['make_visit_tranches', 'omit_existing_ccds']


def omit_existing_ccds(visit, ccds, output_dir):
    return [det_name for det_name in ccds if not
            glob.glob(os.path.join(output_dir,
                                   f"amp_*{visit}*{det_name}*.fits*"))]


def make_visit_tranches(num_tranches, output_dir, ccd_list_file=None):
    # Read in CCD lists keyed by visit.
    if ccd_list_file is None:
        ccd_list_file = os.path.join(os.environ['RUBIN_ROMAN_SIMS_DIR'], 'data',
                                     'AY2022_sims_ccds_rw0.9_v2.99.json')

    with open(ccd_list_file) as fobj:
        ccd_lists = json.load(fobj)

    # Create tranches of visits by cycling through sorted_lists.
    visit_tranches = defaultdict(dict)
    for i, (visit, ccds) in enumerate(ccd_lists.items()):
        key = i % num_tranches
        visit_tranches[key][visit] = omit_existing_ccds(visit, ccds, output_dir)
    return visit_tranches
