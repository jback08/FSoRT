#!/bin/python

# Python script to store the A,Z isotopes from the XRadNuclides_sum.lis
# files obtained from combineRadNucl.py which uses $FLUPRO/flutil/usrsuwev,
# where X = region name.

import os
import ROOT
import sys

# Data tree structures
ROOT.gInterpreter.Declare("""
struct AStruct{
   int A;
   double w;
   double fErr;
};
""")

ROOT.gInterpreter.Declare("""
struct ZStruct{
   int Z;
   double w;
   double fErr;
};
""")

ROOT.gInterpreter.Declare("""
struct AZStruct{
   int Z;
   int A;
   double w;
   double fErr;
};
""")

class parameters(object):

    def __init__(self, label, region):

        self.baseDir = 'FlukaArchive/fluka2020_v0p3/FSoRT'
        self.label = label
        self.region = region

def run(pars):

    inFileName = '{0}/{1}RadNuclides_sum.lis'.format(pars.label, pars.region)
    print('Running storeIsotopes for {0}'.format(inFileName))

    rootName = '{0}/{1}RadNuclides_sum.root'.format(pars.label, pars.region)

    # Store isotope yields as a function of atomic mass number
    storeMassNumbers(inFileName, rootName)

    # Store isotope yields as a function of atomic number
    storeAtomicNumbers(inFileName, rootName)

    # Store residual nuclei distribution (A vs Z)
    storeAZResNucl(inFileName, rootName)
    
 
def storeMassNumbers(inFileName, rootName):

    print('storeMassNumbers for {0} and {1}'.format(inFileName, rootName))
          
    rootFile = ROOT.TFile.Open(rootName, 'recreate')
    ATree = ROOT.TTree('ATree', 'ATree')
    ATree.SetDirectory(rootFile)

    aStruct = ROOT.AStruct()
    ATree.Branch('A', ROOT.addressof(aStruct, 'A'), 'A/I')
    ATree.Branch('w', ROOT.addressof(aStruct, 'w'), 'w/D')
    ATree.Branch('fErr', ROOT.addressof(aStruct, 'fErr'), 'fErr/D')
    
    with open(inFileName, 'r') as inFile:
        
        iLine = 0
        nSkip = 0
        procData = False

        # Loop over file lines
        for line in inFile:
            iLine += 1

            # Skip lines
            if nSkip > 0:
                nSkip -= 1
                continue
            
            words = line.rstrip('\n').split()
            nWords = len(words)
            if nWords == 0:
                continue

            # Atomic mass values
            if nWords == 5 and words[0] == 'A_min:':
                nSkip = 1
                procData = True

            elif nWords == 6 and words[0] == "A:":
                aStruct.A = int(words[1])
                aStruct.w = float(words[2])
                aStruct.fErr = float(words[4])*0.01
                ATree.Fill()

            elif procData == True and words[0] == '****':
                # Stop processing file
                break

    # Write info
    rootFile.cd()
    ATree.Write()
    rootFile.Close()

    
def storeAtomicNumbers(inFileName, rootName):

    print('storeAtomicNumbers for {0} and {1}'.format(inFileName, rootName))
          
    rootFile = ROOT.TFile.Open(rootName, 'update')
    ZTree = ROOT.TTree('ZTree', 'ZTree')
    ZTree.SetDirectory(rootFile)

    zStruct = ROOT.ZStruct()
    ZTree.Branch('Z', ROOT.addressof(zStruct, 'Z'), 'Z/I')
    ZTree.Branch('w', ROOT.addressof(zStruct, 'w'), 'w/D')
    ZTree.Branch('fErr', ROOT.addressof(zStruct, 'fErr'), 'fErr/D')
    
    with open(inFileName, 'r') as inFile:
        
        iLine = 0
        nSkip = 0
        procData = False

        # Loop over file lines
        for line in inFile:
            iLine += 1

            # Skip lines
            if nSkip > 0:
                nSkip -= 1
                continue
            
            words = line.rstrip('\n').split()
            nWords = len(words)
            if nWords == 0:
                continue

            # Atomic mass values
            if nWords == 5 and words[0] == 'Z_min:':
                nSkip = 1
                procData = True

            elif nWords == 6 and words[0] == "Z:":
                zStruct.Z = int(words[1])
                zStruct.w = float(words[2])
                zStruct.fErr = float(words[4])*0.01
                ZTree.Fill()

            elif procData == True and nWords > 0 and words[0] == '****':
                # Stop processing file
                break

    # Write info
    rootFile.cd()
    ZTree.Write()
    rootFile.Close()

    
def storeAZResNucl(inFileName, rootName):

    print('storeAZResNucl for {0} and {1}'.format(inFileName, rootName))
          
    rootFile = ROOT.TFile.Open(rootName, 'update')
    AZTree = ROOT.TTree('AZTree', 'AZTree')
    AZTree.SetDirectory(rootFile)

    azStruct = ROOT.AZStruct()
    AZTree.Branch('Z', ROOT.addressof(azStruct, 'Z'), 'Z/I')
    AZTree.Branch('A', ROOT.addressof(azStruct, 'A'), 'A/I')
    AZTree.Branch('w', ROOT.addressof(azStruct, 'w'), 'w/D')
    AZTree.Branch('fErr', ROOT.addressof(azStruct, 'fErr'), 'fErr/D')
    
    with open(inFileName, 'r') as inFile:
        
        iLine = 0
        nSkip = 0
        procData = False
        newTable = True
        nCols = 0
        ZValues = []
        weights = []
        
        # Loop over file lines
        for line in inFile:
            iLine += 1

            # Skip lines
            if nSkip > 0:
                nSkip -= 1
                continue
            
            words = line.rstrip('\n').split()
            nWords = len(words)
            if nWords == 0:
                continue

            if words[0] == 'Residual':
                nSkip = 4
                procData = True
                continue

            if words[1] == 'Isomers':
                break
            
            if procData == True:

                if words[0] == 'A' and words[1] == '\\':
                    # Get new table
                    nCols = nWords - 3
                    del ZValues[:]                    
                    for iC in range(nCols):
                        ZVal = int(words[iC+3])
                        ZValues.append(int(words[iC+3]))
                        

                elif nWords == nCols+1:
                    # Atomic mass row
                    azStruct.A = int(words[0])
                    del weights[:]

                    # Store weights for each Z
                    for iC in range(nCols):
                        weights.append(float(words[iC+1]))
                    
                elif nWords >= 2*nCols:
                    
                    # Fractional errors. Zero weights have a space after +-,
                    # otherwise there is no space. Here, reformat the line
                    # to remove these spaces
                    newLine = line.replace('+/- ', '+/-')
                    newWords = newLine.split()
                    newNCols = len(newWords)
                    
                    for iC in range(newNCols/2):

                        errWord = newWords[2*iC]
                        # Remove +- sign
                        newErrWord = errWord.replace('+/-', '')
                        azStruct.fErr = float(newErrWord)*0.01

                        # Retrieve other values then fill the tree
                        azStruct.Z = ZValues[iC]
                        azStruct.w = weights[iC]
                        AZTree.Fill()
                        
    # Write info
    rootFile.cd()
    AZTree.Write()
    rootFile.Close()

    
if __name__ == "__main__":

    label = 'LBNFTargetL150cmAll'
    region = 'Target'

    nArg = len(sys.argv)
    if nArg > 1:
        label = sys.argv[1]
    if nArg > 2:
        region = sys.argv[2]

    pars = parameters(label, region)
    run(pars)

