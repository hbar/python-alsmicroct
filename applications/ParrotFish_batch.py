import reconstruction as recon
import numpy as np
import tomopy
import dxchange

fileList = ["""
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y00",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y01",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y02",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y03",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y04",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y05",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y06",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y07",
"20160610_150949_parrotfish_teeth_2x_35keV_tilescan_x00y08",
"20160610_182027_parrotfish_toptooth_10x_24keV", """
"20160610_184113_parrotfish_tooth3_10x_24keV"
]

pathIN = '/media/win4HDD1/hsbarnard/20160610_ParrotFish_RawData/'
pathOUT = '/media/win4HDD1/hsbarnard/20160610_ParrotFish_Reconstructions/'

COR = [1316.5,#00
1315.0,#01
1314.0,#02
1313.5,#03
1313.5,#04
1313.5,#05
1312.0,#06
1311.5,#07
1313.5,#08
1213.5,#10x
1210.0 #10x
]

recon.reconstruct(filename=fileList,inputPath=pathIN, outputPath=pathOUT, COR=COR)
