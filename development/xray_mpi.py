from __future__ import print_function, division

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import numpy as np
import os
import time
import tomopy
import dxchange
from mpiarray import MpiArray

import logging

#NOTE: basicConfig ignored when using IPython
if rank == 0:
    logging.basicConfig(#filename='radon.log',
                        format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s',
                        level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

working_dir = "/mnt/ssd0/xray/20151216_APS_32ID/rs64_5X_9200eV_2s"
filename = 'rs64_241proj_5X_9200eV_2_.h5'

os.chdir(working_dir)
start = time.time()

# Read HDF5 file.
logger.info("Reading data from H5 file %s" % filename)
#TODO: read directly into different mpi processes
if rank == 0:
    # read data into root node
    proj, flat, dark, theta = dxchange.read_aps_32id(filename, dtype=np.float32)
else:
    proj, flat, dark, theta = None, None, None, None

# create MpiArray from Proj data
proj = MpiArray.fromglobalarray(proj)
proj.scatter(0)
proj.arr = None # remove full array to save memory

# share flats, darks, and theta to all MPI nodes
flat = comm.bcast(flat, root=0)
dark = comm.bcast(dark, root=0)
theta = comm.bcast(theta, root=0)

# Flat field correct data
logger.info("Flat field correcting data")
proj.scatter(0)
tomopy.normalize(proj.local_arr, flat, dark, ncore=1, out=proj.local_arr)
np.clip(proj.local_arr, 1e-6, 1.0, proj.local_arr)
del flat, dark

# Remove Stripe
# NOTE: we need to change remove_strip_fw to take sinogram order data, since it internally rotates the data
#proj.scatter(1)
#proj.local_arr = tomopy.remove_stripe_fw(proj.local_arr, ncore=1)

# Take the minus log to prepare for reconstruction
#NOTE: no scatter required since minus_log doesn't care about order
tomopy.minus_log(proj.local_arr, ncore=1, out=proj.local_arr)

# Find rotation center per set of sinograms
logger.info("Finding center of rotation")
proj.scatter(1)
# NOTE: center finding doesn't work for my datasets :-(
#center = tomopy.find_center(proj.local_arr, theta, sinogram_order=True)
center = proj.shape[2] // 2
logger.info("Center for sinograms [%d:%d] is %f" % (proj.offset, proj.offset+proj.size, center))

alg = 'gridrec'
logger.info("Reconstructing using: %s" % alg)
# Reconstruct object using algorithm
proj.scatter(1)
rec = tomopy.recon(proj.local_arr,
                   theta,
                   center=center,
                   algorithm=alg,                           
                   sinogram_order=True,
                   ncore=1)
logger.info("Writing result to file")
dxchange.write_tiff_stack(rec, fname='%s(mpi)/recon' % (alg), start=proj.offset, overwrite=True)

logger.info("Done in %0.2f seconds"%(time.time() - start))

