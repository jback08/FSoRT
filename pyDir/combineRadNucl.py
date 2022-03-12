#! /usr/bin/python

# Script to combine Fluka job output (@Fermilab) for the target area radionuclides,
# which also provides estimates of decay products for given exposure/decay times

import os
import sys

class parameters(object):

    def __init__(self, label, nJobs):

        self.label = label
        self.baseDir = 'FlukaArchive/fluka4-2.1/FSoRT'
        self.nJobs = nJobs

        # Beam and runtime parameters
        self.runYrDays = 204.5 # Run days per calendar year
        self.daySecs = 24.0*3600.0 # Seconds in 1 day
        self.yearSecs = self.daySecs*365.25 # Seconds in 1 year
        
        self.runYrSecs = self.runYrDays*self.daySecs # Run year in seconds
        
        # Beam intensity (POT/yr) at 120 GeV
        self.POTYr = 1.1e21
        self.POTSec = self.POTYr/self.runYrSecs # POT/sec

        # Decay times (in seconds): 1 hr, 8 hrs, 1 day, 7 days,
        # 1 month (30 days), 6 months, 1 year, 2 years, 3 years,
        # 5 years, 10 years, 50 years
        self.decTimes = [self.daySecs/24.0, self.daySecs/3.0, self.daySecs,
                         7.0*self.daySecs, 30.0*self.daySecs, self.yearSecs/2.0,
                         self.yearSecs, 2.0*self.yearSecs, 3.0*self.yearSecs,
                         5.0*self.yearSecs, 10.0*self.yearSecs, 50.0*self.yearSecs]
        
def run(pars, doExtract):
    
    runFile = open('runCombineRadNucl.sh', 'w')
    print('POT per sec = {0}'.format(pars.POTSec))

    # Create combined directory if it does not exist
    combDir = pars.baseDir + '/' + pars.label + 'All'

    if (os.path.isdir(combDir) == False):
        print 'Creating {0}'.format(combDir)
        os.makedirs(combDir)

    # First extract all of the tarball files
    if doExtract:
        for iJob in range(1, pars.nJobs+1):

            jobName = '{0}_{1}'.format(pars.label, iJob)
            jobDir = '{0}/{1}'.format(pars.baseDir, jobName)
            tarCmd = 'tar -zxf {0}/binList.tar.gz -C {0}'.format(jobDir)
            os.system(tarCmd)

    # Specify list of rad nuclei usrbin regional info (same for all jobs): min, max+1
    radList = range(72, 94)
    print('radList = {0}'.format(radList))

    for iR,radIdx in enumerate(radList):

        combName = createScript(radIdx, combDir, pars)
        runFile.write('sh {0}\n'.format(combName))

    runFile.close()


def createScript(radIdx, combDir, pars):

    # usrbin integer from filename
    binFile = '{0}001_fort.{1}'.format(pars.label, radIdx)

    combName = 'radNucl{0}.sh'.format(radIdx)
    combFile = open(combName, 'w')

    combFile.write('$FLUPRO/bin/usrsuwev << EOF\n')
    combFile.write('yes\n')
    combFile.write('{0:.6e}\n'.format(pars.POTSec))

    for iJob in range(1, pars.nJobs+1):

        binName = '{0}/{1}_{2}/{3}\n'.format(pars.baseDir, pars.label, iJob, binFile)
        combFile.write(binName)

    combFile.write('\n')
    regName = getRegionName(radIdx)
    # Radionuclides
    combFile.write('{0}/{1}RadNuclides\n'.format(combDir, regName))
    # Irradiation time (secs)
    combFile.write('{0:.6e}\n'.format(pars.runYrSecs))
    # Induced activity as a function of decay time
    combFile.write('{0}/{1}Evolution\n'.format(combDir, regName))

    # Decay times (seconds)
    for iT,time in enumerate(pars.decTimes):
        combFile.write('{0:.6e}\n'.format(time))

    combFile.write('-1\n')
    combFile.write('EOF\n')
    combFile.close()

    return combName


def getRegionName(radIdx):

    name = 'Void'
    if radIdx == 72:
        name = 'H1Out'
    elif radIdx == 73:
        name = 'H1In'
    elif radIdx == 74:
        name = 'H1End'
    elif radIdx == 75:
        name = 'H1Plate'
    elif radIdx == 76:
        name = 'H1Ceram'
    elif radIdx == 77:
        name = 'H1Gas1'
    elif radIdx == 78:
        name = 'H1Gas2'
    elif radIdx == 79:
        name = 'BeamGas'
    elif radIdx == 80:
        name = 'H1Gas3'
    elif radIdx == 81:
        name = 'H1Cool'
    elif radIdx == 82:
        name = 'TFlow'
    elif radIdx == 83:
        name = 'TCont'
    elif radIdx == 84:
        name = 'TWindow'
    elif radIdx == 85:
        name = 'BafCont'
    elif radIdx == 86:
        name = 'BafGas'
    elif radIdx == 87:
        name = 'TGas1'
    elif radIdx == 88:
        name = 'TGas2'
    elif radIdx == 89:
        name = 'TGas3'
    elif radIdx == 90:
        name = 'Target'
    elif radIdx == 91:
        name = 'Bafflet'
    elif radIdx == 92:
        name = 'TFins'
    elif radIdx == 93:
        name = 'UpWindow'

    return name

        
if __name__ == "__main__":

    targetLabel = 'LBNFTgtL150cmFinsBaf'
    nJobs = 100

    nArg = len(sys.argv)
    if (nArg > 1):
        targetLabel = sys.argv[1]
    if (nArg > 2):
        nJobs = int(sys.argv[2])

    pars = parameters(targetLabel, nJobs)
    doExtract = False
    run(pars, doExtract)

