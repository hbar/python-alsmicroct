# functions for post processing datasets
import glob
import numpy as np
import os
from skimage import io
import skimage.external.tifffile as skTiff
import numexpr as ne # routines for the fast evaluation of array expressions elementwise by using a vector-based virtual machine
# =============================================================================

# generates list of all files in a directory with the desired extension
def get_fileList(filepath='./', extensions=("tif","tiff")):
    filepath = filepath.rstrip('/')
    fileList=[]
    for iExt in range(len(extensions)):
        searchterm = filepath+'/*.'+extensions[iExt]
        files = glob.glob(searchterm)
        fileList.extend(files)
    return(fileList)

# loads images in directory into a numpy array
def load_DataStack(filepath='./',imagerange=(1000,1100)):
    #Imports Tomography Dataset
    fileList = get_fileList(filepath)

    if imagerange=="all" or imagerange=="All" or imagerange=="ALL":
        imageMin = 0
        imageMax = len(fileList)
    else:
        imageMin = imagerange[0]
        imageMax = imagerange[1]

    image = io.imread(fileList[0])
    rows,cols = image.shape

    dataset = np.zeros((imageMax-imageMin,rows, cols))

    for iImage in range(imageMin,imageMax):
        dataset[iImage-imageMin,:,:] = io.imread(fileList[iImage])
        print(iImage)
    return dataset


def convert_DirectoryTo8Bit(inputpath='./', data_min=-10.0, data_max=10.0, outputpath=None,filename=None):

    fileList= get_fileList(inputpath)

    # Strip file extension, etc from first filename in list
    if filename == None:
        filename = fileList[0].split('/')[-1]
        filename = filename.rstrip('.tif')
        filename = filename.rstrip('0')
        filename = filename +"_8bit"

    if outputpath == None:
        outputpath = inputpath.rstrip('/') + "_8bit/"

    # create output directory if it does not exist
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)

    for iImage in range(len(fileList)):
        image32 = io.imread(fileList[iImage])
        image8 = convert8bit(image32,data_min,data_max)
        outputfilepath = outputpath.rstrip('/')+'/'+filename + '_' + '{:04d}'.format(iImage) + '.tiff'
        io.imsave(outputfilepath,image8)
        print(outputfilepath)
        #print(iImage)

    print("conversion complete")


def convert8bit(rec,data_min,data_max):
    rec = rec.astype(np.float32,copy=False)
    df = np.float32(data_max-data_min)
    mn = np.float32(data_min)
    scl = ne.evaluate('0.5+255*(rec-mn)/df',truediv=True)
    ne.evaluate('where(scl<0,0,scl)',out=scl)
    ne.evaluate('where(scl>255,255,scl)',out=scl)
    return scl.astype(np.uint8)

def save_TiffStack(dataset,filename="image",outputPath="./"):
    filename = filename.rstrip(".tiff")
    filename = filename.rstrip(".tif")
    outputFile = outputPath + filename + ".tiff"
    print("saving ... : " + outputFile)
    skTiff.imsave(outputFile,dataset)
    print("save complete: " + outputFile)

def convert_DirectoryToTiffStack(filepath='./'):
    pass

def convert_ArrayToDirectory(dataset,filename="image",outputPath="./"):
    pass

