#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/


import numpy as np
import gdal, os, argparse, sys, datetime

def VariableLowPassFilter(dem, sizingRast):

    startTime = datetime.datetime.now()

    print("Reading DEM...")
    demData = gdal.Open(dem)
    demBand = demData.GetRasterBand(1)
    demXSize = demBand.XSize
    demYSize = demBand.YSize
    demGeoTransform = demData.GetGeoTransform()
    demWKTProjection = demData.GetProjection()
    demArray = gdal.Band.ReadAsArray(demBand)
    print("Reading sizing raster...")
    sizingData = gdal.Open(sizingRast)
    sizingBand = sizingData.GetRasterBand(1)
    sizingXSize = sizingBand.XSize
    sizingYSize = sizingBand.YSize
    # Should check to see whether shape and GCS are the same for dem and sizing...
    sizingArray = gdal.Band.ReadAsArray(sizingBand).astype("Int16")

    # assert demArray.shape == sizingArray.shape

    newArray = np.copy(demArray)

    nRows, nCols = demArray.shape
    print("Performing variable kernel low-pass filter...")
    iterlabel = 1
    iCount = demYSize

    for nRow in range(demYSize):

        sys.stdout.flush()

        for nCol in range(demXSize):
            size = sizingArray[ nRow, nCol ]
            shift = size / 2
            top = max(0, nRow - shift)
            bottom = min(nRows-1, nRow+shift)
            rows = demArray[top:bottom+1]
            left = max(0, nCol-shift)
            right = min(nCols-1, nCol+shift)
            kernel = rows[:,range(left, right+1)]
            nR, nC = kernel.shape
            newArray[nRow,nCol] = float(np.sum(kernel)) / nR / nC # the low pass filter

        prcnt = round(( float(iterlabel) / float(iCount) ) * 100 , 3)
        sys.stdout.write("\r")
        sys.stdout.write("Progress: " + str(iterlabel) + " of " + str(iCount) + " | "  + str(prcnt) + r" %... | Elapsed: " + str(datetime.datetime.now() - startTime))
        iterlabel += 1
        if prcnt == 100.0:
            print("\n")

    inSizingDir, inSizingFile = os.path.split(sizingRast)
    inSizingbasename = os.path.splitext( inSizingFile )[0]
    inDEMDir, inDEMFile = os.path.split(dem)
    inDEMbasename = os.path.splitext( inDEMFile )[0]
    outDEM = os.path.join(inDEMDir, inDEMbasename + inSizingbasename + ".tif")
    print("Writing out to disk...")
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outDEM, demXSize, demYSize, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(demGeoTransform)
    ds.SetProjection(demWKTProjection)
    dsB1 = ds.GetRasterBand(1)
    dsB1.SetNoDataValue(-99999.0)
    dsB1.WriteArray(newArray)
    ds.FlushCache()

    print("Written out to: " + outDEM)

def main():

    parser = argparse.ArgumentParser(description="Performs a low-pass filter on a DEM or any raster using kernels whose dimensions are defined by the cells of another raster, which must be of the same size and shape.")
    parser.add_argument('INDEM')
    parser.add_argument('INSIZINGS')
    args = parser.parse_args()

    print("Input DEM: " + args.INDEM)
    print("Input sizing raster: " + args.INSIZINGS)

    VariableLowPassFilter(args.INDEM, args.INSIZINGS)

    print("Done")


if __name__ == '__main__':
    main()
