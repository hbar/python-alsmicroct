import numpy as np
import xlrd
from ast import literal_eval # For converting string to tuple

#path0 = "C:/Users/hsbarnard/Dropbox/Research(LBL)"
path0 = '/mnt/bl832data-scratch/hsbarnard/python/python-TomographyTools/'
path1 = "tests/testdata/"
filename = "test_recon_input_spreadsheet1.xlsx"

# opens workbook (excel document), ch0oses first sheet
workbook=xlrd.open_workbook(path0+path1+filename)
worksheet =  workbook.sheet_by_index(0)

# imports first row and converts to a list of header strings
headerList = []
for col_index in range(worksheet.ncols):
    headerList.append(worksheet.cell_value(0,col_index))


dataList = []
# For each row, create a dictionary and like header name to data 
# converts each row to following format rowDictionary1 ={'header1':colvalue1,'header2':colvalue2,... }
# compiles rowDictinaries into a list: dataList = [rowDictionary1, rowDictionary2,...]
for row_index in range(1,worksheet.nrows):
    rowDictionary = {}
    for col_index in range(worksheet.ncols):
        cellValue = worksheet.cell_value(row_index,col_index)
        
        # if cell contains string that looks like a tuple, convert to tuple
        if '(' in str(cellValue):
            cellValue = literal_eval(cellValue)

        # if cell contains string or int that looks like 'True', convert to boolean True
        if str(cellValue).lower() =='true' or (type(cellValue)==int and cellValue==1):
            cellValue = True

        # if cell contains string or int that looks like 'False', convert to boolean False
        if str(cellValue).lower() =='false' or (type(cellValue)==int and cellValue==0):
            cellValue = False

        if cellValue != '': # create dictionary element if cell value is not empty
            rowDictionary[headerList[col_index]] = cellValue
    dataList.append(rowDictionary)

print dataList
