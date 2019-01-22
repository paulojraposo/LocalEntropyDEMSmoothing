#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/


# Some common functions used across several scripts here.

import platform, socket, os
import gdal


def printandlog(aMessage, logFilePath):
    """Prints to STOUT, and appends with a newline-ending to a text file to write a log of messages."""
    print(aMessage)
    with open(logFilePath, "a") as theFile:
        theFile.write(aMessage + "\n")

def OSandHost(theLogFile):
    """Check whether Linux or Windows, and what machine by name. Returns 'Windows' or 'Linux' on my machines for platform."""
    theHostName = socket.gethostname()
    currentPlatform = platform.system()
    printandlog("Running on " + theHostName + ", " + currentPlatform, theLogFile)
    return theHostName, currentPlatform

def GeoTiffToSAGA(pathtoGeoTiff):

    """Takes the full path of a one-band GeoTiff file and saves it in the same directory in 32-bit float SAGA raster format. Sets NoData to -99999.0. Returns full path to SAGA sdat file."""

    NoData = -99999.0

    GTiffDir, GTiffFile = os.path.split(pathtoGeoTiff)
    GTiffbasename = os.path.splitext( GTiffFile )[0]
    SAGAFile = os.path.join(GTiffDir, GTiffbasename + ".sdat") # not .sgrd in GDAL

    GTiffData = gdal.Open(pathtoGeoTiff)
    band = GTiffData.GetRasterBand(1)
    a = gdal.Band.ReadAsArray(band).astype("float32")

    driver = gdal.GetDriverByName('SAGA')
    ds = driver.Create(SAGAFile, band.XSize, band.YSize, 1, gdal.GDT_Int32)
    ds.SetGeoTransform(GTiffData.GetGeoTransform())
    ds.SetProjection(GTiffData.GetProjection())
    band = ds.GetRasterBand(1)
    band.SetNoDataValue(NoData)
    band.WriteArray(a)
    ds.FlushCache() # Write raster to disk.

    return SAGAFile


def SAGAtoGeoTiff(pathtoSAGAfile):

    """Takes the full path of a one-band SAGA raster file and saves it in the same directory in 32-bit float GeoTiff raster format. Sets NoData to -99999.0. Returns full path to GeoTiff file."""

    NoData = -99999.0

    SAGADir, SAGAFile = os.path.split(pathtoSAGAfile)
    SAGAbasename, SAGAextension = os.path.splitext( SAGAFile )
    GeoTiffFile = os.path.join(SAGADir, SAGAbasename + ".tif")

    # Handle sdat/sgrd issue between SAGA and GDAL
    if SAGAextension == ".sgrd":
        correctedFile = os.path.splitext(pathtoSAGAfile)[0] + ".sdat"
    else:
        correctedFile = pathtoSAGAfile

    SAGAData = gdal.Open(correctedFile)
    band = SAGAData.GetRasterBand(1)
    a = gdal.Band.ReadAsArray(band).astype("float32")

    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(GeoTiffFile, band.XSize, band.YSize, 1, gdal.GDT_Int32)
    ds.SetGeoTransform(SAGAData.GetGeoTransform())
    ds.SetProjection(SAGAData.GetProjection())
    band = ds.GetRasterBand(1)
    band.SetNoDataValue(NoData)
    band.WriteArray(a)
    ds.FlushCache() # Write raster to disk.

    return GeoTiffFile
