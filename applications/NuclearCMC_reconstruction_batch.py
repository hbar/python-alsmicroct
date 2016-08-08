import reconstruction

execfile("../filepath/NuclearCMC_raw_data_file_list.py")

pathList = reconstruction.NERSC_ArchivePath(fileList)

outputPath = "/scratch1/scratchdirs/hbar/" #"/global/homes/h/hbar/NuclearReconOutput/"

reconstruction.reconstruct(fileList,inputPath=pathList,outputPath=outputPath)


