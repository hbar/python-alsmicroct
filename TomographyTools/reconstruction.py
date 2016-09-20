# -*- coding: utf-8 -*-

import os
import sys
import time
from mpi4py import MPI # message passing interface (MPI) for parallel computing

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout,format='%(message)s')

import numpy as np # fundamental numeric operations package
import tomopy # tomographic reconstrcution package
import dxchange
import h5py

# =============================================================================
def read_als_832h5_metadata(fname):
	"""
	Read metadata in ALS 8.3.2 hdf5 dataset files
	:param fname: str, Path to hdf5 file.
	:return dict: dictionary of metadata items
	"""

	fdata, gdata = {}, {}

	with h5py.File(fname, 'r') as f:
		fdata = dict(f.attrs)
		g = _find_dataset_group(f)
		gdata = dict(g.attrs)

	return fdata, gdata

#------------------------------------------------------------------------------
def _find_dataset_group(h5object):
	"""
	Finds the group name containing the stack of projections datasets within
	a ALS BL8.3.2 hdf5 file
	"""
	# Only one root key means only one dataset in BL8.3.2 current format
	keys = h5object.keys()
	if len(keys) == 1:
		if isinstance(h5object[keys[0]], h5py.Group):
			group_keys = h5object[keys[0]].keys()
			if isinstance(h5object[keys[0]][group_keys[0]], h5py.Dataset):
				return h5object[keys[0]]
			else:
				return _find_dataset_group(h5object[keys[0]])
		else:
			raise Exception('Unable to find dataset group')
	else:
		raise Exception('Unable to find dataset group')

#------------------------------------------------------------------------------
def get_interleaved_indices(mdata):
    """
    Return the indices within tomography projection dataset where bright fields where taken
    """
    i0 = int(mdata['i0cycle'])
    nproj = int(mdata['nangles'])
    if i0 > 0:
        indices = list(range(0, nproj, i0))
        if indices[-1] != nproj - 1:
            indices.append(nproj - 1)
    elif i0 == 0:
        indices = [0, nproj - 1]
    return indices

#------------------------------------------------------------------------------
def sino_360_to_180(data, overlap=0, rotation='left'):
	"""
	Converts 0-360 degrees sinogram to a 0-180 sinogram.
	
	Parameters
	----------
	data : ndarray
		Input 3D data.
	overlap : scalar, optional
		Overlapping number of pixels.
	rotation : string, optional
		Left if rotation center is close to the left of the
		field-of-view, right otherwise.
	Returns
	-------
	ndarray
	Output 3D data.
	"""
	
	dx, dy, dz = data.shape

	lo = overlap//2
	ro = overlap - lo
	n = dx//2

	out = np.zeros((n, dy, 2*dz-overlap), dtype=data.dtype)

	if rotation == 'left':
		out[:, :, -(dz-lo):] = data[:n, :, lo:]
		out[:, :, :-(dz-lo)] = data[n:2*n, :, ro:][:, :, ::-1]
	elif rotation == 'right':
		out[:, :, :dz-lo] = data[:n, :, :-lo]
		out[:, :, dz-lo:] = data[n:2*n, :, :-ro][:, :, ::-1]

	return out

# ==== RECONSTRUCTION CODE ====================================================s

# default inputs for reconstruction

COR = [] # set this as list of Centers of rotation for each dataset, if COR is negative or boolean False, auto COR will be used for the dataset
doOutliers = True
outlier_diff = 1000
outlier_size = 3

# default ring removal parameters
doFWringremoval = False
ringSigma = 4
ringLevel = 8
ringWavelet = 'db5'

pad_sino = True

# default phase retreieval parameters
doPhaseRetrieval = False
propagation_dist = 10
kev = 20
alphaReg = 0.0003

butterworthpars = [.25,2]

doPolarRing = True
Rarc=30
Rmaxwidth=30
Rtmax=3000.0
Rthr=3000.0
Rtmin=-1000.0

useAutoCOR = False # use auto COR on all

use360to180 = False

recon_slice = False # input True for center slice, input slice number for specific slice

#num_sino_per_substack = 270
num_substacks = 10

def reconstruct(filename,inputPath="", outputPath="", COR=COR, doOutliers=doOutliers, outlier_diff=outlier_diff, outlier_size=outlier_size, doFWringremoval=doFWringremoval, ringSigma=ringSigma,ringLevel=ringLevel, ringWavelet=ringWavelet,pad_sino=pad_sino,  doPhaseRetrieval=doPhaseRetrieval, propagation_dist=propagation_dist, kev=kev,alphaReg=alphaReg, butterworthpars=butterworthpars, doPolarRing=doPolarRing,Rarc=Rarc, Rmaxwidth=Rmaxwidth, Rtmax=Rtmax, Rthr=Rthr, Rtmin=Rtmin, useAutoCOR=useAutoCOR, use360to180=use360to180, num_substacks=num_substacks,recon_slice=recon_slice):

	# Convert filename to list type if only one file name is given
	if type(filename) != list:
		filename=[filename]

	# If useAutoCor == true, a list of COR will be automatically calculated for all files
	# If a list of COR is given, only entries with boolean False will use automatic COR calculation
	if useAutoCOR==True or (len(COR) != len(filename)):
		logging.info('using auto COR for all input files')
		COR = [False]*len(filename)

	for x in range(len(filename)):
		logging.info('opening data set, checking metadata')

		fdata, gdata = read_als_832h5_metadata(inputPath[x]+filename[x]+'.h5')
		pxsize = float(gdata['pxsize'])/10.0 # convert from metadata (mm) to this script (cm)
		numslices = int(gdata['nslices'])

		# recon_slice == True, only center slice will be reconstructed
		# if integer is given, a specific 		
		if recon_slice != False:
			if (type(recon_slice) == int) and (recon_slice <= numslices):
				sinorange [recon_slice-1, recon_slice]
			else:
				sinorange = [numslices//2-1, numslices//2]
		else:
			sinorange = [0, numslices]

		# Calculate number of substacks (chunks)
		substacks = num_substacks #(sinorange[1]-sinorange[0]-1)//num_sino_per_substack+1

		if (sinorange[1]-sinorange[0]) >= substacks:
			num_sino_per_substack = (sinorange[1]-sinorange[0])//num_substacks
		else:
			num_sino_per_substack = 1

	
		firstcor, lastcor = 0, int(gdata['nangles'])-1
		projs, flat, dark, floc = dxchange.read_als_832h5(inputPath[x]+filename[x]+'.h5', ind_tomo=(firstcor, lastcor))
		projs = tomopy.normalize_nf(projs, flat, dark, floc)
		autocor = tomopy.find_center_pc(projs[0], projs[1], tol=0.25)


		if (type(COR[x]) == bool) or (COR[x]<0) or (COR[x]=='auto'):
			firstcor, lastcor = 0, int(gdata['nangles'])-1
			projs, flat, dark, floc = dxchange.read_als_832h5(inputPath[x]+filename[x]+'.h5', ind_tomo=(firstcor, lastcor))
			projs = tomopy.normalize_nf(projs, flat, dark, floc)
			cor = tomopy.find_center_pc(projs[0], projs[1], tol=0.25)
		else:
			cor = COR[x]

		logging.info('Dataset %s, has %d total slices, reconstructing slices %d through %d in %d substack(s), using COR: %f',filename[x], int(gdata['nslices']), sinorange[0], sinorange[1]-1, substacks, cor)
		
		for y in range(0, substacks):
			logging.info('Starting dataset %s (%d of %d), substack %d of %d',filename[x], x+1, len(filename), y+1, substacks)

			logging.info('Reading sinograms...')
			projs, flat, dark, floc = dxchange.read_als_832h5(inputPath[x]+filename[x]+'.h5', sino=(sinorange[0]+y*num_sino_per_substack, sinorange[0]+(y+1)*num_sino_per_substack, 1)) 

			logging.info('Doing remove outliers, norm (nearest flats), and -log...')
			if doOutliers:
				projs = tomopy.remove_outlier(projs, outlier_diff, size=outlier_size, axis=0)
				flat = tomopy.remove_outlier(flat, outlier_diff, size=outlier_size, axis=0)
			tomo = tomopy.normalize_nf(projs, flat, dark, floc)
			tomo = tomopy.minus_log(tomo, out=tomo) # in place logarithm 
		
			# Use padding to remove halo in reconstruction if present
			if pad_sino:
				npad = int(np.ceil(tomo.shape[2] * np.sqrt(2)) - tomo.shape[2])//2
				tomo = tomopy.pad(tomo, 2, npad=npad, mode='edge')
				cor_rec = cor + npad # account for padding
			else:
				cor_rec = cor
		
			if doFWringremoval:
				logging.info('Doing ring (Fourier-wavelet) function...')
				tomo = tomopy.remove_stripe_fw(tomo, sigma=ringSigma, level=ringLevel, pad=True, wname=ringWavelet)		

			if doPhaseRetrieval:
				logging.info('Doing Phase retrieval...')
				#tomo = tomopy.retrieve_phase(tomo, pixel_size=pxsize, dist=propagation_dist, energy=kev, alpha=alphaReg, pad=True)	
				tomo = tomopy.retrieve_phase(tomo, pixel_size=pxsize, dist=propagation_dist, energy=kev, alpha=alphaReg, pad=True)		

			logging.info('Doing recon (gridrec) function and scaling/masking, with cor %f...',cor_rec)
			rec = tomopy.recon(tomo, tomopy.angles(tomo.shape[0], 270, 90), center=cor_rec, algorithm='gridrec', filter_name='butterworth', filter_par=butterworthpars)
			#rec = tomopy.recon(tomo, tomopy.angles(tomo.shape[0], 180+angularrange/2, 180-angularrange/2), center=cor_rec, algorithm='gridrec', filter_name='butterworth', filter_par=butterworthpars)		
			rec /= pxsize  # intensity values in cm^-1
			if pad_sino:
				rec = tomopy.circ_mask(rec[:, npad:-npad, npad:-npad], 0)
			else:
				rec = tomopy.circ_mask(rec, 0, ratio=1.0, val=0.0)
			
			if doPolarRing:
				logging.info('Doing ring (polar mean filter) function...')
				rec = tomopy.remove_ring(rec, theta_min=Rarc, rwidth=Rmaxwidth, thresh_max=Rtmax, thresh=Rthr, thresh_min=Rtmin)

			logging.info('Writing reconstruction slices to %s', filename[x])
			#dxchange.write_tiff_stack(rec, fname=outputPath+'alpha'+str(alphaReg)+'/rec'+filename[x]+'/rec'+filename[x], start=sinorange[0]+y*num_sino_per_substack)
			dxchange.write_tiff_stack(rec, fname=outputPath + 'recon_'+filename[x]+'/recon_'+filename[x], start=sinorange[0]+y*num_sino_per_substack)
		logging.info('Reconstruction Complete: '+ filename[x])


"""
#==============================================================================
# Reconstruct function with MPI Modifications
#==============================================================================
def reconstructMPI(filename,inputPath="", outputPath="", COR=COR, doOutliers=doOutliers, outlier_diff=outlier_diff, outlier_size=outlier_size, doFWringremoval=doFWringremoval,ringSigma=ringSigma,ringLevel=ringLevel,ringWavelet=ringWavelet,pad_sino=pad_sino,doPhaseRetrieval=doPhaseRetrieval,propagation_dist=propagation_dist,kev=kev,alphaReg=alphaReg,butterworthpars=butterworthpars,doPolarRing=doPolarRing,Rarc=Rarc,Rmaxwidth=Rmaxwidth,Rtmax=Rtmax,Rthr=Rthr,Rtmin=Rtmin,useAutoCOR=useAutoCOR,use360to180=use360to180,num_substacks=num_substacks):
	# get MPI rank for process
 	comm = MPI.COMM_WORLD
	rank = comm.Get_rank()
	# Convert filename to list type if only one file name is given
	if type(filename) != list:
		filename=[filename]
	# If useAutoCor is true, list of COR will be generated with boolean False for entries, this will initiate autoCOR for every dataset
	if useAutoCOR==True or (len(COR) != len(filename)):
		logging.info('using auto COR for all input files')
		COR = [False]*len(filename)
	for x in range(len(filename)):
		logging.info('opening data set, checking metadata')
		fdata, gdata = read_als_832h5_metadata(inputPath[x]+filename[x]+'.h5')
		pxsize = float(gdata['pxsize'])/10.0 # convert from metadata (mm) to this script (cm)
		sinorange = [0, int(gdata['nslices'])]
		num_sino_per_substack = num_sino_per_substack
		#sinorange = [975, 1025]
		#num_sino_per_substack = 50
		substacks = (sinorange[1]-sinorange[0])/num_sino_per_substack
	
		firstcor, lastcor = 0, int(gdata['nangles'])-1
		projs, flat, dark, floc = dxchange.read_als_832h5(inputPath[x]+filename[x]+'.h5', ind_tomo=(firstcor, lastcor))
		projs = tomopy.normalize_nf(projs, flat, dark, floc)
		autocor = tomopy.find_center_pc(projs[0], projs[1], tol=0.25)
		if (type(COR[x]) == bool) or (COR[x]<0) or (COR[x]=='auto'):
			firstcor, lastcor = 0, int(gdata['nangles'])-1
			projs, flat, dark, floc = dxchange.read_als_832h5(inputPath[x]+filename[x]+'.h5', ind_tomo=(firstcor, lastcor))
			projs = tomopy.normalize_nf(projs, flat, dark, floc)
			cor = tomopy.find_center_pc(projs[0], projs[1], tol=0.25)
		else:
			cor = COR[x]
		logging.info('Dataset %s, has %d total slices, reconstructing slices %d through %d in %d substack(s), using COR: %f',filename[x], int(gdata['nslices']), sinorange[0], sinorange[1]-1, substacks, cor)
		
		for y in range(0, substacks):
			if (rank == y):
				logging.info('Starting dataset %s (%d of %d), substack %d of %d',filename[x], x+1, len(filename), y+1, substacks)
				logging.info('Reading sinograms...')
				projs, flat, dark, floc = dxchange.read_als_832h5(inputPath[x]+filename[x]+'.h5', sino=(sinorange[0]+y*num_sino_per_substack, sinorange[0]+(y+1)*num_sino_per_substack, 1)) 
				logging.info('Doing remove outliers, norm (nearest flats), and -log...')
				if doOutliers:
					projs = tomopy.remove_outlier(projs, outlier_diff, size=outlier_size, axis=0)
					flat = tomopy.remove_outlier(flat, outlier_diff, size=outlier_size, axis=0)
				tomo = tomopy.normalize_nf(projs, flat, dark, floc)
				tomo = tomopy.minus_log(tomo, out=tomo) # in place logarithm 
			
				# Use padding to remove halo in reconstruction if present
				if pad_sino:
					npad = int(np.ceil(tomo.shape[2] * np.sqrt(2)) - tomo.shape[2])//2
					tomo = tomopy.pad(tomo, 2, npad=npad, mode='edge')
					cor_rec = cor + npad # account for padding
				else:
					cor_rec = cor
			
				if doFWringremoval:
					logging.info('Doing ring (Fourier-wavelet) function...')
					tomo = tomopy.remove_stripe_fw(tomo, sigma=ringSigma, level=ringLevel, pad=True, wname=ringWavelet)		
				if doPhaseRetrieval:
					logging.info('Doing Phase retrieval...')
					tomo = tomopy.retrieve_phase(tomo, pixel_size=pxsize, dist=propagation_dist, energy=kev, alpha=alphaReg, pad=True)	
					
				logging.info('Doing recon (gridrec) function and scaling/masking, with cor %f...',cor_rec)
				rec = tomopy.recon(tomo, tomopy.angles(tomo.shape[0], 270, 90), center=cor_rec, algorithm='gridrec', filter_name='butterworth', filter_par=butterworthpars)
				#rec = tomopy.recon(tomo, tomopy.angles(tomo.shape[0], 180+angularrange/2, 180-angularrange/2), center=cor_rec, algorithm='gridrec', filter_name='butterworth', filter_par=butterworthpars)		
				rec /= pxsize  # intensity values in cm^-1
				if doPolarRing:  # Apply polar ring filter
					logging.info('Doing ring (polar mean filter) function...')
					rec = tomopy.remove_ring(rec, theta_min=Rarc, rwidth=Rmaxwidth, thresh_max=Rtmax, thresh=Rthr, thresh_min=Rtmin)
				if pad_sino: # Un-pad sinogram
					rec = tomopy.circ_mask(rec[:, npad:-npad, npad:-npad], 0)
				else:
					rec = tomopy.circ_mask(rec, 0, ratio=1.0, val=0.0)
			
				logging.info('Writing reconstruction slices to %s', filename[x])
				#dxchange.write_tiff_stack(rec, fname=outputPath+'alpha'+str(alphaReg)+'/rec'+filename[x]+'/rec'+filename[x], start=sinorange[0]+y*num_sino_per_substack)
				dxchange.write_tiff_stack(rec, fname=outputPath + 'recon_'+filename[x]+'/recon_'+filename[x], start=sinorange[0]+y*num_sino_per_substack)
			logging.info('Reconstruction Complete: '+ filename[x]+', Process '+rank)
"""

