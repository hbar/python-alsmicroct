# python-TomographyTools

This repo contains python code for reconstructing and processing x-ray tomography datasets generated the advanced light source.

## Overview:
[Beamline 8.3.2][BL832] is located at the Advanced Light Source [(ALS)][ALS] at Lawrence Berkeley National Laboratory [(LBNL)][LBNL]. 8.3.2 is a synchrotron x-ray endstation that is devoted to x-ray microtomography. This repository provides a toolkit of useful tomography tools to process data produced by the x-ray tomography performed at 8.3.2.

Tomography analysis requires proessing of large (many GB) datasets that contain 32-bit image stacks. Standard raw datasets contain X-ray radiographs/images/projections) of a sample taken at many angles as the sample is rotated w.r.t. the imaging system. A tomographic reconstruction algorithm is used to convert the multiple views into a 3D dataset/imagestack. These python tools utilize the [TomoPy][TomoPy] libraries, deveoloped at Argon National Laboratory, to perform reconstructions. Additionally, postprocessing tools using numpy, scipy, and matplotlib libaries are included.

[LBNL]:http://www.lbl.gov/
[ALS]:https://www-als.lbl.gov/
[BL832]:http://microct.lbl.gov/
[TomoPy]:https://tomopy.readthedocs.io/en/latest/index.html

## About TomoPy:
[TomoPy][TomoPy] is an open-source Python package for tomographic data processing and image reconstruction. Anaconda is the prefered python distribution for using TomoPy it can be installed directly from TomoPy's [conda install channel][TomoPyConda]

[TomoPyConda]:https://anaconda.org/dgursoy/tomopy
