#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/


import numpy as np
import gdal, os, argparse

def multiply(rast, aFactor):
    """foo"""
    print("Reading raster...")
    rastData = gdal.Open(rast)
    rastBand = rastData.GetRasterBand(1)
    rastXSize = rastBand.XSize
    rastYSize = rastBand.YSize
    rastGeoTransform = rastData.GetGeoTransform()
    rastWKTProjection = rastData.GetProjection()
    rastArray = gdal.Band.ReadAsArray(rastBand)

    print("Multiplying...")
    floatFactor = float(aFactor)
    for x in np.nditer(rastArray, op_flags=["readwrite"]):
        x[...] = x * floatFactor

    inrastDir, inrastFile = os.path.split(rast)
    inrastbasename = os.path.splitext( inrastFile )[0]
    outrast = os.path.join(inrastDir, inrastbasename + "_x" + str(aFactor) + ".tif")
    print("Writing out to disk...")
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outrast, rastXSize, rastYSize, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(rastGeoTransform)
    ds.SetProjection(rastWKTProjection)
    dsB1 = ds.GetRasterBand(1)
    dsB1.SetNoDataValue(-99999.0)
    dsB1.WriteArray(rastArray)
    ds.FlushCache()

    print("Written out to: " + outrast)

def main():

    parser = argparse.ArgumentParser(description="Used to multiply a raster by some constant number.")
    parser.add_argument('INRAST')
    parser.add_argument('FACTOR')
    args = parser.parse_args()

    print("Input raster: " + args.INRAST)
    print("Input factor: " + args.FACTOR)
    
    multiply(args.INRAST, args.FACTOR)

    print("Done")


if __name__ == '__main__':
    main()
