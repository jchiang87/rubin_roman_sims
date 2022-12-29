from astropy.io import fits
import lsst.afw.math as afwMath
import lsst.afw.image as afwImage
from lsst.afw.cameraGeom import utils as cgu
import imsim


__all__ = ['mosaic_eimages']


class EImageSource:
    isTrimmed = True
    background = 0.0

    def __init__(self, eimage_files, rafts=None):
        self.eimage_files = {}
        for eimage_file in eimage_files:
            with fits.open(eimage_file) as hdus:
                det_name = hdus[0].header['DET_NAME']
            if rafts is None or det_name.split('_')[0] in rafts:
                self.eimage_files[det_name] = eimage_file
        if not self.eimage_files:
            raise RuntimeError("No eimage files selected.")

    def getCcdImage(self, det, imageFactory, binSize=1, *args, **kwargs):
        ccdImage = afwImage.ImageF(self.eimage_files[det.getName()])
        ccdImage = afwMath.binImage(ccdImage, binSize)
        return afwMath.rotateImageBy90(ccdImage,
                                       det.getOrientation().getNQuarter()), det


def mosaic_eimages(eimage_files, binSize=8, outfile=None,
                   camera_name='LsstCam', rafts=None):
    camera = imsim.get_camera(camera_name)
    image_source = EImageSource(eimage_files, rafts=rafts)
    detectorNameList = list(image_source.eimage_files.keys())
    output_mosaic = cgu.showCamera(camera, imageSource=image_source,
                                   detectorNameList=detectorNameList,
                                   binSize=binSize)
    if outfile is not None:
        output_mosaic.writeFits(outfile)

    return output_mosaic
