# python-TomographyTools

This repo contains python code for reconstructing and processing x-ray tomography datasets generated the advanced light source.

## Overview:
[Beamline 8.3.2][BL832] is located at the Advanced Light Source [(ALS)][ALS] at Lawrence Berkeley National Laboratory [(LBNL)][LBNL]. 8.3.2 is a synchrotron x-ray endstation that is devoted to x-ray microtomography. This repository provides a toolkit for reconstruction and processing data produced by the x-ray tomography performed at 8.3.2.

Tomography analysis requires proessing of large (many GB) datasets that contain 32-bit image stacks. Standard raw datasets contain X-ray radiographs/images/projections) of a sample taken at many angles as the sample is rotated w.r.t. the imaging system. A tomographic reconstruction algorithm is used to convert the multiple views into a 3D dataset/imagestack. These python tools utilize the [TomoPy][TomoPy] libraries, deveoloped at Argon National Laboratory, to perform reconstructions. Additionally, postprocessing tools using numpy, scipy, and matplotlib libaries are included.

[LBNL]:http://www.lbl.gov/
[ALS]:https://www-als.lbl.gov/
[BL832]:http://microct.lbl.gov/
[TomoPy]:https://tomopy.readthedocs.io/en/latest/index.html

## About TomoPy:
[TomoPy][TomoPy] is an open-source Python package for tomographic data processing and image reconstruction. Anaconda is the prefered python distribution for using TomoPy it can be installed directly from TomoPy's [conda channel][TomoPyConda].

[TomoPyConda]:https://anaconda.org/dgursoy/tomopy

## Repo File Structure

`lib/` contains functions and classes used for data analysis


`applications/` contains programs that utilize functions from lib and TomoPy.

`filepath/` contains input files that provide lists of paths the datasets that are to be reconstructed or processed.

`batch/` contains .slurm scripts that are used to submit jobs to the [NERSC] supercomputer.

[NERSC]: http://www.nersc.gov/



### SPOT Suite API Commands

SPOT Suite is an online platform for storage and datamanagement of ALS data on NERSC. In this library commands commands and data requests can be sent to the SPOT API using functions contained in a class called `spotSession`. This class utilizes python's `requests` library to communicate with the API. This class is available in `TomographyTools.data_management` toolkit.

#### `SpotSession(username='default')`

Creating an instance of the `SpotSession()` class establishes a session with the SPOT API. The user will be prompted for username and password

`username` will default to your spot username, however, you can enter a different username if you are not the owner of the dataset you will request. You will permission to access data for which are not the owner.

```
import sys
sys.path.append("[local path]/python-TomographyTools")
import TomographyTools.data_management as dm

s = dm.SpotSession()
```

##### `SpotSession()` built in functions:


`check_authentication()` returns True if authentication is active

`authentication()` prompts user for username and password for current session and reconnects.

```
search(query,                        # input search string
	limitnum = 10,               # number of results to show
	skipnum = 0,                 # number of results to skip
	sortterm = "fs.stage_date",  # database field on which to sort
	sorttype = "desc")           # sorttype: desc or asc
```
Searches for filenames containing `query` string


`derived_datasets(self,dataset)` Finds derived datasets (norm, sino, gridrec, imgrec) from raw dataset. Returns `json` type object



`attributes(self,dataset,username='default)` Requests metadata for dataset.

`stage(self,dataset,username='default')` Stage dataset from tape to disk if required (data is stored long term on tape drives and must be transferred to disk for use). 

```
download(dataset,			# Name of dataset
	username='default',		# username of dataset owner, defaults to spot login username
	downloadPath='default',		# download destination, defaults to pwd
	downloadName='default')		# download name filename, defaults to name of dataset
```
Downloads raw dataset from SPOT
