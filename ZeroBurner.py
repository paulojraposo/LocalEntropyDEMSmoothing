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


def main():

    parser = argparse.ArgumentParser(description="Takes a one-band GeoTiff assumed to have some zero-valued pixels, and another one-band GeoTiff, and burns zero values into the second raster where the first one has them.")
    parser.add_argument('IN_ZEROED_RAST', help="Full path to a one-band GeoTiff that contains zero-valued pixels to be replicated in the other raster.")
    parser.add_argument('IN_TO_BURN_RAST', help="Full path to a one-band GeoTiff to be modified so that it has zero-valued pixels in the same locations as IN_ZEROED_RAST. Must be the same size in rows and columns.")
    parser.add_argument('OUTRAST', help="Full path to output GeoTIFF, containing the pixel values of IN_TO_BURN_RAST, except where IN_ZEROED_RAST had zero-valued pixels, where the new pixel value is also zero. Created as a one-band 32-bit float GeoTiff, with -99999.0 as NoData.")
    args = parser.parse_args()

    print("Reading first GeoTiff...")
    # 0
    data0 = gdal.Open(args.IN_ZEROED_RAST)
    band0 = data0.GetRasterBand(1)
    arr0 = gdal.Band.ReadAsArray(band0).astype("float32")
    nRowsO, nColsO = arr0.shape

    print("Reading second GeoTiff...")
    # 1
    data1 = gdal.Open(args.IN_TO_BURN_RAST)
    band1 = data1.GetRasterBand(1)
    arr1 = gdal.Band.ReadAsArray(band1).astype("float32")
    nRows1, nCols1 = arr1.shape
    # Also get information for building the georeferenced output GeoTiff
    # from this raster:
    band1XSize = band1.XSize
    band1YSize = band1.YSize
    GeoTransform = data1.GetGeoTransform()
    WKTProjection = data1.GetProjection()

    # We check that both rasters are the same size in terms of rows by
    # columns, since not being so would crash or array indexing in the
    # next step.
    if not ( ( nRows1 == nRowsO ) and ( nCols1 == nColsO ) ):
        print("Number of rows and columns don't match! Aborting program.")
        exit()

    print("Burning zeros...")
    for nRow in range(nRows1):
        for nCol in range(nCols1):
            if arr0[ nRow, nCol ] == 0.0:
                arr1[ nRow, nCol ] = 0.0
    
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(args.OUTRAST, band1XSize, band1YSize, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(GeoTransform)
    ds.SetProjection(WKTProjection)
    dsB1 = ds.GetRasterBand(1)
    dsB1.SetNoDataValue(-99999.0)
    dsB1.WriteArray(arr1)
    ds.FlushCache()

    print("Written out to: " + args.OUTRAST)


if __name__ == '__main__':
    main()
