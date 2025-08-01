#!/usr/bin/env python3

"""
Python script to store the pion and muon tracking information using ROOT
from the Fluka BXDRAW subroutine output (crossing planes)

"""

# Import various python libraries

# Parse script input parameters: "python createROOTFiles.py -h"
import argparse
# Math operators, e.g sqrt
import math
# Operating system
import os
# ROOT data analysis package
import ROOT
# Used to read run argument parameters
import sys
# Used for ROOT data structure
from cppyy.ll import cast

# Define structure for storing variables when processing output file:
# job & event numbers, Particle Data Group integer, total energy & KE (GeV),
# position & radius (cm), momentum components (GeV), lifetime (ns)
# and Monte Carlo (MC) weight (usually 1.0)
ROOT.gInterpreter.Declare("""
struct FlukaStruct{
   int iJob;
   int iEvt;
   int PDGId;
   double totE;
   double KE;
   double x;
   double y;
   double z;
   double rxy;
   double px;
   double py;
   double pz;
   double pT;
   double p;
   double tns;
   double weight;
};
""")

# Object storing various parameters
class parameters(object):

    def __init__(self, workName = 'FSoRT', flukaVer = 'fluka4-5.0', flairVer = 'flair-3.4-3'):

        # Storage area for batch job output
        self.user = os.getenv('USER')
        self.storage = '/exp/dune/data/users/jback/FlukaArchive'.format(self.user)
        self.baseJob = '{0}/{1}/{2}'.format(self.storage, flukaVer, workName)

        
def processArgs(parser):

    # Fluka input file name without the .inp extension
    parser.add_argument('--inName', default='LBNFBaffleJul25', metavar='name', help='Fluka input file name (without .inp)')

    # Number of jobs
    parser.add_argument('--nJobs', default=100, metavar='n', type=int, help='Number of jobs to submit, default = 100')

    # Beam run option
    parser.add_argument('--option', default=1, metavar='n', type=int, help='Beam run option, default = 1 (nominal)')
    

def run():

    # Process the command line arguments. Use "python createROOTFiles.py --help" to see the full list
    parser = argparse.ArgumentParser(description='List of arguments')
    processArgs(parser)
    args = parser.parse_args()

    # Various other parameters
    pars = parameters()

    # Create the ROOT file storing the track output over all jobs
    createROOTFile(args, pars)


def createROOTFile(args, pars):

    rootFileName = '{0}/{1}_Opt{2}_All/{1}_Opt{2}_Trk.root'.format(pars.baseJob, args.inName, args.option)

    # Create ROOT file
    print('Creating {0}\n'.format(rootFileName))
    rootFile = ROOT.TFile.Open(rootFileName, 'recreate')
    rootFile.cd()

    # Create TTree (ntuple) called "Data"
    data = ROOT.TTree('Data', 'Data')
    # Link this TTree to the file
    data.SetDirectory(rootFile)

    # Define data structure
    fS = ROOT.FlukaStruct()

    # Create branches that will store the data in the TTree:
    # branch name, address of variable, variable name and type
    # where I = integer and D = double
    data.Branch('iJob', cast['void*'](ROOT.addressof(fS, 'iJob')), 'iJob/I')
    data.Branch('iEvt', cast['void*'](ROOT.addressof(fS, 'iEvt')), 'iEvt/I')
    data.Branch('PDGId', cast['void*'](ROOT.addressof(fS, 'PDGId')), 'PDGId/I')
    data.Branch('totE', cast['void*'](ROOT.addressof(fS, 'totE')), 'totE/D')
    data.Branch('KE', cast['void*'](ROOT.addressof(fS, 'KE')), 'KE/D')
    data.Branch('x', cast['void*'](ROOT.addressof(fS, 'x')), 'x/D')
    data.Branch('y', cast['void*'](ROOT.addressof(fS, 'y')), 'y/D')
    data.Branch('z', cast['void*'](ROOT.addressof(fS, 'z')), 'z/D')
    data.Branch('rxy', cast['void*'](ROOT.addressof(fS, 'rxy')), 'rxy/D')
    data.Branch('px', cast['void*'](ROOT.addressof(fS, 'px')), 'px/D')
    data.Branch('py', cast['void*'](ROOT.addressof(fS, 'py')), 'py/D')
    data.Branch('pz', cast['void*'](ROOT.addressof(fS, 'pz')), 'pz/D')
    data.Branch('pT', cast['void*'](ROOT.addressof(fS, 'pT')), 'pT/D')
    data.Branch('p', cast['void*'](ROOT.addressof(fS, 'p')), 'p/D')
    data.Branch('tns', cast['void*'](ROOT.addressof(fS, 'tns')), 'tns/D')
    data.Branch('weight', cast['void*'](ROOT.addressof(fS, 'weight')), 'weight/D')

    # Loop over jobs.
    # Each job should have the same number of events    
    for iJob in range(args.nJobs):

        # Specify Fluka BXDRAW output file
        dirName = '{0}/{1}_Opt{2}_{3}'.format(pars.baseJob, args.inName, args.option, iJob)
        textFile = '{0}/{1}001_data.txt'.format(dirName, args.inName)

        print('Processing {0}'.format(textFile))

        # Open BXDRAW text file and read its contents
        with open(textFile, 'r') as inputFile:

            # Loop over each output line
            for line in inputFile:

                # Store space-separated line entries in an array
                arr = line.split()

                # Check that we have the correct number of words on the line.
                # Otherwise we could get errors if we try to access missing entries
                if (len(arr) < 12):
                    print('Expecting 12 words\n')
                    continue

                # Set the variables using the array entries:
                
                # Job and event numbers, as well as the particle ID integer
                fS.iJob = iJob
                fS.iEvt = int(arr[0])
                partId = int(arr[1])
                fS.PDGId = getPDGId(partId)

                # Total energy and KE (GeV)
                fS.totE = float(arr[2])
                fS.KE = float(arr[3])

                # Weight and position (cm)
                fS.weight = float(arr[4])
                fS.x = float(arr[5])
                fS.y = float(arr[6])
                fS.z = float(arr[7])
                fS.rxy = math.sqrt(fS.x*fS.x + fS.y*fS.y)
                
                # Direction cosines (particle direction w.r.t given axis)
                cosx = float(arr[8])
                cosy = float(arr[9])
                cosz = float(arr[10])
                
                # Momentum (GeV)
                pSq = fS.KE*(2.0*fS.totE - fS.KE)
                if pSq > 0.0:
                    fS.p = math.sqrt(pSq)
                else:
                    fS.p = 0.0

                # Momentum components (using direction cosines)
                fS.px = fS.p*cosx
                fS.py = fS.p*cosy
                fS.pz = fS.p*cosz
                # Transverse (x-y) momentum
                fS.pT = math.sqrt(fS.px*fS.px + fS.py*fS.py)
                
                # Lifetime (nanosecs)
                fS.tns = float(arr[11])*1e9

                # Fill the TTree branch entries using the data structure
                data.Fill()

    # Write data ntuple to ROOT file and close it
    print('Writing {0}'.format(rootFile))
    data.Write()
    rootFile.Close()

    
def getPDGId(partId):

    # Get the PDG integer from the Fluka id
    pdgId = 0
    
    if partId == 1:
        pdgId = 2212 # proton
    elif partId == 8:
        pdgId = 2112 # neutron
    elif partId == 13:
        pdgId = 211 # pi+
    elif partId == 14:
        pdgId = -211 # pi-
    elif partId == 23:
        pdgId = 111 # pi0
    elif partId == 15:
        pdgId = 321 # K+
    elif partId == 16:
        pdgId = -321 # K-
    elif partId == 19 or partId == 24 or partId == 25:
        pdgId = 310 # K0s, K0 or K0bar
    elif partId == 12:
        pdgId = 130 # K0L
    elif partId == 10:
        pdgId = -13 # mu+
    elif partId == 11:
        pdgId = 13 # mu-
    else:
        print('Using PDGId = {0} for PID partId = {1}'.format(pdgId, partId))
        
    return pdgId


def getMass(PDGId):

    # Get the particle rest mass for important PDGId's
    mass = 0.0

    if (PDGId == 2212):
        mass = 0.938272 # proton

    elif (PDGId == 2112):
        mass = 0.939565 # neutron

    elif (abs(PDGId) == 211):
        mass = 0.139570 # pi+-

    elif (PDGId == 111):
        mass = 0.134977 # pi0

    elif (abs(PDGId) == 321):
        mass = 0.493677 # K+-

    elif (PDGId == 310 or PDGId == 130):
        mass = 0.497614 # K0

    elif (abs(PDGId) == 13):
        mass = 0.105658 # mu+-

    else:
        print('getMass: Ignored PDGId {0}'.format(PDGId))

    return mass
  

# "Main" program that runs the above python code
if __name__ == '__main__':

    run()
