import sys
#sys.path.append("/global/u2/h/hbar/python-TomographyTools") # Path on nersc
sys.path.append("/home/hsbarnard@als.lbl.gov/data-scratch/python/python-TomographyTools") # Path on beamline viz computers

import TomographyTools as tt
import TomographyTools.data_management as dm
import TomographyTools.reconstruction as rec


params = rec.spreadsheet("recon_test_spreadsheet.xlsx")

rec.recon(**params[0])
