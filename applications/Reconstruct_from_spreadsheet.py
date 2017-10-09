import sys

#sys.path.append("/home/hsbarnard@als.lbl.gov/data-scratch/python/python-TomographyTools/") # Path on beamline viz computers
sys.path.append("[local path]/python-TomographyTools/")

import TomographyTools.reconstruction as rec

filename = "[path]/recon_test_spreadsheet.xlsx"
params = rec.spreadsheet(filename)

for i in range(len(params)):
    rec.recon(**params[i])
