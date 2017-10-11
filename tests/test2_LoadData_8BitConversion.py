import sys
#sys.path.append("C:/Users/hsbarnard/Dropbox/Research(LBL)/python-TomographyTools")
sys.path.append("/home/hsbarnard@als.lbl.gov/data-scratch/python/python-TomographyTools/")

import skimage as sk
from skimage.viewer import ImageViewer

#import TomographyTools as tt
#import TomographyTools.data_management as dm
#import TomographyTools.reconstruciton as rn
import TomographyTools.image_processing as ip

inputDir = "/home/hsbarnard@als.lbl.gov/data-scratch/20171006_ChaiLor_PaintData/rec20171005_162920_TiO2_sample1/"

inputDirs = ['/home/hsbarnard@als.lbl.gov/data-scratch/20171006_ChaiLor_PaintData/rec20171005_155036_TiO2_control_scan2',
    "/home/hsbarnard@als.lbl.gov/data-scratch/20171006_ChaiLor_PaintData/rec20171005_162920_TiO2_sample1/",
    '/home/hsbarnard@als.lbl.gov/data-scratch/20171006_ChaiLor_PaintData/rec20171005_165313_TiO2_sample2',
    '/home/hsbarnard@als.lbl.gov/data-scratch/20171006_ChaiLor_PaintData/rec20171005_172237_TiO2_sample3']

if True:
    ip.convert_DirectoryTo8Bit(inputpath=inputDirs[0],data_min=-5.0,data_max=7.0)
    ip.convert_DirectoryTo8Bit(inputpath=inputDirs[1],data_min=-5.0,data_max=7.0)
    ip.convert_DirectoryTo8Bit(inputpath=inputDirs[2],data_min=-5.0,data_max=7.0)
    ip.convert_DirectoryTo8Bit(inputpath=inputDirs[3],data_min=-5.0,data_max=7.0)

if False:
    imageStack = ip.loadDataStack(inputDir)
    imageStack8Bit = ip.convert8bit(imageStack,-5.0,7.0)

    ip.saveTiffStack(imageStack,filename="testStack_8Bit")

    image = imageStack8Bit[:,:,50]
    viewer = ImageViewer(image); viewer.show()
