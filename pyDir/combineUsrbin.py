#! /usr/bin/python

# Script to combine usrbin EDep Fluka histogram files.
# First, manually copy scratch directories to the data area,
# then this extracts and combines the tarball files.
# Tarball also contains the EDep & tracking text files

import os
import sys

class parameters(object):

    def __init__(self, label, nJobs):

        self.label = label
        self.baseDir = 'FlukaArchive/fluka4-2.1/FSoRT'
        self.nJobs = nJobs

def run(pars):
    
    runFile = open('runCombineUsrbin.sh', 'w')

    # Create combined directory if it does not exist
    combDir = pars.baseDir + '/' + pars.label + 'All'

    if (os.path.isdir(combDir) == False):
        print 'Creating {0}'.format(combDir)
        os.makedirs(combDir)

    # First extract all of the tarball files
    for iJob in range(1, pars.nJobs+1):

        jobName = '{0}_{1}'.format(pars.label, iJob)
        jobDir = '{0}/{1}'.format(pars.baseDir, jobName)
        print('Extracting {0}'.format(jobDir))
        tarCmd = 'tar -zxf {0}/binList.tar.gz -C {0}'.format(jobDir)
        os.system(tarCmd)

    # Specify list of usrbin histograms (same for all jobs): min, max+1
    usrBins = range(21, 95)
    print('usrBins = {0}'.format(usrBins))

    for iB,binIdx in enumerate(usrBins):

        combName = createScript(binIdx, combDir, pars)
        runFile.write('sh {0}\n'.format(combName))

    runFile.close()


def createScript(binIdx, combDir, pars):

    # usrbin integer from filename
    binFile = '{0}001_fort.{1}'.format(pars.label, binIdx)

    combName = 'combine{0}.sh'.format(binIdx)
    combFile = open(combName, 'w')

    line = '$FLUPRO/bin/usbsuw << EOF\n'
    combFile.write(line)

    for iJob in range(1, pars.nJobs+1):

        binName = '{0}/{1}_{2}/{3}\n'.format(pars.baseDir, pars.label, iJob, binFile)
        combFile.write(binName)

    combFile.write('\n')
    line = '{0}/{1}\n'.format(combDir, binFile)
    combFile.write(line)

    combFile.write('EOF\n')
    combFile.close()

    return combName


if __name__ == "__main__":

    targetLabel = 'LBNFTgtL150cmFinsBaf'
    nJobs = 100

    nArg = len(sys.argv)
    if (nArg > 1):
        targetLabel = sys.argv[1]
    if (nArg > 2):
        nJobs = int(sys.argv[2])

    pars = parameters(targetLabel, nJobs)
    run(pars)

