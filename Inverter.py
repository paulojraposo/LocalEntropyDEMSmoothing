#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/


# Input numbers should all be integers.


import os, datetime, argparse, shutil
import numpy as np
from osgeo import gdal
import processingCommon as pc


scriptName = "Inverter.py"


def main():

    parser = argparse.ArgumentParser(description='Inverts a raster surface through the z axis about its mid-range point.')
    parser.add_argument('INPUTRAST', help='Full path to the input GeoTiff surface file.')
    parser.add_argument('OUTPUTRAST', help='Full path to the output GeoTiff surface file to create.')
    args = parser.parse_args()
    inRast  = args.INPUTRAST
    outRast = args.OUTPUTRAST

    gdal.UseExceptions()
    NoDataVal = -99999

    # Set up log file and working directory.
    outPathDir, outFile = os.path.split(outRast)
    outFileNoExt = os.path.splitext(outFile)[0]
    theLog = os.path.join(outPathDir, outFileNoExt + "_log.txt")

    # Note and print start time
    startTime = datetime.datetime.now()
    pc.printandlog("\nStarting {} at ".format(scriptName) + str(datetime.datetime.now()), theLog)

    pc.printandlog("Input file:  {}".format(inRast), theLog)
    pc.printandlog("Output file: {}".format(outRast), theLog)

    # Read input raster, get statistics on it.
    ds = gdal.Open(inRast)
    b = ds.GetRasterBand(1) # Assume only 1 band.
    b.ComputeStatistics(False)
    mdata = b.GetMetadata() # Returns a dictionary with values for "STATISTICS_X" where X can be
                            # one of MEAN, MINIMUM, MAXIMUM, STDDEV. Values are given as strings.
    terrMin = float(mdata["STATISTICS_MINIMUM"]) # Given as float
    terrMax = float(mdata["STATISTICS_MAXIMUM"]) # Given as float
    # Test to see whether these are whole-number integer values.
    if terrMin.is_integer() and terrMax.is_integer():
        pass
    else:
        pc.printandlog("One or both of the terrain minimum & maximum is not an integer.", theLog)
    xSize = b.XSize
    ySize = b.YSize
    totalPixels = xSize * ySize
    rMin = mdata["STATISTICS_MINIMUM"]
    rMax = mdata["STATISTICS_MAXIMUM"]
    rng = float(rMax) - float(rMin)
    halfrng = rng / 2.0
    fulcrum = float(rMin) + halfrng
    pc.printandlog("Raster size is {:,} by {:,} = {:,} total pixels.".format(xSize, ySize, totalPixels), theLog)
    pc.printandlog("Raster Statistics", theLog)
    pc.printandlog("Min ............. " + rMin, theLog)
    pc.printandlog("Max ............. " + rMax, theLog)
    pc.printandlog("Range ........... " + str(rng), theLog)
    pc.printandlog("Fulcrum point at  " + str(fulcrum), theLog)

    # Getting geotransform and projection information.
    geoTrans = ds.GetGeoTransform()
    wktProjection = ds.GetProjection()

    # Reading to numpy array.
    bArr = gdal.Band.ReadAsArray(b) # probably as dtype=int16
    bArr32 = bArr.astype("Int32") # Ensure 32-bit signed integer array.
    bArr32copy = np.copy(bArr32)

    pc.printandlog("Inverting, please wait...", theLog)

    # Inversion.
    for x in np.nditer(bArr32copy, op_flags=["readwrite"]):

        if x != NoDataVal: # We want to leave the NoData cells unchanged.

            px = float(x)

            if px > fulcrum:
                diff = px - fulcrum
                newVal = fulcrum - diff
                intTrue = newVal.is_integer()
                if intTrue == False:
                    print("error maybe, newVal is " + str(newVal)) # should be an int
                x[...] = np.int32(int(newVal))

            if px < fulcrum:
                diff = fulcrum - px
                newVal = fulcrum + diff
                intTrue = newVal.is_integer()
                if intTrue == False:
                    print("error maybe, newVal is " + str(newVal)) # should be an int
                x[...] = np.int32(int(newVal))

            # if px == fulcrum, we simply leave it unchanged.

    pc.printandlog("Numpy calculations complete." ,theLog)
    dst_filename = outRast
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_filename, xSize, ySize, 1, gdal.GDT_Int32)
    dataset.SetGeoTransform(geoTrans)
    dataset.SetProjection(wktProjection)
    oBand = dataset.GetRasterBand(1)
    oBand.SetNoDataValue(NoDataVal)
    oBand.WriteArray(bArr32copy)
    dataset.FlushCache() # Finally writes raster to disk.

    endTime = datetime.datetime.now()
    totalTime = endTime - startTime
    pc.printandlog("Output written to " + dst_filename, theLog)
    pc.printandlog("Total elapsed time: " + str(totalTime) + "\n", theLog)



if __name__ == "__main__":
    main()
