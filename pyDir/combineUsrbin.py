#! /usr/bin/python

# Script to combine usrbin EDep Fluka histogram files.
# First, copy the scratch directories to the data area,
# then extract and combine the tarball files

import os
import sys

class parameters(object):

    def __init__(self, label, option, nJobs):

        self.label = label
        self.versionDir = 'FlukaArchive/fluka4-5.0/FSoRT'
        self.scratchDir = '/pnfs/dune/scratch/users/jback/{0}'.format(self.versionDir)
        self.dataBaseDir = '/exp/dune/data/users/jback/{0}'.format(self.versionDir)
        self.option = option
        self.nJobs = nJobs


def run(pars):
    
    runFile = open('runCombineUsrbin.sh', 'w')

    # Create combined directory if it does not exist
    combDir = pars.dataBaseDir + '/' + pars.label + '_Opt{0}_'.format(pars.option) + 'All'

    if (os.path.isdir(combDir) == False):
        print('Creating {0}'.format(combDir))
        os.makedirs(combDir)

    # Copy the job dirs then extract their tarball files
    for iJob in range(pars.nJobs):

        jobName = '{0}_Opt{1}_{2}'.format(pars.label, pars.option, iJob)
        jobDir = '{0}/{1}'.format(pars.scratchDir, jobName)
        dataDir = '{0}/{1}'.format(pars.dataBaseDir, jobName)

        # May need to get token using command:
        # htgettoken -i dune --vaultserver htvaultprod.fnal.gov
        if (os.path.isdir(dataDir) == False):
            runFile.write('echo Copying {0} to {1}\n'.format(jobDir, dataDir))
            line = 'ifdh cp --proxy_enable=0 --token_enable=1 -D {0} {1}\n'.format(jobDir, pars.dataBaseDir)
            runFile.write(line)

        # Check if the files have already been extracted
        outFile = '{0}/{1}001.out'.format(dataDir, pars.label)
        if (os.path.isfile(outFile) == False):
            runFile.write('echo Extracting {0}\n'.format(dataDir))
            tarCmd = 'tar -zxf {0}/binList.tar.gz -C {0}\n'.format(dataDir)
            runFile.write(tarCmd)

    # Specify list of usrbin histograms (same for all jobs)
    usrBins = list(range(21,36)) + list(range(41, 55))
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

    for iJob in range(pars.nJobs):

        binName = '{0}/{1}_Opt{2}_{3}/{4}\n'.format(pars.dataBaseDir, pars.label, pars.option, iJob, binFile)
        combFile.write(binName)

    combFile.write('\n')
    line = '{0}/{1}\n'.format(combDir, binFile)
    combFile.write(line)

    combFile.write('EOF\n')
    combFile.close()

    return combName


if __name__ == "__main__":

    targetLabel = 'LBNFBaffleSept25'
    option = 1
    nJobs = 100

    nArg = len(sys.argv)
    if (nArg > 1):
        targetLabel = sys.argv[1]
    if (nArg > 2):
        option = sys.argv[2]
    if (nArg > 3):
        nJobs = int(sys.argv[3])

    pars = parameters(targetLabel, option, nJobs)
    run(pars)

