import sys
sys.path.append("[Local Path]/python-TomographyTools/")
import TomographyTools.reconstruction as rec

parameterList = rec.spreadsheet('[path]/inputfile.xlsx')

for i in range(len(parameterlist)):
    rec.recon(parameterList[i])