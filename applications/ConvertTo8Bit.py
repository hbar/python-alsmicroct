import sys
sys.path.append("[local path]/python-TomographyTools")
import microct_toolbox.image_processing as ip

path0 = "/home/[username]@als.lbl.gov/data-scratch/[dataset]"

inputDirectory = ["[dataset1]","[dataset2]","[dataset3]" ]

MIN = -10.0 # minimum pixel value for scaling
MAX = 25.0 # maximum pixel value for scaling

for i in range(len(inputDirectory)):
    ip.convert_DirectoryTo8Bit(inputDirectory[i],data_min=MIN,data_max=MAX,basepath=path0)

