#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/


# Calculating local entropy using the method built into scikit-image.
# IMPORTANT: The method only ingests unsigned 8 or 16 bit integer pixel types. May
# need to convert input rasters into uint16!

scriptName = "LocalEntropy.py"

import datetime, argparse, os, sys
from osgeo import gdal
import numpy as np
import processingCommon as pc
from skimage.filters.rank import entropy
from skimage.morphology import disk





def main():

    parser = argparse.ArgumentParser(description="Calculates local entropy by on pixel-by-pixel basis, outputs an image of this.")
    parser.add_argument('INIMAGE', help="Full path to the input image.")
    parser.add_argument('OUTIMAGE', help="Full path to the output image.")
    parser.add_argument('DISKRADIUS', help="Size in pixels of disk structuring element (i.e., kernel) to use.")
    args = parser.parse_args()
    inIMAGE = args.INIMAGE
    outIMAGE = args.OUTIMAGE
    diskRadius = int(args.DISKRADIUS)

    NoDataVal = -99999
    gdal.UseExceptions()

    # Set up log file location.
    # Also get some path to input raster folder for later use.
    inPathDir, inFile   = os.path.split(inIMAGE)
    outPathDir, outFile = os.path.split(outIMAGE)
    outFileNoExt        = os.path.splitext(outFile)[0]
    theLog              = os.path.join(outPathDir, outFileNoExt + "_log.txt")


    # Note and print start time
    startTime = datetime.datetime.now()
    print("")
    pc.printandlog("Starting " + scriptName + " at " + str(startTime), theLog)

    pc.printandlog("Input file:  " + str(inIMAGE), theLog)
    pc.printandlog("Output file: " + str(outIMAGE), theLog)
    pc.printandlog("diskRadius:  {}".format(str(diskRadius)), theLog)

    # Open and load data, convert to numpy array.
    ds = gdal.Open(inIMAGE)
    b = ds.GetRasterBand(1) # Assuming only 1 band.
    bArr = gdal.Band.ReadAsArray(b)
    bArr_u16 = bArr.astype(np.uint16) # unsigned 16 bit integer - possibly bad with some input rasters.

    # Get geotransform and projection information.
    geoTrans = ds.GetGeoTransform()
    wktProjection = ds.GetProjection()

    # Calc entropy on disk-shaped kernel of given size...
    pc.printandlog("Calculating local entropy. Please wait, this make take a while...", theLog)
    ent = entropy(bArr_u16, disk(diskRadius)) # TODO: change to square? Or later work to disk?

    # Writing to file with tranform info.
    driver = gdal.GetDriverByName("GTiff")
    dst_filename = outIMAGE
    out_ds = driver.Create(dst_filename, b.XSize, b.YSize, 1, gdal.GDT_UInt16) # unsigned 16 bit integer
    # out_ds = driver.Create(dst_filename, b.XSize, b.YSize, 1, gdal.GDT_Int32) # unsigned 32 bit integer
    out_ds.SetGeoTransform(geoTrans)
    out_ds.SetProjection(wktProjection)
    oBand = out_ds.GetRasterBand(1)
    oBand.SetNoDataValue(NoDataVal)
    oBand.WriteArray(ent)
    oBand.ComputeStatistics(True)

    pc.printandlog("Written out to: " + dst_filename, theLog)

    # Print ending message for script.
    endTime = datetime.datetime.now()
    pc.printandlog("Ending at " + str(endTime) + ". Total time: " + str(endTime - startTime) + "\n", theLog)


if __name__ == "__main__":
    main()
