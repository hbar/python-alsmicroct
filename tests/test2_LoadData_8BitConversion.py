import sys
#sys.path.append("C:/Users/hsbarnard/Dropbox/Research(LBL)/python-TomographyTools")
sys.path.append("/home/hsbarnard@als.lbl.gov/data-scratch/python/python-TomographyTools/")

#import TomographyTools as tt
#import TomographyTools.data_management as dm
#import TomographyTools.reconstruciton as rn
import TomographyTools.image_processing as ip

inputDir = "/home/hsbarnard@als.lbl.gov/data-scratch/rec20171005_155036_TiO2_control_scan2/"

fileList = ip.loadDataSet(inputDir)

