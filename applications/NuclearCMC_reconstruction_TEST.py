#NERSC_recon_TEST.py
import reconstruction

execfile("/global/homes/h/hbar/NuclearCMC_raw_data_file_list.py")

pathList = reconstruction.NERSC_ArchivePath(fileList)

outputPath = "/scratch1/scratchdirs/hbar/TestOutput/" #"/global/homes/h/hbar/NuclearReconOutput/"

reconstruction.reconstructMPI(fileList,inputPath=pathList,outputPath=outputPath)

