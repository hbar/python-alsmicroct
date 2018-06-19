from distutils.core import setup

setup(
    name='microct_toolbox',
    version='0.1dev',
    author='H.S.Barnard, D.Y.Parkinson',
    packages=['data_management','image_processing','reconstruction',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
