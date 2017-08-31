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

import getpass # allows commandline password input

import requests # tools for web requests/communication with online APIs



# Create spot session class
# This class includes all functions for authenticating and communcating with SPOT API

class spotSession():

# =============================================================================
# Login
	def __init__ (self):
		"""
		Prompts user for username and password
		"""
		self.URL_authentication = "https://portal-auth.nersc.gov/als/auth"

		spot_username = raw_input("username:")
		spot_password = getpass.getpass()

		s = requests.Session()
		r = s.get(self.URL_authentication)
		r = s.post(self.URL_authentication,{"username":spot_username,"password":spot_password})
		self.session = s
	"""
POST

URL:
https://portal-auth.nersc.gov/als/auth

EXAMPLE:

% curl -k -c cookies.txt -X POST -d "username=[your_username]&password=[your_password]" https://portal-auth.nersc.gov/als/auth

	"""

# =============================================================================
# Search Datasets

	def search(self,
		search,
		session=None,
		limitnum = 10, # number of results to show
		skipnum = 0, # number of results to skip
		sortterm = "fs.stage_date", # database field on which to sort (commonly fs.stage_date or appmetadata.sdate)
		sorttype = "desc"): # sorttype: desc or asc

		self.URL_search = "https://portal-auth.nersc.gov/als/hdf/search"
		self.PARAMS_search = {"limitnum": limitnum, "skipnum":skipnum, "sortterm": sortterm, "sorttype": sorttype, "search": search}
		r = self.session.get(url=self.URL_search,params=self.PARAMS_search)
		return r.json()


	"""
GET

URL:
https://portal-auth.nersc.gov/als/hdf/search

Arguments:
limitnum: number of results to show
skipnum: number of results to skip
sortterm: database field on which to sort (commonly fs.stage_date or appmetadata.sdate)
sorttype: desc or asc
search: query

Result:
JSON List

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/search?skipnum=0&limitnum=10&sortterm=fs.stage_date&sorttype=desc&search=end_station=bl832"

	"""

# =============================================================================
# Find Derived Datasets (norm, sino, gridrec, imgrec) from raw dataset

	def derived_datasets(self,dataset):
		
		self.URL_DerivedDatasets = "https://portal-auth.nersc.gov/als/hdf/dataset"
		self.PARAMS_DerivedDatasets = {"dataset":dataset}

		r = self.session.get(self.URL_DerivedDatasets,params=self.PARAMS_DerivedDatasets)

		return r.json()

"""
GET

URL:
https://portal-auth.nersc.gov/als/hdf/dataset

Arguments:
dataset: raw dataset

Result:
JSON List

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/dataset?dataset=20130713_185717_Chilarchaea_quellon_F_9053427_IKI_"

"""


# =============================================================================
# View Attributes for Single Dataset and Image Within Dataset

	def spot_attributes(self.dataset):

		self.URL_attributes = "https://portal-auth.nersc.gov/als/hdf/attributes/"

		r = session.get(self.URL_attributes + dataset,{"group":"/"})

		return r.json()

	"""
GET

URL:
https://portal-auth.nersc.gov/als/hdf/attributes/[dataset]

Arguments:
group: path in hdf5 file. Set to "/" for overall attributes

Result:
JSON Array

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/attributes/als/bl832/hmwood/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/raw/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_.h5?group=/"

	"""


# =============================================================================
# List Images Within Dataset

"""
 GET

URL:
https://portal-auth.nersc.gov/als/hdf/listimages/[dataset]

Arguments:
None

Result:
JSON List (paths to images within the HDF5 file)

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/listimages/als/bl832/hmwood/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/raw/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_.h5"

"""

# =============================================================================
# Stage Dataset From Tape to Disk if Required

"""
 GET

URL:
https://portal-auth.nersc.gov/als/hdf/stageifneeded/[dataset]

Arguments:
None

Result:
JSON Array

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/stageifneeded/als/bl832/hmwood/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/raw/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_.h5"

"""

# =============================================================================
# Download Dataset

"""
 GET

URL:
https://portal-auth.nersc.gov/als/hdf/download/[dataset]

Arguments:
None

Result:
H5 File

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/download/als/bl832/hmwood/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/raw/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_.h" > file.h5

"""



# =============================================================================
# Download Rawdata For Individual Image

"""
 GET

URL:
https://portal-auth.nersc.gov/als/hdf/rawdata/[dataset]

Arguments:
group: path in HDF5 file to image

Result:
JSON Array

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/rawdata/als/bl832/hmwood/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/norm/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_-norm-20130714_192637.h5?group=/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/20130713_185717_Chilarchaea_quellon_F_9053427_IKI__0000_0640.tif"

"""


# =============================================================================
# Get Download URLs for .tif and .png files for individual image

"""
 GET

URL:
https://portal-auth.nersc.gov/als/hdf/image/[dataset]

Arguments:
group: path in HDF5 file to image

Result:
JSON Array

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/image/als/bl832/hmwood/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/norm/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_-norm-20130714_192637.h5?group=/20130713_185717_Chilarchaea_quellon_F_9053427_IKI_/20130713_185717_Chilarchaea_quellon_F_9053427_IKI__0000_0640.tif"

"""



# =============================================================================
# Run TomoPy on an existing dataset

"""
 GET

URL:
https://portal-auth.nersc.gov/als/hdf/tomopyjob

Arguments:
dataset: raw dataset

Result:
JSON List

EXAMPLE:

% curl -k -b cookies.txt -X GET "https://portal-auth.nersc.gov/als/hdf/tomopyjob?dataset=20130713_185717_Chilarchaea_quellon_F_9053427_IKI_"

"""



# =============================================================================
#

"""
Older functions below
"""

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
		h5_list = glob.glob(searchDir+"*.h5")
	else:
		h5_list = glob.glob(searchDir+"/*.h5")
	return(h5_list)

# =============================================================================
NERSC_DefaultPath="/global/project/projectdirs/als/spade/warehouse/als/bl832/"
userDefault = "hsbarnard"

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

def NERSC_RetreiveData(filename,
	destinationpath,
	useraccount=userDefault,
	archivepath=NERSC_DefaultPath):

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



