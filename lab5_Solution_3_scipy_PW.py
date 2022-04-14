'''*********************************************
Author: Phil White
Date: 3/23/22
Purpose: A partial solution to lab 5 using Scipy. This script
uses scipy ndimage convolve to apply kernels. Out of bounds
per the Lab 5 rules, but fast, effecive, and includes margins! 
*********************************************'''

import time
ti = time.time()
import arcpy
import numpy as np
from arcpy import env
from arcpy import sa
import scipy.ndimage

print 'import time:',time.time()-ti
ti = time.time()

def kernel_maker(winShape, winDims, radius=None):
    if winShape == 'circle':
        kernel = np.zeros(winDims)
        for i in range(0,np.size(kernel,1)):
            for j in range(0,np.size(kernel,0)):
                if ((int(radius)-j)**2+(int(radius)-i)**2)**.5 <= radius:
                    kernel[j][i] = 1 
    if winShape == 'rectangle':
        kernel = np.ones(winDims)
    
    return kernel

winShape = 'rectangle'
if winShape == 'circle':
    winDims = 15,15
    radius = (((float(11)/2)**2) + ((float(9)/2)**2))**.5
    kernel = kernel_maker(winShape, winDims, radius=radius)
if winShape == 'rectangle':
    winDims = 11,9
    kernel = kernel_maker(winShape,winDims)
    

arcpy.CheckOutExtension('SPATIAL')

env.workspace = r'C:\Users\phwh9568\GEOG_4303\Lab5\data\results'
env.overwriteOutput = 1

slopeRaster = sa.Slope(r'C:\Users\phwh9568\GEOG_4303\Lab5\data\dem_lab5')
cellSize = slopeRaster.meanCellWidth
crs = slopeRaster.spatialReference
llpt = slopeRaster.extent.lowerLeft
slopeArray = arcpy.RasterToNumPyArray(slopeRaster)
nlcdArray = arcpy.RasterToNumPyArray(r'C:\Users\phwh9568\GEOG_4303\Lab5\data\nlcd06_lab5')
aShape = nlcdArray.shape    

#green    
greenBool = np.where(nlcdArray==41,1,0) + np.where(nlcdArray==42,1,0) + np.where(nlcdArray==43,1,0) + np.where(nlcdArray==52,1,0)  
gvolv = scipy.ndimage.convolve(greenBool,kernel).astype(float)
gOut = np.where(((gvolv/kernel.sum())*100) >= 30,1,0)    

#ag
agBool = np.where(nlcdArray==81,1,0) + np.where(nlcdArray==82,1,0)
agvolv = scipy.ndimage.convolve(agBool,kernel).astype(float)
agOut = np.where(((agvolv/kernel.sum())*100) <= 5,1,0)    

#lid
lidBool = np.where(nlcdArray==21,1,0) + np.where(nlcdArray==22,1,0)
lidvolv = scipy.ndimage.convolve(lidBool,kernel).astype(float)
lidOut = np.where(((lidvolv/kernel.sum())*100) <= 20,1,0)

#water
waterBool = np.where(nlcdArray==11,1,0)
wvolv = scipy.ndimage.convolve(waterBool,kernel).astype(float)
wOut = np.where(((wvolv/kernel.sum())*100) <= 20,1,0) * np.where(((wvolv/kernel.sum())*100) >= 5,1,0)

#slope
slopevolv = scipy.ndimage.convolve(slopeArray,kernel).astype(float)
slopeOut = np.where((slopevolv/kernel.sum()) < 8,1,0)

#model
model = slopeOut + wOut + agOut + lidOut + gOut

hiDev = np.where(nlcdArray==23,0,1) * np.where(nlcdArray==24,0,1)
outModel = model * hiDev

#output
outRaster = arcpy.NumPyArrayToRaster(outModel,llpt,cellSize,cellSize)
arcpy.management.DefineProjection(outRaster,crs)
outRaster.save('site_suitability_conv.tif')

#summary
print 'total suitable pixels:',np.where(model==5,1,0).sum()
print 'run time:', time.time() - ti