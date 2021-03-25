#!/usr/bin/python 

# Python script to print out the maximum energy density (J/cc/pulse) from the Fluka
# usrbin/ascii converted ROOT files. For a given ROOT file, it takes an r and z range
# and prints out the maximum energy density value

import ROOT
import sys
import math
import os

# Energy tree data variables
ROOT.gInterpreter.Declare("""
struct EDataStruct{
   double r;
   double z;
   double E;
};
""")

# Parameters
class initPars(object):
    ''' 
    Simple object to store initial parameters
    '''
    def __init__(self):
        # Target name
        self.targetName = 'DoubleTarget'
        # Fluka file number
        self.index = 21
        # Coordinate boundaries (cm)
        self.zMin = 0.0
        self.zMax = 100.0
        self.rMin = 0.0
        self.rMax = 1.0
        # Pulse time (sec): J/cc/pulse -> W/cc
        self.tPulse = 1.2


def run(pars):
        
    # Open the ascii usrbin files and store the information in the overall ROOT file, 
    # e.g. converted/DoubleTarget001_fort.21.txt

    rootFileName = 'rootFiles/{0}_fort{1}.root'.format(pars.targetName, pars.index)

    rootFile = ROOT.TFile.Open(rootFileName, 'read')
    theTree  = rootFile.Get('Data')

    theData = ROOT.EDataStruct()
    theTree.SetBranchAddress('z', ROOT.addressof(theData, 'z'))
    theTree.SetBranchAddress('r', ROOT.addressof(theData, 'r'))
    theTree.SetBranchAddress('E', ROOT.addressof(theData, 'E'))

    nEntries = theTree.GetEntries()

    maxE = 0.0

    for i in range(nEntries):

        theTree.GetEntry(i)

        # Check r and z ranges
        if theData.z >= pars.zMin and theData.z <= pars.zMax:

            if theData.r >= pars.rMin and theData.r <= pars.rMax:

                if theData.E > maxE:
                    maxE = theData.E

    print '{0} for z = [{1},{2}] and r = [{3},{4}] cm max E den = {5} J/cc/pulse = {6} W/cc'.format(rootFileName, pars.zMin, pars.zMax,
                                                                                                    pars.rMin, pars.rMax, maxE, 
                                                                                                    maxE/pars.tPulse)

    rootFile.Close()


if __name__ == "__main__":

    pars = initPars()

    nArg = len(sys.argv)
    if nArg != 7:
        print 'Expecting the following 6 arguments: targetName, fileIndex, zMin, zMax, rMin, rMax (cm)'
        exit()

    pars.targetName = sys.argv[1]
    pars.index = int(sys.argv[2])
    pars.zMin = float(sys.argv[3])
    pars.zMax = float(sys.argv[4])
    pars.rMin = float(sys.argv[5])
    pars.rMax = float(sys.argv[6])

    run(pars)

