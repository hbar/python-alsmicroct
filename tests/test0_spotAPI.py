import sys
#sys.path.append("/global/u2/h/hbar/python-TomographyTools")
sys.path.append("/home/hsbarnard@als.lbl.gov/data-scratch/python/python-TomographyTools")

import TomographyTools as tt
import TomographyTools.data_management as dm

s = dm.SpotSession(username='hsbarnard')

testData1 = "20160309_091927_sample06_650C_00"
testData2 = "20160309_093629_sample06_650C_01.h5"
testData3 = "20160309_095337_sample06_650C_02.h5"


# Test search function, returns JSON
r_search = s.search("hsbarnard")

# Test 'find derived datasets' function
r_DerivedData = s.derived_datasets(testData1)

# Test data staging function
r_stage = s.stage(testData2,username="roritchie")

# Test attributes function
r_att1 = s.attributes(testData1,username="roritchie")
r_att2 = s.attributes("roritchie/"+testData2)
r_att3 = s.attributes(testData3,username="roritchie")

# Test download
r_download1 = s.download(testData1,username="roritchie")


"""
# Test 'check_authentication
print "authentication = ", s.check_authentication()
print "closing session"
s.close()
print "authentication = ", s.check_authentication()
"""
