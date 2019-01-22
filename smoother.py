#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   .-.                              _____                                  __
#   /v\    L   I   N   U   X       / ____/__   ___   ___   ____ ___   ___  / /_  __  __
#  // \\                          / / __/ _ \/ __ \/ __ `/ ___/ __ `/ __ \/ __ \/ / / /
# /(   )\                        / /_/ /  __/ /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /
#  ^^-^^                         \____/\___/\____/\__, /_/   \__,_/ .___/_/ /_/\__, /
#                                                /____/          /_/          /____/



# Requires saga_cmd to be in the system PATH already.

import numpy as np
import gdal, os, argparse, subprocess, socket
import processingCommon as pc

def smooth(inGeoTiff, radius):

    print("Converting to SAGA")
    SAGA = pc.GeoTiffToSAGA(inGeoTiff)
    # print("SAGA returned: " + SAGA)
    print("Done converting")
    SAGAfilenoext = os.path.splitext(SAGA)[0]
    SAGAsgrd = SAGAfilenoext + ".sgrd"
    if socket.gethostname() == 'geovista08': # For my GeoVista machine
        sagaDir = "C:\\Program Files\\QGIS Essen\\apps\\saga"
        saga_cmd = os.path.join(sagaDir, "saga_cmd ")
    else:
        saga_cmd = "saga_cmd " # On STUDIOPR
    cmd1 = saga_cmd + "grid_filter 0 -INPUT "
    cmd2 = SAGAsgrd
    fileNoExt = SAGAfilenoext + "_smooth_rad" + str(radius)
    resultFile = fileNoExt + ".sgrd"
    print("resultfile: " + resultFile)
    cmd3 = " -RESULT " + resultFile
    cmd4 = " -MODE 1 -METHOD 0 -RADIUS " + str(radius)
    print("Calling SAGA_CMD to smooth")
    cmd = cmd1 + cmd2 + cmd3 + cmd4
    print("command is >>>" + cmd)
    subprocess.call(cmd)
    # print("Converting back to GeoTiff")
    GeoTiff = pc.SAGAtoGeoTiff(resultFile)

    print("Smoothed output saved to: " + GeoTiff)

    deleteInterim = True
    if deleteInterim:
        print("Deleting interim SAGA files")
        SAGAprj = os.path.splitext(SAGA)[0] + ".prj"
        SAGAsgrd = os.path.splitext(SAGA)[0] + ".sgrd"
        SAGAxml = SAGA + ".aux.xml"
        resultsmgrd = os.path.splitext(resultFile)[0] + ".mgrd"
        resultsprj = os.path.splitext(resultFile)[0] + ".prj"
        resultsdat = os.path.splitext(resultFile)[0] + ".sdat"
        resultxml = resultsdat + ".aux.xml"
        for sagafile in [resultFile, resultsdat, resultxml, resultsmgrd, resultsprj, SAGA, SAGAxml, SAGAsgrd, SAGAprj]:
            if os.path.isfile(sagafile):
                os.remove(sagafile)

def main():

    parser = argparse.ArgumentParser(description="Takes a GeoTiff and runs the SAGA simple filter on it, using smooth, a circle neighborhood, and a given radius in cells. Makes a SAGA version of the raster in the interim and converts back again.")
    parser.add_argument('INGEOTIFF')
    parser.add_argument('RADIUS')
    args = parser.parse_args()

    print("Input GeoTiff: " + args.INGEOTIFF)
    print("Input radius: " + args.RADIUS)

    smooth(args.INGEOTIFF, args.RADIUS)

    print("Done")


if __name__ == '__main__':
    main()
