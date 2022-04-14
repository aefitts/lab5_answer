'''*********************************************
Author: Phil White
Date: 3/23/22
A partial solution to lab 5. Note: this script uses a 
vectorization approach toward the moving window, but 
It is fast though! 
*********************************************'''
import time
ti = time.time()
import arcpy
import numpy as np
from arcpy import env
from arcpy import sa

print 'import time:',time.time()-ti
ti = time.time()

def make_slices(data,win_shape):
    
    rows = data.shape[0] - win_shape[0] + 1
    cols = data.shape[1] - win_shape[1] + 1
    slices = []
    for i in range(win_shape[0]):
        for j in range(win_shape[1]):
            slices.append(data[i:rows+i,j:cols+j])
    slice_shape = slices[0].shape
    return slices,slice_shape

def slice_summer(slices,slice_shape):
    sumArray = np.zeros(slice_shape)
    for s in slices:
        sumArray += s
    return sumArray

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
winShape = 11,9
winSize = float(11*9)

#green
greenBool = np.where(nlcdArray==41,1,0) + np.where(nlcdArray==42,1,0) + np.where(nlcdArray==43,1,0) + np.where(nlcdArray==52,1,0) 
greenArray = np.zeros(aShape)
slices,sShape = make_slices(greenBool,winShape)
greenSum = slice_summer(slices,sShape)
greenArray[5:-5,4:-4] = np.where(((greenSum/99)*100)>=30,1,0)

#ag
agBool = np.where(nlcdArray==81,1,0) + np.where(nlcdArray==82,1,0)
agArray = np.zeros(aShape)
slices,sShape = make_slices(agBool,winShape)
agSum = slice_summer(slices,sShape)
agArray[5:-5,4:-4] = np.where(((agSum/99)*100)<=5,1,0)

#lid
lidBool = np.where(nlcdArray==21,1,0) + np.where(nlcdArray==22,1,0)
lidArray = np.zeros(aShape)
slices,sShape = make_slices(lidBool,winShape)
lidSum = slice_summer(slices,sShape)
lidArray[5:-5,4:-4] = np.where(((lidSum/99)*100)<=20,1,0)

#water
waterBool = np.where(nlcdArray==11,1,0)
waterArray = np.zeros(aShape)
slices,sShape = make_slices(waterBool,winShape)
waterSum = slice_summer(slices,sShape)
waterArray[5:-5,4:-4] = np.where(((waterSum/99)*100)<=20,1,0) * np.where(((waterSum/99)*100)>=5,1,0) 

#slope
slope8Array = np.zeros(aShape)
slices,sShape = make_slices(slopeArray,winShape)
slopeSum = slice_summer(slices,sShape)
slope8Array[5:-5,4:-4] = np.where(((slopeSum/99))<8,1,0) 

model = slope8Array + waterArray + agArray + lidArray + greenArray
hiDev = np.where(nlcdArray==23,0,1) * np.where(nlcdArray==24,0,1)
outModel = model * hiDev

outRaster = arcpy.NumPyArrayToRaster(outModel.astype(int),llpt,cellSize,cellSize)
arcpy.management.DefineProjection(outRaster,crs)
outRaster.save('suite_suitability_vect.tif')

#print greenArray.sum()
#print agArray.sum()
#print lidArray.sum()
#print waterArray.sum()
#print slope8Array.sum()

print 'total suitable pixels:',np.where(outModel==5,1,0).sum()
print 'run time:', time.time() - ti
