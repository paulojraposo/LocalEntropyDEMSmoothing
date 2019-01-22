#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/



import numpy as np
import os, argparse
from osgeo import gdal

def performscaling(origDEM, burnDEM):
    """foo"""

    # Should assert the two are the same size and shape!

    print("Reading original...")
    origData = gdal.Open(origDEM)
    origBand = origData.GetRasterBand(1)
    aO = gdal.Band.ReadAsArray(origBand).astype("float32")
    nRowsO, nColsO = aO.shape

    print("Reading raster to burn into...")
    burnData = gdal.Open(burnDEM)
    burnBand = burnData.GetRasterBand(1)
    burnXSize = burnBand.XSize
    burnYSize = burnBand.YSize
    GeoTransform = burnData.GetGeoTransform()
    WKTProjection = burnData.GetProjection()
    aB = gdal.Band.ReadAsArray(burnBand).astype("float32")
    nRows, nCols = aB.shape

    if ( nRows == nRowsO ) and ( nCols == nColsO ):
        pass
    else:
        print("Number of rows and columns don't match! Exiting program.")
        exit()

    print("Burning zeros into raster to burn into...")
    for nRow in range(nRows):
        for nCol in range(nCols):
            if aO[ nRow, nCol ] == 0.0:
                aB[ nRow, nCol ] = 0.0

    print("Writing out to disk...")
    inDir, inFile = os.path.split(burnDEM)
    inBasename = os.path.splitext( inFile )[0]
    outRast = os.path.join(inDir, inBasename + "_zerobrn.tif")

    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outRast, burnXSize, burnYSize, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(GeoTransform)
    ds.SetProjection(WKTProjection)
    dsB1 = ds.GetRasterBand(1)
    dsB1.SetNoDataValue(-99999.0)
    dsB1.WriteArray(aB)
    ds.FlushCache()

    print("Written out to: " + outRast)

def main():

    parser = argparse.ArgumentParser(description="Takes a one-band original DEM, and a one-band processed DEM and burns zero values into the processed one where the original one has them.")
    parser.add_argument('IN_ORIG_DEM')
    parser.add_argument('IN_SURFACE_TO_BURN_INTO')
    args = parser.parse_args()

    performscaling(args.IN_ORIG_DEM, args.IN_SURFACE_TO_BURN_INTO)

    print("Done")


if __name__ == '__main__':
    main()
