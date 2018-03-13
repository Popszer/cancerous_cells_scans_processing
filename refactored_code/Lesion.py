# coding=utf-8

###
# Lesion.py -
# This file contains the definition of class Lesion used to process patients lesions (mask and features
# values associated to a lesion. Lesion.py also implements handy function to process the building of a mask (combining
# pile of file, majority vote, etc.
#
# Author : François Paupier - francois.paupier@gmail.com
#
# Created on : 16/02/2018
###

import numpy as np
import os
import re
from skimage.external import tifffile
import SimpleITK as sitk
from skimage import io
import collections


# --------------------------
# Lesion class definition
# --------------------------

class Lesion:

    def __init__(self, ref, masksPath):
        ''' Provide ref number as string "lx", where x is the number of the lesion, masksPath is the path to the folder
        containing the masks '''
        self.ref = ref
        self.mask = majorityVote(masksPath)
        self.dict_features = collections.OrderedDict()  # Expected features are in the .yaml parameter file


# --------------------------
# Set of functions used handle binary mask creation
# --------------------------

def getWords(text):
    '''From a text input as a string, get the words separated by a space and return it as a list of strings'''
    return re.compile('\w+').findall(text)


def makeTifFromPile(pathToPile):
    '''Takes an absolute path containing a pile of masks, compute the resulting .tif mask and
     output the path to the created .tif mask'''
    list_pileFiles = []
    for dirpath, dirnames, fileNames in os.walk(pathToPile):
        for fileName in fileNames:
            if not fileName.startswith('.'):
                list_pileFiles.append(os.path.join(dirpath, fileName))

    first_file = list_pileFiles[0]
    # get the shape of the image
    with open(first_file, mode='r', encoding='utf-8') as tifFile:
        tifFile.readline()  # first line is junk data
        shapeLocalMask = getWords(tifFile.readline())  # second line of raw tif is shape of the dcm pile
        xShape = int(shapeLocalMask[0])
        yShape = int(shapeLocalMask[1])

    num_file = len(list_pileFiles)
    mask_array = np.zeros((num_file, xShape, yShape))
    fileIndex = num_file - 1
    for pileFile in list_pileFiles:
        with open(pileFile, mode='r', encoding='utf-8') as tifFile:
            tifFile.readline()  # junk line
            tifFile.readline()  # second line is shape of the dcm pile
            tifFile.readline()  # 3 line is junk data
            for rowIndex in range(xShape):
                for colIndex in range(yShape):
                    val = tifFile.read(1)
                    while val != '0' and val != '1':
                        val = tifFile.read(1)
                    mask_array[fileIndex, rowIndex, colIndex] = int(val)
            fileIndex = fileIndex - 1  # Start with last file in the pile to construct the mask in correct order

    pathToLesion = os.path.abspath(os.path.join(pathToPile, os.pardir))

    pathToTifMask = os.path.join(pathToLesion, '_non-standard-mask.tif') # In case not 2.5 or 40 mask (non nominal path)
    if '2.5' in pathToPile:
        pathToTifMask = os.path.join(pathToLesion, '25.tif')
    if '40' in pathToPile:
        pathToTifMask = os.path.join(pathToLesion, '40.tif')

    # Warning : check why the size (in bytes) of the saved mask is up to 10 times the size of the 2.5 or 40 masks
    tifffile.imsave(pathToTifMask, mask_array)
    return pathToTifMask


def getTifMasks(masksPath):
    '''Return path toward the KMean, 40 and 2.5 mask respectively in this order'''
    list_files = [file for file in os.listdir(masksPath) if os.path.isfile(os.path.join(masksPath, file))]
    mask40Name = '40.tif'
    mask25Name = '25.tif'
    pathToKmeanMask = os.path.join(masksPath, "kmean.tif")
    if mask40Name in list_files:
        pathTo40Mask = os.path.join(masksPath, mask40Name)
    else:
        pathTo40Mask = makeTifFromPile(os.path.join(masksPath, "40"))
    if mask25Name in list_files:
        pathTo25Mask = os.path.join(masksPath, mask25Name)
    else:
        pathTo25Mask = makeTifFromPile(os.path.join(masksPath, '2.5'))
    return(pathToKmeanMask, pathTo40Mask, pathTo25Mask)


def majorityVote(masksPath):
    '''Compute the average mask based on the majority vote method for a lesion. Masks used to compute resulting masks 
    are Kmean mask, 2.5 mask and 40% mask. The masks should be in the same path. The resulting tif mask is saved under 
    the masksPath directory under the name 'majority.tif' '''

    # Import the 3 masks
    (pathToKmeanMask, pathTo40Mask, pathTo25Mask) = getTifMasks(masksPath)
    mkmean = io.imread(pathToKmeanMask).T
    m25 = io.imread(pathTo40Mask).T
    m40 = io.imread(pathTo25Mask).T

    # Parameters
    thresh = 0.33  # threshold value for accepting a voxel as belonging in the resulting majority vote mask
    nbMethods = 3  # Number of methods used (40%, 2.5 and kmean)

    # Dimensions
    imageDims = mkmean.shape

    # TODO: For some patients the masks provided have wrong dimensions. In such a case only the kmean (which is supposed to
    # have the same dimension as the image is outputted as the resulting mask. This is purely arbitrary and shal be
    # change in favor of a more robust solution.
    masksAreSameSize = mkmean.shape == m25.shape == m40.shape

    # Initialize resulting matrix
    mMajority = np.zeros(imageDims)
    if masksAreSameSize:
        sum_mask = m40 + m25 + mkmean
        sum_mask = np.divide(sum_mask, nbMethods)
        mMajority[sum_mask >= thresh] = 1  # Vectorized method
    else:
        mMajority[mkmean >= 1] = 1
    sITK_mask = sitk.GetImageFromArray(mMajority)

    majorityTiffPath = os.path.join(masksPath, "majority.tif")
    tifffile.imsave(majorityTiffPath, mMajority)

    return sITK_mask