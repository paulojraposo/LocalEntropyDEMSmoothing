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


def main():

    parser = argparse.ArgumentParser(description="Used to multiply a raster by some constant number.")
    parser.add_argument('INRAST', help="Full path to input GeoTiff.")
    parser.add_argument('FACTOR', help="The number by which to multiply each cell. Give as integer or float.")
    parser.add_argument('OUTRAST', help="Full path to output GeoTiff. Created as a one-band 32-bit Float GeoTiff, with -99999.0 as NoData.")
    args = parser.parse_args()

    print("Reading raster...")
    rastData = gdal.Open(args.INRAST)
    rastBand = rastData.GetRasterBand(1) # One-band raster assumed.
    rastXSize = rastBand.XSize
    rastYSize = rastBand.YSize
    rastGeoTransform = rastData.GetGeoTransform()
    rastWKTProjection = rastData.GetProjection()
    rastArray = gdal.Band.ReadAsArray(rastBand)

    print("Multiplying...")
    # Multiplication of array in place.
    floatFactor = float(args.FACTOR)
    for x in np.nditer(rastArray, op_flags=["readwrite"]):
        x[...] = x * floatFactor

    print("Writing out to disk...")
    driver = gdal.GetDriverByName("GTiff")
    # Float 32-bit bit depth set here:
    ds = driver.Create(args.OUTRAST, rastXSize, rastYSize, 1, gdal.GDT_Float32)
    ds.SetGeoTransform(rastGeoTransform)
    ds.SetProjection(rastWKTProjection)
    dsB1 = ds.GetRasterBand(1)
    dsB1.SetNoDataValue(-99999.0)
    dsB1.WriteArray(rastArray)
    ds.FlushCache()

    print("Written out to: " + args.OUTRAST)


if __name__ == '__main__':
    main()
