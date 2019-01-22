#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/



import numpy as np
import gdal, os, argparse, datetime, sys

def performscaling(raster_at_scale, raster_to_scale):

    startTime = datetime.datetime.now()

    print("Reading raster at scale...")
    atSData = gdal.Open(raster_at_scale)
    atSBand = atSData.GetRasterBand(1)
    atSArray = gdal.Band.ReadAsArray(atSBand).astype("float32")
    atSMin = np.amin(atSArray)
    atSMax = np.amax(atSArray)
    atSRange = atSMax - atSMin
    print("At-scale min and max: " + str(atSMin) + " " + str(atSMax))

    print("Reading raster to scale...")
    toSData = gdal.Open(raster_to_scale)
    toSBand = toSData.GetRasterBand(1)
    toSXSize = toSBand.XSize
    toSYSize = toSBand.YSize
    GeoTransform = toSData.GetGeoTransform()
    WKTProjection = toSData.GetProjection()
    toSArray = gdal.Band.ReadAsArray(toSBand).astype("float32")
    toSMin = np.amin(toSArray)
    toSMax = np.amax(toSArray)
    toSRange = toSMax - toSMin
    print("To-scale min and max: " + str(toSMin) + " " + str(toSMax))

    scalar = atSRange / toSRange
    print("Scalar is " + str(scalar))
    shift = atSMin - toSMin
    print("Shift is " + str(shift))
    if shift > 0.0:
        print("Shifting to-scale array")
        for x in np.nditer(toSArray, op_flags=["readwrite"]):
            x[...] = x + shift
    print("Scaling to-scale array...")

    iterlabel = 1
    iCount = toSArray.size

    for x in np.nditer(toSArray, op_flags=["readwrite"]):

        # sys.stdout.flush() # Commented progress report out - really slows down the code when run for every array element!

        if x > atSMin:
            diff = x - atSMin
            x[...] = (diff * scalar) + atSMin

        # prcnt = round(( float(iterlabel) / float(iCount) ) * 100 , 3)
        # sys.stdout.write("\r")
        # sys.stdout.write("Progress: " + str(iterlabel) + " of " + str(iCount) + " | "  + str(prcnt) + r" %... | Elapsed: " + str(datetime.datetime.now() - startTime))
        # iterlabel += 1
        # if prcnt == 100.0:
        #     print("\n")

    print("New min and max of scaled array: " + str(np.amin(toSArray)) + " " + str(np.amax(toSArray)))

    print("Writing out to disk...")
    toSDir, toSFile = os.path.split(raster_to_scale)
    toSbasename = os.path.splitext( toSFile )[0]
    atSDir, atSFile = os.path.split(raster_at_scale)
    atSbasename = os.path.splitext( atSFile )[0]
    outRast = os.path.join(toSDir, toSbasename + "_scaledto_" + atSbasename + ".tif")

    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outRast, toSXSize, toSYSize, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(GeoTransform)
    ds.SetProjection(WKTProjection)
    dsB1 = ds.GetRasterBand(1)
    dsB1.SetNoDataValue(-99999.0)
    dsB1.WriteArray(toSArray)
    ds.FlushCache()

    print("Written out to: " + outRast)

def main():

    parser = argparse.ArgumentParser(description="Takes two one-band rasters, and scales the pixel z-values in the second one to match the range of the first one.")
    parser.add_argument('INRAST_ATSCALE')
    parser.add_argument('INRAST_TOSCALE')
    args = parser.parse_args()

    print("Input raster at scale: " + args.INRAST_ATSCALE)
    print("Input raster to scale: " + args.INRAST_TOSCALE)

    performscaling(args.INRAST_ATSCALE, args.INRAST_TOSCALE)

    print("Done")


if __name__ == '__main__':
    main()
