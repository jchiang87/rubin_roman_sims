import os
import logging
import sqlite3
import pandas as pd
import galsim
import imsim


__all__ = ['RunImSim']


_ay2022_query = """select * from observations where
                   observationStartMJD < 60583.001805555556 and
                   48.24 < fieldRA and fieldRA < 58.76 and
                   -44.05 < fieldDec and fieldDec < -35.95"""

_camera = imsim.get_camera('LsstCam')


class RunImSim:
    def __init__(self, sky_catalog_file, opsim_db_file,
                 output_dir, psf_dir='atm_psf_files', log_level=logging.INFO):
        self.sky_catalog_file = sky_catalog_file
        self.opsim_db_file = opsim_db_file
        assert os.path.isfile(opsim_db_file)
        with sqlite3.connect(opsim_db_file) as con:
            self.opsim_db = pd.read_sql(_ay2022_query, con)
        self.output_dir = output_dir
        self.psf_dir = psf_dir
        logging.basicConfig(format="%(asctime)s: %(message)s")
        self.logger = logging.getLogger('RunImSim')
        self.logger.setLevel(log_level)

    def make_atm_psf(self, visit):
        print(f"making atm_psf for {visit}")
        row = self.opsim_db.query(f'observationId=={visit}').iloc[0]
        airmass = row['airmass']
        rawSeeing = row['seeingFwhm500']
        band = row['filter']
        boresight = galsim.CelestialCoord(row['fieldRA']*galsim.degrees,
                                          row['fieldDec']*galsim.degrees)
        rng = galsim.BaseDeviate(visit)
        exptime = row['visitExposureTime']
        screen_size = 409.6
        doOpt = False
        snap = 1
        nproc = 1
        save_file = os.path.join(self.psf_dir,
                                 f'atm_psf_{visit:08d}-{snap:1d}-{band}.pkl')
        imsim.AtmosphericPSF(airmass, rawSeeing, band, boresight, rng,
                             exptime=exptime, screen_size=screen_size,
                             doOpt=doOpt, nproc=nproc, save_file=save_file)

    def __call__(self, visit, only_dets, nproc=1, nobjects=None,
                 random_seed=None):
        global _camera
        visit = int(visit)
        if random_seed is None:
            random_seed = visit
        config = {'template': 'imsim-config',
                  'input.instance_catalog': '',
                  'input.sky_catalog':
                      {'file_name': self.sky_catalog_file,
                       'apply_dc2_dilation':  True},
                  'input.opsim_meta_dict.file_name': self.opsim_db_file,
                  'input.opsim_meta_dict.visit': visit,
                  'input.tree_rings.only_dets': only_dets,
                  'input.atm_psf.save_file':
                      {'type': 'FormattedStr',
                       'format': os.path.join(self.psf_dir,
                                              'atm_psf_%08d-%1d-%s.pkl'),
                       'items': [{'type': 'OpsimMeta', 'field': 'observationId'},
                                 {'type': 'OpsimMeta', 'field': 'snap'},
                                 {'type': 'OpsimMeta', 'field': 'band'}]
                       },
                  'image.random_seed': random_seed,
                  'gal.type': 'SkyCatObj',
                  'stamp.world_pos.type': 'SkyCatWorldPos',
                  'stamp.fft_sb_thresh': 1e5,
                  'output.nproc': nproc,
                  'output.camera': 'LsstCam',
                  'output.only_dets': only_dets,
                  'output.dir': self.output_dir,
                  'output.det_num.first': 0,
                  'output.nfiles': len(only_dets),
                  'output.timeout': 1e5,
                  'output.truth.dir': '@output.dir'}
        if nobjects is not None:
            config['image.nobjects'] = nobjects
        galsim.config.Process(config, logger=self.logger)
