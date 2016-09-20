import os
import sys
import time

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout,format='%(message)s')

import numpy as np # fundamental numeric operations package
import tomopy # tomographic reconstrcution package
import dxchange
import h5py

import glob
# =============================================================================
def list_from_txt(TextFilePath='../filepath/UnformatedFileList_Test.txt',comment='#'):
	"""
	Converts unformatted .txt file with \n separated file names into python list
	"""

	if '.py' in TextFilePath: # if file path is actually a python script, run script instead
		execfile(TextFilePath)
	else:
		textFile = open(TextFilePath,'r') # open text file
		data = textFile.readlines() #read lines of text into list of strings
		fileList = []
		for i in range(len(data)):
			data[i] = data[i].strip(" ") # remove spaces
			data[i]=data[i].strip("\n")  # remove returns
			if data[i][0] != comment:
				fileList.append(data[i]) # keep lines that are not commented
		return(fileList)

# =============================================================================

def list_h5_files(searchDir): 
	"""
	Finds all .h5 files in the search directory
	"""
	if searchDir[-1] == '/': 
		h5_list = glob.glob(searchDir+"*.h5"
	else:
		h5_list = glob.glob(searchDir+"/*.h5"
	return(h5_list)

# =============================================================================
NERSC_DefaultPath="/global/project/projectdirs/als/spade/warehouse/als/bl832/"
userDefault = "phosemann"

def NERSC_ArchivePath(filename,useraccount=userDefault,archivepath=NERSC_DefaultPath):
	'''
	Generates path to raw tomography projection data in NERSC Archives 
	Input list of file names, returns list of NERSC paths
	'''
	# Convert filename to list type if only one file name is given
	if type(filename) != list:
		filename=[filename]

	# Generate list of NERSC Paths from fileList
	pathOut=[]
	for i in range(len(filename)):
		#pathOut.append( archivepath +useraccount+ "/" + filename[i] + "/raw/" + filename[i]+".h5" )
		pathOut.append( archivepath +useraccount+ "/" + filename[i] + "/raw/")
	print pathOut
	return pathOut

# =============================================================================

def NERSC_StageData(filename,useraccount=userDefault):
	'''
	curl command sent to spot.nersc to stage data if stored on tape
	requires credentials. Run the following command
	> curl -k -c cookies.txt -X POST -d "username=[your_username]&password=[your_password]" https://portal-auth.nersc.gov/als/auth
	for more info: http://spot.nersc.gov/api.php
	'''
	# Convert filename to list type if only one file name is given
	if type(filename) != list:
		filename=[filename]	
	#EXAMPLE Command: curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/stageifneeded/als/bl832/phosemann/20160512_092220_tensile7_T700_240mic/raw/20160512_092220_tensile7_T700_240mic.h5"
	baseURL = "https://portal-auth.nersc.gov/als/hdf/stageifneeded/als/bl832/"
	curlCommand = "curl -k -b cookies.txt -X GET "
	for i in range(len(filename)):
		command_string = curlCommand + baseURL + useraccount +"/"+ filename[i]+"/raw/"+filename[i]+".h5"
		os.system(command_string)
		print(command_string)
		time.sleep(1)

# =============================================================================

def NERSC_RetreiveData(filename,destinationpath,useraccount=userDefault,archivepath=NERSC_DefaultPath):
	'''
	Downloads raw tomography projection data in NERSC from NERSC Archives 
	for a list of file names
	'''

	# Convert filename to list type if only one file name is given
	if type(filename) != list:
		filename=[filename]

	# Generate file paths and destination paths
	filePathIn = []
	filePathOut = []
	for i in range(len(filename)):
		print(archivepath,useraccount,filename[i])
		filePathIn.append( archivepath +useraccount+ "/" + filename[i] + "/raw/" + filename[i]+".h5" )
		filePathOut.append( destinationpath + filename[i] + ".h5")
	logging.info("file path list complete"); print filePathIn
	logging.info("destination path list complete"); print filePathOut
	
	# Copy Files to desintation
	for i in range(len(filename)):
		logging.info("begin transfer: "+filePathIn[i])
		os.system("cp " + filePathIn[i] + " " + filePathOut[i])
		logging.info("transfer complete: ")
