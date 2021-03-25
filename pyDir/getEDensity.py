#!/usr/bin/python 

# Python script to extract the energy densities (J/cc/pulse) for the target.
# This creates a ROOT file of the ascii data of the combined usrbin histogram files 
# created by the convertUsrbin.py script. The ascii file first contains the histogram 
# entries, followed by the statistical uncertainty for each bin

import ROOT
import sys
import math
import os

# Used to store the energy histogram data: radius, z, energy and its uncertainty.
ROOT.gInterpreter.Declare("""
struct EDataStruct{
   double r;
   double r1;
   double r2;
   double z;
   double z1;
   double z2;
   double E;
   double Err;
};
""")

# Parameters
class initPars(object):
    ''' 
    Simple object to store initial parameters
    '''

    def __init__(self):
        # The label for the target output files
        self.targetLabel = 'DoubleTarget'
        # The number of simulation job directories
        self.nJobs = 100
        # Convert GeV to Joules
        self.GeVToJ = 1.602e-10
        # Proton beam momentum (GeV/c)
        self.p = 120.0
        # Proton beam KE
        self.KE = getKE(self.p)
        # LBNF efficiency
        self.eff = 0.56
        # Number of seconds in year
        self.yrSec = 3.15576e7
        # Number of protons on target per year for 1.2 MW operation
        self.POTyr = getPowerPOTScaleFactor(self.KE)*1.1e21
        # Pulse length: varies with proton momentum according to POTScaleFactor calculation.
        # For 120 GeV, t = 1.2 sec. For lower E, t decreases to get 1.2 MW, scaling with this factor
        self.POTScale = getPowerPOTScaleFactor(self.KE)
        self.pulseT = 1.2/self.POTScale
        # Number of protons on target per pulse ("spill") for 1.2 MW: fixed at 7.5e13/pulse
        #self.POTPulse = self.POTyr*self.pulseT/(self.yrSec*self.eff)
        self.POTPulse = 7.5e13
        # POT rate (per sec) for deposited power calculations
        self.POTRate = self.POTPulse/self.pulseT
        print 'KE = {0}, POTyr = {1}, POTScale = {2}, POTPulse = {3}, t = {4} s, rate = {5}'.format(self.KE, self.POTyr,
                                                                                                    self.POTScale,
                                                                                                    self.POTPulse, 
                                                                                                    self.pulseT,
                                                                                                    self.POTRate)
        # Start and end indices for "fort.txt" output files
        self.startInt = 21
        self.endInt = 29
  

def getPowerPOTScaleFactor(energy):

    # From GeneticOptimization/OptimizationUtils.py

    if (energy >= 120.0):
        return 120.0/energy

    if (energy < 60.0):
        return 1.71e21/1e21 # limited to 0.7 s cycle time

    # linear interpolate
    energies = [60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0]
    potperyear = [1.71e21, 1.5e21, 1.33e21, 1.23e21, 1.14e21, 1.07e21, 1e21]

    for i in range(0,len(energies)):
        if energy < energies[i]:
            interp_high = i
            interp_low = i-1
            break

    scale_factor = (potperyear[interp_high]+(potperyear[interp_low]-potperyear[interp_high])/(energies[interp_high]-energies[interp_low])*(energies[interp_high]-energy))/1e21

    return scale_factor


def getKE(pBeam):

    # Get the kinetic energy given the proton beam momentum.
    # E = T + m, E2 = p2 + m2 => T = sqrt(p2 + m2) - m
    m0 = 0.938272
    KE = math.sqrt(pBeam*pBeam + m0*m0) - m0
    return KE


# Above is all initialisation

def createRootFile(pars):
        
    # Open the ascii usrbin files and store the information in the overall ROOT file, 
    # e.g. converted/DoubleTarget001_fort.21.txt

    if not os.path.exists(pars.textFileName):
        print 'Cannot find file {0}'.format(pars.textFileName)
        return

    print 'Creating {0} from {1}'.format(pars.rootFileName, pars.textFileName)

    # First store the ascii information in vectors then put the data in the ROOT Tree.
    # We need to do this since the uncertainties are in the last half of the file and we
    # only want to call TTree.Fill() when we have read all of the file data
    r1Vect = ROOT.std.vector('double')()
    r2Vect = ROOT.std.vector('double')()
    z1Vect = ROOT.std.vector('double')()
    z2Vect = ROOT.std.vector('double')()
    EVect = ROOT.std.vector('double')()
    ErrVect = ROOT.std.vector('double')()

    with open(pars.textFileName, 'r') as inFile:

        iLine = 0
        nSkip = 0
        gotBins = False
        gotAllData = False
        gotRemain = False
        dataLine = 0
        fracLine = 0
        
        minR = 0.0
        maxR = 0.0
        nR = 0
        dR = 0.0
        minZ = 0.0
        maxZ = 0.0
        nZ = 0
        dZ = 0.0
        
        nTotBins = 0
        nFullLines = 0
        nRemain = 0
        nAllLines = 0
        nPrevWords = 0
        
        # Loop over lines in the file
        for inLine in inFile:

            iLine += 1
                
            # Skip any lines
            if nSkip > 0:
                nSkip -= 1
                continue

            # Strings on the line
            words = inLine.rstrip('\n').split()
            nWords = len(words)
            if nWords < 1:
                continue

            if iLine == 3:
                # r binning
                minR = float(words[3])
                maxR = float(words[5])
                nR = int(words[7])
                dR = float(words[10])
                continue

            elif iLine == 4:
                # z binning
                minZ = float(words[3])
                maxZ = float(words[5])
                nZ = int(words[7])
                dZ = float(words[10])
                    
                # Number of lines containing the energy values. Each row contains 10 numbers (columns).
                # Find out if we have a nonzero remainder
                nTotBins = nR*nZ
                nFullLines = nTotBins/10
                nRemain = nTotBins%10
                nAllLines = nFullLines
                if nRemain > 0:
                    nAllLines += 1
                print 'nTotBins = {0}, nFull = {1}, nRemain = {2}, nAll = {3}'.format(nTotBins, nFullLines, nRemain, nAllLines)
                    
                gotBins = True
                # Skip the next few lines
                nSkip = 4
                continue
                
            if gotBins == True and gotAllData == False:

                # Read the data values (should be 10 columns per full line)
                startIdx = nPrevWords*dataLine

                for iCol in range(nWords):
                        
                    dataIndex = startIdx + iCol
                    rIndex = dataIndex%nR
                    zIndex = dataIndex/nR
                        
                    # Bin co-ordinate boundaries
                    r1 = rIndex*dR + minR
                    r2 = r1 + dR
                    z1 = zIndex*dZ + minZ
                    z2 = z1 + dZ
                    
                    # Energy density value
                    value = float(words[iCol])
                    
                    r1Vect.push_back(r1)
                    r2Vect.push_back(r2)
                    z1Vect.push_back(z1)
                    z2Vect.push_back(z2)
                    EVect.push_back(value)

                    #print 'r = {0}, {1}, z = {2}, {3}, E = {4}'.format(r1, r2, z1, z2, value)

                # Increment the data line count, and check if we have finished reading them
                dataLine += 1
                # Keep track of how many words we had on this line for the next index
                nPrevWords = nWords

                # Check to see if we have processed all of the required number of data lines
                if dataLine == nAllLines:
                    gotAllData = True
                    # We need to skip the next few lines for the percentage errors
                    nSkip = 3

            elif gotBins == True and gotAllData == True:

                # Read the fractional uncertainties (should be 10 columns per line). These
                # numbers will correspond with the exact same binning as the values above
                startIdx = nWords*fracLine

                for iCol in range(nWords):
                        
                    # Fractional error
                    error = float(words[iCol])
                    ErrVect.push_back(error)


    rootDir = 'rootFiles'
    if (os.path.isdir(rootDir) == False):
        os.makedirs(rootDir)

    rootFile = ROOT.TFile.Open(pars.rootFileName, 'recreate')
    theTree  = ROOT.TTree('Data', 'Data')
    theTree.SetDirectory(rootFile)

    theData = ROOT.EDataStruct()
    theTree.Branch('r', ROOT.addressof(theData, 'r'), 'r/D')
    theTree.Branch('r1', ROOT.addressof(theData, 'r1'), 'r1/D')
    theTree.Branch('r2', ROOT.addressof(theData, 'r2'), 'r2/D')
    theTree.Branch('z', ROOT.addressof(theData, 'z'), 'z/D')
    theTree.Branch('z1', ROOT.addressof(theData, 'z1'), 'z1/D')
    theTree.Branch('z2', ROOT.addressof(theData, 'z2'), 'z2/D')
    theTree.Branch('E', ROOT.addressof(theData, 'E'), 'E/D')
    theTree.Branch('Err', ROOT.addressof(theData, 'Err'), 'Err/D')

    # Scale the energy values from GeV/cc to J/cc/pulse
    EScale = pars.GeVToJ*pars.POTPulse

    for i in range(nTotBins):
        
        theData.r1 = r1Vect[i]
        theData.r2 = r2Vect[i]
        theData.z1 = z1Vect[i]
        theData.z2 = z2Vect[i]
        theData.E = EVect[i]*EScale
        theData.Err = ErrVect[i]*0.01
        theData.r = 0.5*(theData.r1 + theData.r2)
        theData.z = 0.5*(theData.z1 + theData.z2)

        theTree.Fill()


    rootFile.cd()
    theTree.Write()
    rootFile.Close()

def run(pars):

    # Create ROOT file equivalent for each ascii data file
    for iFile in range(pars.startInt, pars.endInt+1):

        textFileName = 'converted/{0}001_fort.{1}.txt'.format(pars.targetLabel, iFile)
        pars.textFileName = textFileName

        rootFileName = 'rootFiles/{0}_fort{1}.root'.format(pars.targetLabel, iFile)
        pars.rootFileName = rootFileName

        createRootFile(pars)


if __name__ == "__main__":

    pars = initPars()

    nArg = len(sys.argv)
    if nArg > 1:
        pars.targetLabel = sys.argv[1]

    run(pars)
