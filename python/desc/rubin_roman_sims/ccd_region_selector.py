import os
import json
import sqlite3
import warnings
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import galsim
import lsst.geom
import lsst.sphgeom
from lsst.afw import cameraGeom
from lsst.obs.lsst import LsstCam
import imsim


__all__ = ['get_convex_polygon', 'WcsInterfaceFactory', 'SkyRegion']


def get_convex_polygon(corners):
    vertices = []
    for corner in corners:
        lonlat = lsst.sphgeom.LonLat.fromDegrees(*corner)
        vertices.append(lsst.sphgeom.UnitVector3d(lonlat))
    return lsst.sphgeom.ConvexPolygon(vertices)


class WcsInterface:
    def __init__(self, wcs, ra0, dec0, center_det):
        self.wcs = wcs
        self.ra0 = ra0
        self.dec0 = dec0
        self.transform = center_det.getTransform(cameraGeom.FOCAL_PLANE,
                                                 cameraGeom.PIXELS)

    def get_sky_corners(self, det):
        sky_corners = []
        for fp_corner in det.getCorners(cameraGeom.FOCAL_PLANE):
            pixel_coords = self.transform.applyForward(fp_corner)
            sky_corners.append(self.wcs.toWorld(pixel_coords.x, pixel_coords.y,
                                                units=galsim.degrees))
        return sky_corners

    def get_CCD_polygon(self, det):
        return get_convex_polygon(self.get_sky_corners(det))

    def draw(self, det, linestyle='-', color=None):
        ra, dec = [list(_) for _ in zip(*self.get_sky_corners(det))]
        ra.append(ra[0])
        dec.append(dec[0])
        plt.plot(ra, dec, linestyle=linestyle, color=color)

    def get_sky_center(self, det):
        center = det.getCenter(cameraGeom.FOCAL_PLANE)
        pixel_coords = self.transform.applyForward(center)
        return self.wcs.toWorld(pixel_coords.x, pixel_coords.y,
                                units=galsim.degrees)


class WcsInterfaceFactory:
    def __init__(self, opsim_file, query=None):
        self.center_det = LsstCam.getCamera()[94]
        assert os.path.isfile(opsim_file)
        if query is None:
            query = 'select * from observations'
        with sqlite3.connect(opsim_file) as con:
            self.df = pd.read_sql(query, con)
        self.bands = dict(zip(self.df['observationId'], self.df['filter']))

    def create(self, visit):
        row = self.df.query(f"observationId == {visit}").iloc[0]
        ra0, dec0 = row.fieldRA, row.fieldDec
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            wcs = imsim.readout.make_batoid_wcs(
                ra0, dec0, row.rotTelPos, row.observationStartMJD,
                row['filter'], 'LsstCam')
        return WcsInterface(wcs, ra0, dec0, self.center_det)


class SkyRegion:
    def __init__(self, ra_range, dec_range):
        self.region_corners = ((ra_range[0], dec_range[0]),
                               (ra_range[1], dec_range[0]),
                               (ra_range[1], dec_range[1]),
                               (ra_range[0], dec_range[1]))
        self.skycoords = [galsim.CelestialCoord(ra*galsim.degrees,
                                                dec*galsim.degrees)
                          for ra, dec in self.region_corners]
        self.region_polygon = get_convex_polygon(self.region_corners)

    def overlapping_ccds(self, camera, wcs_interface):
        det_names = []
        for det in camera:
            ccd_polygon = wcs_interface.get_CCD_polygon(det)
            if self.region_polygon.intersects(ccd_polygon):
                det_names.append(det.getName())
        return det_names

    def min_sep(self, ra, dec):
        coord = galsim.CelestialCoord(ra*galsim.degrees, dec*galsim.degrees)
        return min(coord.distanceTo(_) for _ in self.skycoords)/galsim.degrees

    def draw(self, linestyle='-', color=None):
        x, y = [list(_) for _ in zip(*self.region_corners)]
        x.append(x[0])
        y.append(y[0])
        plt.plot(x, y, linestyle=linestyle, color=color)


def get_start_mjd(opsim_db):
    if not os.path.isfile(opsim_db):
        raise FileNotFoundError(opsim_db)
    query = ('select observationStartMJD from observations order by '
             'observationStartMJD asc limit 1')
    with sqlite3.connect(opsim_db) as con:
        result = con.execute(query).fetchone()[0]
    return result


if __name__ == '__main__':
    camera = LsstCam.getCamera()
    det_nums = {_.getName(): _.getId() for _ in camera}

    sky_region = SkyRegion((51, 56), (-42, -38))

#    opsim_file = ('/global/cfs/cdirs/descssim/imSim/lsst/data/'
#                  'baseline_v2.1_10yrs.db')
#    json_file = 'AY2022_sims_ccds_v2.1.json'

    opsim_file = ('/global/cfs/cdirs/descssim/imSim/lsst/data/'
                  'draft2_rw0.9_v2.99_10yrs.db')
    json_file = 'AY2022_sims_ccds_rw0.9_v2.99.json'
    ccd_coords_file = 'AY2022_sims_ccds_rw0.9_v2.99.parq'

#    opsim_file = ('/global/cfs/cdirs/descssim/imSim/lsst/data/'
#                  'draft2_rw0.9_uz_v2.99_10yrs.db')
#    json_file = 'AY2022_sims_ccds_rw0.9_uz_v2.99.json'
#    ccd_coords_file = 'AY2022_sims_ccds_rw0.9_uz_v2.99.parq'

    mjd_max = get_start_mjd(opsim_file) + 365.
    query = ("select * from observations where "
             f"observationStartMJD < {mjd_max} and "
             f"{51 - 2.76} < fieldRA and fieldRA < {56 + 2.76} and "
             f"{-42 - 2.05} < fieldDec and fieldDec < {-38 + 2.05}")
    print(query)
    wcs_factory = WcsInterfaceFactory(opsim_file, query)
    num_visits = len(wcs_factory.df)
    print(num_visits)

    if not os.path.isfile(json_file):
        ccd_lists = {}
        for i, visit in enumerate(wcs_factory.df['observationId']):
            wcs = wcs_factory.create(visit)

            if sky_region.min_sep(wcs.ra0, wcs.dec0) < 2.04:
                my_ccds = sky_region.overlapping_ccds(camera, wcs)
                if my_ccds:
                    ccd_lists[visit] = my_ccds
                print(i, num_visits, visit, len(my_ccds))

        with open(json_file, 'w') as fobj:
            json.dump(ccd_lists, fobj)
    else:
        with open(json_file) as fobj:
            ccd_lists = json.load(fobj)

    if not os.path.isfile(ccd_coords_file) or True:
        data = defaultdict(list)
        for visit, ccds in ccd_lists.items():
            visit = int(visit)  # json module converts the visit values to str
            wcs = wcs_factory.create(visit)
            for ccd in ccds:
                det = camera[ccd]
                det_name = det.getName()
                data['visit'].append(visit)
                data['band'].append(wcs_factory.bands[visit])
                ra, dec = wcs.get_sky_center(det)
                data['ra'].append(ra)
                data['dec'].append(dec)
                data['det_name'].append(det_name)
                data['detector'].append(det_nums[det_name])
        df = pd.DataFrame(data)
        df.to_parquet(ccd_coords_file)
    else:
        df = pd.read_parquet(ccd_coords_file)
