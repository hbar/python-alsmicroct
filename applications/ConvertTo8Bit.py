import sys
sys.path.append("[Local Path]/python-TomographyTools/")
import TomographyTools.image_processing as ip

path0 = "/home/[username]@als.lbl.gov/data-scratch/[DirectoryName]/"

inputDirectory = ["dataDirectory1","dataDirectory2","dataDirectory3"]

MIN = -10.0
MAX = 10.0

for i in range(len(inputDirectories)):
    ip.convert_DirectoryTo8Bit(inputDirectory[i],data_min=MIN,data_max=MAX,basepath=path0)

