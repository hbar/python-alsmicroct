import sys
sys.path.append('../')

from TomographyTools import *

execfile("../filepath/NuclearCMC_raw_data_file_list.py")

pathList = data_management.NERSC_ArchivePath(fileList)

outputPath = "/scratch1/scratchdirs/hbar/" #"/global/homes/h/hbar/NuclearReconOutput/"

reconstruction.reconstruct(fileList,inputPath=pathList,outputPath=outputPath)


