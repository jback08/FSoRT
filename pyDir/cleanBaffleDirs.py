#! /usr/bin/python

# Script to cleanup the extracted job data files to save disk space.
# Only run this after all files have been merged & processed

import os
import sys

class parameters(object):

    def __init__(self, label, option, nJobs):

        self.label = label
        self.versionDir = 'FlukaArchive/fluka4-5.0/FSoRT'
        self.dataBaseDir = '/exp/dune/data/users/jback/{0}'.format(self.versionDir)
        self.option = option
        self.nJobs = nJobs


def run(pars):
    
    runFile = open('cleanBaffleDirs.sh', 'w')

    # Loop over the data dirs
    for iJob in range(pars.nJobs):

        jobName = '{0}_Opt{1}_{2}'.format(pars.label, pars.option, iJob)
        dataDir = '{0}/{1}'.format(pars.dataBaseDir, jobName)        
        runFile.write('cd {0}\n'.format(dataDir))
        runFile.write('rm {0}001*\n'.format(pars.label))
        runFile.write('cd -\n')

    runFile.close()


if __name__ == "__main__":

    targetLabel = 'LBNFBaffleJul25'
    #targetLabel = 'LBNFBaffleTPTJul25'
    #targetLabel = 'LBNFTgtL150cmJul25'
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

