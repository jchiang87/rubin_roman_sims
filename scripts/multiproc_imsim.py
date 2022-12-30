import os
import sys
import yaml
import subprocess
import multiprocessing
from desc.rubin_roman_sims import RunImSim, make_visit_tranches

sky_catalog_file = '/global/cfs/cdirs/descssim/imSim/skyCatalogs_v2/skyCatalog.yaml'

opsim_db_file = '/global/cfs/cdirs/descssim/imSim/lsst/data/draft2_rw0.9_v2.99_10yrs.db'

output_dir = 'ay2022_sims'

run_imsim = RunImSim(sky_catalog_file=sky_catalog_file,
                     opsim_db_file=opsim_db_file,
                     output_dir=output_dir)

config_dir = 'config_files'
if not os.path.isdir(config_dir):
    os.makedirs(config_dir)
log_dir = 'logging'
if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

nobjects = None

num_tranches = int(sys.argv[1])
tranche = int(sys.argv[2])
visit_tranches = make_visit_tranches(num_tranches, output_dir)

processes = 71
with multiprocessing.Pool(processes=processes) as pool:
    workers = []
    for visit, ccds in visit_tranches[tranche].items():
        for det_name in ccds:
            basename_root = f'imsim-{visit}-{det_name}'
            config_file = os.path.join(config_dir, f'{basename_root}.yaml')
            if not os.path.isfile(config_file):
                config = run_imsim.make_config(visit, [det_name],
                                               nobjects=nobjects)
                with open(config_file, 'w') as fobj:
                    yaml.dump(config, fobj)
            log_file = os.path.join(log_dir, f'{basename_root}.log')
            command = f'(perf stat -d galsim -v 2 {config_file}) >& {log_file}'
            print(tranche, command)
            workers.append(pool.apply_async(subprocess.check_call, (command,),
                                            dict(shell=True)))
    pool.close()
    pool.join()
    _ = [worker.get() for worker in workers]
