import sys
sys.path.append("/global/u2/h/hbar/python-TomographyTools")

import TomographyTools as tt
import TomographyTools.data_management as dm

s = dm.spotSession()

r_search = s.search("hsbarnard")

testData0 = "20160211_172431_gummybear_fast_im1025_exp100us.h5"
testData1 = "20160309_091927_sample06_650C_00"
r_DerivedData = s.derived_datasets(testData1)

