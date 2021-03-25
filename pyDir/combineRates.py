#!/usr/bin/python 
# Python script to combine the regional isotope activities (rates and masses)

import ROOT
import sys
import math
import os

# Parameters
class initPars(object):
    ''' 
    Simple object to store initial parameters
    '''
    def __init__(self, dirName):
        # Directory name
        self.dirName = dirName

def run(pars):

    print('Running combine rates for {0}'.format(pars.dirName))
    

if __name__ == "__main__":

    dirName = 'LBNFTargetL150cmAll'
    nArg = len(os.sys.argv)
    if nArg > 1:
        dirName = os.sys.argv[1]

    pars = initPars(dirName)
    run(pars)
