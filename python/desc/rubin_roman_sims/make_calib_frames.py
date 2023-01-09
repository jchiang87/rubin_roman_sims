import os
import logging
import galsim
from lsst.afw import cameraGeom
import imsim


__all__ = ['make_calib_frames']


def make_calib_frames(exptime, output_dir, random_seed, snap=0,
                      nproc=1, only_dets=None, sky_level=0,
                      camera_name='LsstCam'):
    if only_dets is None:
        camera = imsim.get_camera(camera_name)
        only_dets = [det.getName() for det in camera
                     if det.getType() == cameraGeom.DetectorType.SCIENCE]
    if sky_level == 0:
        tree_ring_dets = only_dets[0]
    else:
        tree_ring_dets = only_dets
    imsim_dir = os.environ['IMSIM_DIR']
    # The sky_catalog, opsim_db_file, and visit are required by
    # the config files and must exist, but otherwise are not used
    # for generating biases or darks.
    sky_catalog = os.path.join(imsim_dir, 'tests', 'data', 'sky_cat_9683.yaml')
    opsim_db_file = os.path.join(imsim_dir, 'data', 'small_opsim.db')
    visit = 222556

    config = {'template': 'imsim-config',
              'input.instance_catalog': '',
              'input.sky_catalog': {'file_name': sky_catalog},
              'input.opsim_meta_dict.file_name': opsim_db_file,
              'input.opsim_meta_dict.visit': visit,
              # Tree rings are not used, but specify one to minimize
              # the time to load the data, since an empty list loads all
              # of them.
              'input.tree_rings.only_dets': tree_ring_dets,
              'input.atm_psf': "",
              'image.random_seed': random_seed,
              'image.nobjects': 0,
              'image.sky_level': sky_level,
              'gal.type': 'SkyCatObj',
              'stamp.world_pos.type': 'SkyCatWorldPos',
              'output.nproc': nproc,
              'output.camera': camera_name,
              'output.exp_time': exptime,
              'output.only_dets': only_dets,
              'output.dir': output_dir,
              'output.det_num.first': 0,
              'output.nfiles': len(only_dets),
              'output.timeout': 1e5,
              'output.truth': "",
              'output.file_name':
                  {'type': 'FormattedStr',
                   'format': 'eimage_%s-%03d-%s.fits',
                   'items': [output_dir, snap, "$det_name"]},
              'output.readout.file_name':
                  {'type': 'FormattedStr',
                   'format': 'amp_%s-%03d-%s.fits.fz',
                   'items': [output_dir, snap, "$det_name"]}}

    logging.basicConfig(format="%(asctime)s: %(message)s")
    logger = logging.getLogger('make_dark_frames')
    galsim.config.Process(config, logger=logger)
