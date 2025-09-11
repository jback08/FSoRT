#!/usr/bin/python 

# Python script to create ROOT files containing the event-by-event regional
# energy deposition data from the Fluka simulations, i.e. the "evt.txt" files.
# Each evt.txt file is in the appropriate job sub-directory.
# The 64-bit Fluka results have a different output format compared to the old NuFact
# simulations (more spacings/decimals), so we avoid using the old perl and C++ code

import ROOT
import os
import sys
import math

# Used to store the average energy and power values
ROOT.gInterpreter.Declare("""
struct EDataStruct{
   int nRegions;
   vector<double>* EDep;
   vector<double>* EDepErr;
   vector<double>* Power;
   vector<double>* PowerErr;
   vector<TString>* region;
};
""")

# Parameters
class initPars(object):
    ''' 
    Simple object to store initial parameters
    '''

    def __init__(self, targetLabel, option = 1, nJobs = 100):

        # Base directory containing the job output
        self.baseDir = '/exp/dune/data/users/jback/FlukaArchive/fluka4-5.0/FSoRT'

        # The label for the target output files
        self.targetLabel = targetLabel

        # Beam option
        self.option = option
        
        # The number of simulation job directories
        self.nJobs = nJobs

        # Convert GeV to Joules
        self.GeVToJ = 1.602e-10
        # Proton beam momentum (GeV/c)
        self.p = 120.0
        # Proton beam KE
        self.KE = getKE(self.p)
        # LBNF efficiency (57%, was 56%)
        self.eff = 0.57
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
        print('KE = {0}, POTyr = {1}, POTScale = {2}, POTPulse = {3}, ' \
              't = {4} s, rate = {5}'.format(self.KE, self.POTyr, self.POTScale, self.POTPulse,
                                             self.pulseT, self.POTRate))
        print('POTRate = {0}'.format(self.POTRate))

        PScale = self.GeVToJ*self.POTRate
        print('PScale = {0}'.format(PScale))



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

    rootFileName = '{0}/{1}_Opt{2}_All/{1}_Opt{2}_EDep.root'.format(pars.baseDir, pars.targetLabel, pars.option)
    print('Creating {0}'.format(rootFileName))

    rootFile = ROOT.TFile.Open(rootFileName, 'recreate')
    theTree  = ROOT.TTree('Data', 'Data')
    theTree.SetDirectory(rootFile)

    theData = ROOT.EDataStruct()
    theTree.Branch('nRegions', ROOT.addressof(theData, 'nRegions'), 'nRegions/I')
    
    theData.EDep = ROOT.std.vector('double')()
    theData.EDepErr = ROOT.std.vector('double')()
    theData.Power = ROOT.std.vector('double')()
    theData.PowerErr = ROOT.std.vector('double')()
    theData.region = ROOT.std.vector('TString')()

    theTree.Branch('EDep', theData.EDep)
    theTree.Branch('EDepErr', theData.EDepErr)
    theTree.Branch('Power', theData.Power)
    theTree.Branch('PowerErr', theData.PowerErr)
    theTree.Branch('region', theData.region)
    
    # Keep track of the cumulative event number for finding the recursive mean and sigma
    NEvent = 0.0

    # Fill region information
    fillRegionInfo(theData, pars)

    # Initialise vector sizes
    theData.EDep.resize(theData.nRegions)
    theData.EDepErr.resize(theData.nRegions)
    theData.Power.resize(theData.nRegions)
    theData.PowerErr.resize(theData.nRegions)

    # For each event file find the total energy in each region averaged over all events.
    # Then find the average value and spread over all job directories (100).
    # Here we use histograms for this
    histList = []
    for iR in range(theData.nRegions):

        hName = 'EHist{0}'.format(iR)

        hist = ROOT.TH1D(hName, '', 100, 0.0, 0.0)
        hist.SetXTitle('E (GeV)')
        hist.SetDirectory(rootFile)

        histList.append(hist)

    # Open the evt.txt files, extract the energy information and store in the ROOT file
    # e.g DoubleTargetJob0/DoubleTarget001_evt.txt
    for iJob in range(pars.nJobs):

        evtFileName = '{0}/{1}_Opt{2}_{3}/{1}001_evt.txt'.format(pars.baseDir, pars.targetLabel, pars.option, iJob)
        print('evtFileName = {0}'.format(evtFileName))

        # Initialise number of events in this file and the energy array for all regions
        EArray = [0.0]*theData.nRegions
        NEvent = 0.0

        # Read the lines until we get to the "Generalized (scoring distribution)" keyword.
        # Then skip the next line and the following line has the event data we need to store
        with open(evtFileName, 'r') as evtFile:
            
            nSkip = 0
            gotLine = False

            for inLine in evtFile:

                if nSkip > 0:
                    nSkip -= 1
                    continue

                words = inLine.rstrip('\n').split()
                if len(words) < 1: 
                    continue

                firstWord = words[0]

                if firstWord == 'Generalized':
                    gotLine = True
                    nSkip = 1

                if gotLine == True and nSkip == 0:
                    
                    nValues = len(words)

                    # Recursively find the mean and standard deviation of the 
                    # deposited energy in each region
                    N1 = NEvent
                    NEvent += 1.0

                    # Loop over all regions
                    for iR in range(theData.nRegions):

                        # The deposited energy (GeV) in the given region
                        energy = float(words[iR])

                        # Recursive mean energy for given region over all events thus far
                        EMean = EArray[iR]
                        EArray[iR] = (N1*EMean + energy)/NEvent

                    # Reset gotLine boolean
                    gotLine = False

        # Store event-averaged regional energy info in the histograms
        for iR in range(theData.nRegions):
            EHist = histList[iR]
            EHist.Fill(EArray[iR])

    # Now scale the deposited energies for one proton beam pulse and also find the
    # average deposited power values in all regions
    EScale = pars.GeVToJ*pars.POTPulse
    PScale = pars.GeVToJ*pars.POTRate

    print('EScale = {0}, PScale = {1}'.format(EScale, PScale))

    for iR in range(theData.nRegions):        

        EHist  = histList[iR]
        energy = EHist.GetMean()
        error  = EHist.GetStdDev()

        theData.EDep[iR] = energy*EScale
        theData.EDepErr[iR] = error*EScale

        theData.Power[iR] = energy*PScale
        theData.PowerErr[iR] = error*PScale
        
        volName = theData.region[iR]
    
    # Write out the power information in the ROOT file
    
    theTree.Fill()

    rootFile.cd()
    theTree.Write()
    # Also store histograms
    for iR in range(theData.nRegions):
        EHist = histList[iR]
        EHist.Write()

    rootFile.Close()
    

def fillRegionInfo(theData, pars):

    theData.region.clear()

    if 'LBNFBaffleSept25' in pars.targetLabel:

        theData.region.push_back(ROOT.TString('BlackBody'))
        theData.region.push_back(ROOT.TString('Void1'))
        theData.region.push_back(ROOT.TString('PWVac'))
        theData.region.push_back(ROOT.TString('PWTotGas'))
        theData.region.push_back(ROOT.TString('PWSteel'))
        theData.region.push_back(ROOT.TString('PBWindow'))
        theData.region.push_back(ROOT.TString('MBaffleA'))
        theData.region.push_back(ROOT.TString('MBaffleB'))
        theData.region.push_back(ROOT.TString('MBaffleC'))
        theData.region.push_back(ROOT.TString('MBaffleD'))
        theData.region.push_back(ROOT.TString('MBaffleE'))
        theData.region.push_back(ROOT.TString('MBFinsA'))
        theData.region.push_back(ROOT.TString('MBFinsB'))
        theData.region.push_back(ROOT.TString('MBFinsC'))
        theData.region.push_back(ROOT.TString('MBFinsD'))
        theData.region.push_back(ROOT.TString('MBFinsE'))
        theData.region.push_back(ROOT.TString('MBRingU'))
        theData.region.push_back(ROOT.TString('MBRingA'))
        theData.region.push_back(ROOT.TString('MBRingB'))
        theData.region.push_back(ROOT.TString('MBRingC'))
        theData.region.push_back(ROOT.TString('MBRingD'))
        theData.region.push_back(ROOT.TString('MBRingE'))
        theData.region.push_back(ROOT.TString('MBDuct'))
        theData.region.push_back(ROOT.TString('MBGasO'))
        theData.region.push_back(ROOT.TString('MBGasU'))
        theData.region.push_back(ROOT.TString('MBGasA'))
        theData.region.push_back(ROOT.TString('MBGasB'))
        theData.region.push_back(ROOT.TString('MBGasC'))
        theData.region.push_back(ROOT.TString('MBGasD'))
        theData.region.push_back(ROOT.TString('MBGasE'))
        theData.region.push_back(ROOT.TString('MBGasF1'))
        theData.region.push_back(ROOT.TString('MBGasF2'))

    elif 'LBNFBaffleTPTSept25' in pars.targetLabel:

        theData.region.push_back(ROOT.TString('BlackBody'))
        theData.region.push_back(ROOT.TString('Void1'))
        theData.region.push_back(ROOT.TString('PWVac'))
        theData.region.push_back(ROOT.TString('PWTotGas'))
        theData.region.push_back(ROOT.TString('PWSteel'))
        theData.region.push_back(ROOT.TString('PBWindow'))
        theData.region.push_back(ROOT.TString('MBaffleA'))
        theData.region.push_back(ROOT.TString('MBaffleB'))
        theData.region.push_back(ROOT.TString('MBaffleC'))
        theData.region.push_back(ROOT.TString('MBaffleD'))
        theData.region.push_back(ROOT.TString('MBaffleE'))
        theData.region.push_back(ROOT.TString('MBFinsA'))
        theData.region.push_back(ROOT.TString('MBFinsB'))
        theData.region.push_back(ROOT.TString('MBFinsC'))
        theData.region.push_back(ROOT.TString('MBFinsD'))
        theData.region.push_back(ROOT.TString('MBFinsE'))
        theData.region.push_back(ROOT.TString('MBRingU'))
        theData.region.push_back(ROOT.TString('MBRingA'))
        theData.region.push_back(ROOT.TString('MBRingB'))
        theData.region.push_back(ROOT.TString('MBRingC'))
        theData.region.push_back(ROOT.TString('MBRingD'))
        theData.region.push_back(ROOT.TString('MBRingE'))
        theData.region.push_back(ROOT.TString('MBDuct'))
        theData.region.push_back(ROOT.TString('MBGasO'))
        theData.region.push_back(ROOT.TString('MBGasU'))
        theData.region.push_back(ROOT.TString('MBGasA'))
        theData.region.push_back(ROOT.TString('MBGasB'))
        theData.region.push_back(ROOT.TString('MBGasC'))
        theData.region.push_back(ROOT.TString('MBGasD'))
        theData.region.push_back(ROOT.TString('MBGasE'))
        theData.region.push_back(ROOT.TString('MBGasF1'))
        theData.region.push_back(ROOT.TString('MBGasF2'))
        theData.region.push_back(ROOT.TString('MBGasG'))
        theData.region.push_back(ROOT.TString('MountGas1'))
        theData.region.push_back(ROOT.TString('TPTGas'))
        theData.region.push_back(ROOT.TString('TPTCeram'))
        theData.region.push_back(ROOT.TString('TPT'))
        theData.region.push_back(ROOT.TString('TPTBox'))
        theData.region.push_back(ROOT.TString('TPTBrac'))
        theData.region.push_back(ROOT.TString('MountGas2'))

    elif 'LBNFTgtL150cmSept25' in pars.targetLabel:

        theData.region.push_back(ROOT.TString('BlackBody'))
        theData.region.push_back(ROOT.TString('Void1'))
        theData.region.push_back(ROOT.TString('PWVac'))
        theData.region.push_back(ROOT.TString('PWTotGas'))
        theData.region.push_back(ROOT.TString('PWSteel'))
        theData.region.push_back(ROOT.TString('PBWindow'))
        theData.region.push_back(ROOT.TString('MBaffleA'))
        theData.region.push_back(ROOT.TString('MBaffleB'))
        theData.region.push_back(ROOT.TString('MBaffleC'))
        theData.region.push_back(ROOT.TString('MBaffleD'))
        theData.region.push_back(ROOT.TString('MBaffleE'))
        theData.region.push_back(ROOT.TString('MBFinsA'))
        theData.region.push_back(ROOT.TString('MBFinsB'))
        theData.region.push_back(ROOT.TString('MBFinsC'))
        theData.region.push_back(ROOT.TString('MBFinsD'))
        theData.region.push_back(ROOT.TString('MBFinsE'))
        theData.region.push_back(ROOT.TString('MBRingU'))
        theData.region.push_back(ROOT.TString('MBRingA'))
        theData.region.push_back(ROOT.TString('MBRingB'))
        theData.region.push_back(ROOT.TString('MBRingC'))
        theData.region.push_back(ROOT.TString('MBRingD'))
        theData.region.push_back(ROOT.TString('MBRingE'))
        theData.region.push_back(ROOT.TString('MBDuct'))
        theData.region.push_back(ROOT.TString('MBGasO'))
        theData.region.push_back(ROOT.TString('MBGasU'))
        theData.region.push_back(ROOT.TString('MBGasA'))
        theData.region.push_back(ROOT.TString('MBGasB'))
        theData.region.push_back(ROOT.TString('MBGasC'))
        theData.region.push_back(ROOT.TString('MBGasD'))
        theData.region.push_back(ROOT.TString('MBGasE'))
        theData.region.push_back(ROOT.TString('MBGasF1'))
        theData.region.push_back(ROOT.TString('MBGasF2'))
        theData.region.push_back(ROOT.TString('MBGasG'))
        theData.region.push_back(ROOT.TString('MountGas1'))
        theData.region.push_back(ROOT.TString('TPTGas'))
        theData.region.push_back(ROOT.TString('TPTCeram'))
        theData.region.push_back(ROOT.TString('TPT'))
        theData.region.push_back(ROOT.TString('TPTBox'))
        theData.region.push_back(ROOT.TString('TPTBrac'))
        theData.region.push_back(ROOT.TString('TPTMount'))
        theData.region.push_back(ROOT.TString('Horn1Out'))
        theData.region.push_back(ROOT.TString('Horn1In'))
        theData.region.push_back(ROOT.TString('Horn1End'))
        theData.region.push_back(ROOT.TString('Horn1Gas1'))
        theData.region.push_back(ROOT.TString('Horn1Gas2'))
        theData.region.push_back(ROOT.TString('MountGas2'))
        theData.region.push_back(ROOT.TString('OutVol'))
        theData.region.push_back(ROOT.TString('BeamGas'))
        theData.region.push_back(ROOT.TString('DSGas'))
        theData.region.push_back(ROOT.TString('EndGas1'))
        theData.region.push_back(ROOT.TString('EndGas2'))
        theData.region.push_back(ROOT.TString('Horn1Cool'))
        theData.region.push_back(ROOT.TString('TFlow'))
        theData.region.push_back(ROOT.TString('TCont'))
        theData.region.push_back(ROOT.TString('BaffletCont'))
        theData.region.push_back(ROOT.TString('TFinsA'))
        theData.region.push_back(ROOT.TString('TFinsB'))
        theData.region.push_back(ROOT.TString('TFinsC'))
        theData.region.push_back(ROOT.TString('TDSWin'))
        theData.region.push_back(ROOT.TString('UpWindow'))
        theData.region.push_back(ROOT.TString('BaffletGas'))
        theData.region.push_back(ROOT.TString('TGas1'))
        theData.region.push_back(ROOT.TString('TGas2'))
        theData.region.push_back(ROOT.TString('TGas2U'))
        theData.region.push_back(ROOT.TString('TGas2A'))
        theData.region.push_back(ROOT.TString('TGas2B'))
        theData.region.push_back(ROOT.TString('TGas2C'))
        theData.region.push_back(ROOT.TString('TGas2D'))
        theData.region.push_back(ROOT.TString('TGas3'))
        theData.region.push_back(ROOT.TString('TGas4A'))
        theData.region.push_back(ROOT.TString('TGas4B'))
        theData.region.push_back(ROOT.TString('TGas4C'))
        theData.region.push_back(ROOT.TString('Target'))
        theData.region.push_back(ROOT.TString('TJoinU'))
        theData.region.push_back(ROOT.TString('TJoinA'))
        theData.region.push_back(ROOT.TString('TJoinB'))
        theData.region.push_back(ROOT.TString('TJoinC'))
        theData.region.push_back(ROOT.TString('Bafflet'))

    nRegions = theData.region.size()
    theData.nRegions = nRegions
    print('Number of regions = {0}'.format(nRegions))


def run(pars):

    createRootFile(pars)


if __name__ == "__main__":

    targetLabel = 'LBNFBaffleSept25'
    #targetLabel = 'LBNFBaffleTPTSept25'
    #targetLabel = 'LBNFTgtL150cmSept25'
    option = 1
    nJobs = 100
    
    nArg = len(sys.argv)
    if nArg > 1:
        targetLabel = sys.argv[1]
    if nArg > 2:
        option = int(sys.argv[2])
    if nArg > 3:
        nJobs = int(sys.argv[3])

    pars = initPars(targetLabel, option, nJobs)
    run(pars)
