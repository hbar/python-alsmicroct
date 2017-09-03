import sys
sys.path.append("/global/u2/h/hbar/python-TomographyTools")

import TomographyTools as tt
import TomographyTools.data_management as dm

s = dm.spotSession(username=hsbarnard)

# Test search function, returns JSON
r_search = s.search("hsbarnard")

# Test 'find derived datasets' function
testData1 = "20160309_091927_sample06_650C_00"
r_DerivedData = s.derived_datasets(testData1)

# Test data staging function
testData2 = "20160309_093629_sample06_650C_01.h5"
r_stage = s.stage(testData2)

r_att1 = s.attributes(testData1,username="roritchie")
r_att2 = s.attributes("roritchie/"+testData2)

"""
# Test 'check_authentication
print "authentication = ", s.check_authentication()
print "closing session"
s.close()
print "authentication = ", s.check_authentication()
"""
