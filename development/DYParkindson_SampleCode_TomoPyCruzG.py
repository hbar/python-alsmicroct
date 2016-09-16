# -*- coding: utf-8 -*-

import sys
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout,format='%(message)s')

import numpy as np #
import tomopy
import dxchange
import h5py
import numexpr as ne
import psutil
import gc
from datetime import datetime


def convert8bit(rec,data_min,data_max):
    rec = rec.astype(np.float32,copy=False)
    df = np.float32(data_max-data_min)
    mn = np.float32(data_min)
    scl = ne.evaluate('0.5+255*(rec-mn)/df',truediv=True)
    ne.evaluate('where(scl<0,0,scl)',out=scl)
    ne.evaluate('where(scl>255,255,scl)',out=scl)
    return scl.astype(np.uint8)

def read_als_832h5_metadata(fname):
    """
    Read metadata in ALS 8.3.2 hdf5 dataset files

    :param fname: str, Path to hdf5 file.
    :return dict: dictionary of metadata items
    """

    with h5py.File(fname, 'r') as f:
        g = _find_dataset_group(f)
        return dict(g.attrs)


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
	
idirectory = '/media/win4HDD1/dula/'
#idirectory = '/home/ALS.LBL.GOV/dyparkinson/acruz-gonzalez/'

odirectory = '/home/ALS.LBL.GOV/dyparkinson/data-scratch/acruz-gonzalez/'

doOutliers = True
outlier_diff = 1000
outlier_size = 3

doFWringremoval = False
ringSigma = 4
ringLevel = 8
ringWavelet = 'db5'

doFWringremovalofJustCentralPortion = True
radiusPixels_CentralFW = 60

pad_sino = True

doPhaseRetrieval = True
#thealphavalues = np.logspace(-5,-3,num=5)
#thealphavalues = [0.0003]
alphaReg = 0.0003
propagation_dist = 10
kev = 20

#leave the second parameter, change the first one to adjust smoothness. 0.1 would be very smooth, 0.3 would be more grainy.
butterworthpars = [.2,2]

doPolarRing = True
Rarc=30
Rmaxwidth=30
Rtmax=3000.0
Rthr=3000.0
Rtmin=-1000.0

useAutoCOR = False
testCOR_insteps = False
varyCOR_steps = np.linspace(-1.5,1.5,num=7)

use360to180 = True

recon_centralSlice = False

castTo8bit = True
data_min=-1
data_max=5

useNormalize_nf = True
useFLOCforFWringremoval = False

chunk_size = 94

#it mostly makes sense to overlap chunks if you're doing phase retrieval (otherwise you get lines between chunks)
#overlap_chunk should not be bigger than chunk_size
overlap_chunk = 5


specialBakCrop = [
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
]

iname = [
'20160811_140251_cruz_gonzalez_cacao1_x00y00',
'20160811_140251_cruz_gonzalez_cacao1_x00y01', #optimal is between 2185.5 and 2186.0 at central slice
'20160811_140251_cruz_gonzalez_cacao1_x00y02',
'20160811_140251_cruz_gonzalez_cacao1_x00y03',
'20160811_140251_cruz_gonzalez_cacao1_x00y04',
'20160811_140251_cruz_gonzalez_cacao1_x00y05',
'20160811_140251_cruz_gonzalez_cacao1_x00y06',
'20160811_140251_cruz_gonzalez_cacao1_x00y07',
'20160811_140251_cruz_gonzalez_cacao1_x00y08',


]
		 
fixedcor = [
2187.5,
2185.5,
2184.0,
2182.0,
2180.5,
2179.5,
2178.25,
2176.75,
2175.25,
]




for x in range(0, len(iname)):
	logging.info('Time: %s',datetime.now().time())
	logging.info('opening %s (%d of %d), checking metadata',iname[x],x+1, len(iname))

	gdata = read_als_832h5_metadata(idirectory+iname[x]+'.h5')
	

	pxsize = float(gdata['pxsize'])/10 # convert from metadata (mm) to this script (cm)
	numslices = int(gdata['nslices'])
	if recon_centralSlice:
		sinorange = [numslices//2-1, numslices//2]
	else:
		sinorange = [0, numslices]
		
	num_sino_per_chunk = np.minimum(chunk_size,sinorange[1]-sinorange[0])
	chunks = (sinorange[1]-sinorange[0]-1)//num_sino_per_chunk+1
	
	floc = get_interleaved_indices(gdata)
	original_floc_length = len(floc)

	#for i in range(0, len(floc)):
	#	logging.info('floc: %d',floc[i])

	if specialBakCrop[x]>0:
		floc = floc[0:-specialBakCrop[x]]
		for i in range(0, len(floc)):
			logging.info('Flat field location %d: %d',i, floc[i])

	
	if useAutoCOR:
		logging.info('auto-detecting COR')
		
		firstcor = 0
		if float(gdata['arange'])>300:
			lastcor = int(np.floor(int(gdata['nangles'])/2)-1)
		else:
			lastcor = int(gdata['nangles'])-1
		
		#projs, flat, dark, floc = dxchange.read_als_832h5(idirectory+iname[x]+'.h5', ind_tomo=(firstcor, lastcor))
		projs, flat, dark, flocOld = dxchange.read_als_832h5(idirectory+iname[x]+'.h5', ind_tomo=(firstcor, lastcor))
		

		if specialBakCrop[x]>0:
			num_per_flat = flat.shape[0]//original_floc_length
			flat = flat[0:-specialBakCrop[x]*num_per_flat]
			#logging.info('length flats: %d',flat.shape[0])
		
		if useNormalize_nf:
			projs = tomopy.normalize_nf(projs, flat, dark, floc)
		else:
			projs = tomopy.normalize(projs, flat, dark)
			
		cor = tomopy.find_center_pc(projs[0], projs[1], tol=0.25)
	else:
		cor = fixedcor[x]
	logging.info('Center of rotation: %f', cor)
	logging.info('recon slices %d through %d in %d chunk(s)', sinorange[0], sinorange[1]-1, chunks)
	
#	for alphaReg in thealphavalues:
	for y in range(0, chunks):
		

		logging.info('dataset %d/%d, chunk %d/%d (%d-%d)', x+1,len(iname), y+1, chunks,sinorange[0]+y*num_sino_per_chunk,sinorange[0]+(y+1)*num_sino_per_chunk-1)

		logging.info('Reading data')
		#projs, flat, dark, floc = dxchange.read_als_832h5(idirectory+iname[x]+'.h5', sino=(sinorange[0]+y*num_sino_per_chunk, sinorange[0]+(y+1)*num_sino_per_chunk, 1)) 

		if recon_centralSlice:
			first_sino_slice = sinorange[0]+y*num_sino_per_chunk
			last_sino_slice =  sinorange[0]+(y+1)*num_sino_per_chunk
		else:
			first_sino_slice = np.maximum(sinorange[0]+y*num_sino_per_chunk-overlap_chunk, sinorange[0])
			last_sino_slice =  np.minimum(sinorange[0]+(y+1)*num_sino_per_chunk+overlap_chunk, sinorange[1])
			
		projs, flat, dark, flocNotUsedSeeOtherFLOCvar = dxchange.read_als_832h5(idirectory+iname[x]+'.h5', sino=(first_sino_slice, last_sino_slice, 1)) 
		
		if specialBakCrop[x]>0:
			num_per_flat = flat.shape[0]//original_floc_length
			#logging.info('length flats before: %d',flat.shape[0])
			flat = flat[0:-specialBakCrop[x]*num_per_flat]
			#logging.info('length flats after: %d',flat.shape[0])

		
		if doOutliers:
			projs = tomopy.remove_outlier(projs, outlier_diff, size=outlier_size, axis=0)
			flat = tomopy.remove_outlier(flat, outlier_diff, size=outlier_size, axis=0)
			
		if useNormalize_nf:
			logging.info('Doing normalize (nearest flats)')
			tomo = tomopy.normalize_nf(projs, flat, dark, floc)
		else:
			logging.info('Doing normalize')
			tomo = tomopy.normalize(projs, flat, dark)
		
		
		#sinofilenametowrite = odirectory+'/rec'+iname[x]+'/'+iname[x]+'sino'
		#dxchange.write_tiff_stack(tomo, fname=sinofilenametowrite, start=sinorange[0]+y*num_sino_per_chunk,axis=1)
		projs = None
		flat = None
					
		logging.info('Doing -log')
		tomo = tomopy.minus_log(np.maximum(tomo,0.000000000001), out=tomo) # in place logarithm 
		
		angularrange = float(gdata['arange'])
		logging.info('angular range: %f', angularrange)


	
		# Use padding to remove halo in reconstruction if present
		if pad_sino:
			npad = int(np.ceil(tomo.shape[2] * np.sqrt(2)) - tomo.shape[2])//2
			tomo = tomopy.pad(tomo, 2, npad=npad, mode='edge')
			cor_rec = cor + npad # account for padding
		else:
			cor_rec = cor
	

		
		if doFWringremoval and useFLOCforFWringremoval:
			logging.info('Doing ring (Fourier-wavelet) function')
			tend = 0
			total_tomo = tomo.shape[0]
			num_flats = len(floc)
			for m, loc in enumerate(floc):
				logging.info('fing removal secstion %d of %d',m+1,num_flats)
				if m==0:
					tstart = 0
				else:
					tstart = tend
				if m >= num_flats-1:
					tend = total_tomo
				else:
					tend = int(np.round((floc[m+1]-loc)/2)) + loc
				logging.info('tsart=%d, tend=%d',tstart, tend)
				tomo[tstart:tend,:,:] = tomopy.remove_stripe_fw(tomo[tstart:tend,:,:], sigma=ringSigma, level=ringLevel, pad=True, wname=ringWavelet)	


		# sinofilenametowrite = odirectory+'/rec'+iname[x]+'/'+iname[x]+'sinoBefore3680-180_'
		# dxchange.write_tiff_stack(tomo, fname=sinofilenametowrite, start=sinorange[0]+y*num_sino_per_chunk,axis=1)
		
		if use360to180:
			#logging.info('Shape of projections matrix before 360 to 180: %d, %d, %d', tomo.shape[0],tomo.shape[1],tomo.shape[2])
			logging.info('overlap for 360 to 180 = %f', tomo.shape[2]-cor)

			if tomo.shape[0]%2>0:
				angularrange = angularrange/2 - angularrange/(tomo.shape[0]-1)
				tomo = sino_360_to_180(tomo[0:-1,:,:], overlap=int(np.round((tomo.shape[2]-cor_rec-.5))*2), rotation='right')
			else:
				angularrange = angularrange/2
				tomo = sino_360_to_180(tomo[:,:,:], overlap=int(np.round((tomo.shape[2]-cor_rec))*2), rotation='right')

			
			logging.info('Shape of projections matrix after 360 to 180: %d, %d, %d', tomo.shape[0],tomo.shape[1],tomo.shape[2])
			logging.info('Angular range after 360 to 180: %f', angularrange)

		# sinofilenametowrite = odirectory+'/rec'+iname[x]+'/'+iname[x]+'sinoAfter3680-180_'
		# dxchange.write_tiff_stack(tomo, fname=sinofilenametowrite, start=sinorange[0]+y*num_sino_per_chunk,axis=1)
			
		if doFWringremoval == True and useFLOCforFWringremoval != True:
			logging.info('Doing ring (Fourier-wavelet) function')
			tomo = tomopy.remove_stripe_fw(tomo, sigma=ringSigma, level=ringLevel, pad=True, wname=ringWavelet)	
			
		if doFWringremovalofJustCentralPortion:
			logging.info('Doing ring (Fourier-wavelet) function on just central portion')
			tomo[:,:,int(np.round(cor_rec-radiusPixels_CentralFW)):int(np.round(cor_rec+radiusPixels_CentralFW))] = tomopy.remove_stripe_fw(tomo[:,:,int(np.round(cor_rec-radiusPixels_CentralFW)):int(np.round(cor_rec+radiusPixels_CentralFW))], sigma=ringSigma, level=ringLevel, pad=True, wname=ringWavelet)	
				
		if doPhaseRetrieval:
			logging.info('Doing Phase retrieval')
			# phase_pad_each_side = 10
			# tomo = tomopy.pad(tomo,axis=1,mode='edge',npad=phase_pad_each_side)
			#logging.info('Shape of projections matrix after phase pad: %d, %d, %d', tomo.shape[0],tomo.shape[1],tomo.shape[2])
			tomo = tomopy.retrieve_phase(tomo, pixel_size=pxsize, dist=propagation_dist, energy=kev, alpha=alphaReg, pad=True)	
			# tomo = tomo[:,phase_pad_each_side:-phase_pad_each_side,:]
			#logging.info('Shape of projections matrix after phase crop: %d, %d, %d', tomo.shape[0],tomo.shape[1],tomo.shape[2])
		
		# sinofilenametowrite = odirectory+'/rec'+iname[x]+'/'+iname[x]+'sinoAfterPhase_'
		# dxchange.write_tiff_stack(tomo, fname=sinofilenametowrite, start=sinorange[0]+y*num_sino_per_chunk,axis=1)
		
		
		if recon_centralSlice != True and overlap_chunk>0:
			if y < chunks-1:
				tomo = tomo[:,:-overlap_chunk,:]
			if y > 0:
				tomo = tomo[:,overlap_chunk:,:]

		logging.info('Doing recon (gridrec) function...')


		if testCOR_insteps:
			logging.info('')
		else:
			varyCOR_steps = [0]
			
		for k in varyCOR_steps:
			logging.info('...with center of rotation shifted %f',k)
			rec = tomopy.recon(tomo, tomopy.angles(tomo.shape[0], 270, 270-angularrange), center=cor_rec+k, algorithm='gridrec', filter_name='butterworth', filter_par=butterworthpars)
			
			rec /= pxsize  # intensity values in cm^-1
			

			
			CORtoWrite =cor_rec+k
			
			if doPolarRing:
				logging.info('Doing ring removal (polar mean filter)')
				rec = tomopy.remove_ring(rec, theta_min=Rarc, rwidth=Rmaxwidth, thresh_max=Rtmax, thresh=Rthr, thresh_min=Rtmin)
			
			if pad_sino:
				logging.info('Unpadding...')
				rec = tomopy.circ_mask(rec[:, npad:-npad, npad:-npad], 0)
				CORtoWrite = CORtoWrite - npad
			else:
				rec = tomopy.circ_mask(rec, 0, ratio=1.0, val=0.0)
		


			logging.info('Writing reconstruction slices to %s', iname[x])
			
			if testCOR_insteps:
				filenametowrite = odirectory+'/rec'+iname[x]+'/'+'cor'+str(CORtoWrite)+'_'+iname[x]
			else:
				filenametowrite = odirectory+'/rec'+iname[x]+'/'+iname[x]

			if castTo8bit:
				rec = convert8bit(rec,data_min,data_max)
            						
			dxchange.write_tiff_stack(rec, fname=filenametowrite, start=sinorange[0]+y*num_sino_per_chunk)
			
			logging.info('virtual memory before gc: %s',psutil.virtual_memory())
			gc.collect()
			logging.info('virtual memory after gc: %s',psutil.virtual_memory())
			logging.info('Time: %s',datetime.now().time())
		tomo = None


		
		
