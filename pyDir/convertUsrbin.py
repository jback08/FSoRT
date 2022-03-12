#!/usr/bin/python

# Script to convert the combined usrbin histogram files to ascii format

import os
import sys

class parameters(object):

    def __init__(self, label):

        self.label = label
        self.baseDir = 'FlukaArchive/fluka4-2.1/FSoRT'
        self.combDir = self.baseDir + '/' + self.label + 'All'

def run(pars):
    
    runFile = open('runConvertUsrbin.sh', 'w')

    # Directory where the combined results are located
    print('combDir = {0}'.format(pars.combDir))

    usrBins = range(21, 72) # energy & DPA
    usrBins += [94] # baffle energy
    print('usrBins = {0}'.format(usrBins))

    for i,iFile in enumerate(usrBins):
            
        convName = createScript(iFile, pars)
        runFile.write('sh {0}\n'.format(convName))

    runFile.close()
        
def createScript(iFile, pars):

    fileName = '{0}001_fort.{1}'.format(pars.label, iFile)
    asciiName = '{0}.txt'.format(fileName)

    convName = 'convert{0}.sh'.format(iFile)
    convFile = open(convName, 'w')

    line = '$FLUPRO/bin/usbrea << EOF\n'
    convFile.write(line)

    binName = '{0}/{1}\n'.format(pars.combDir, fileName)
    convFile.write(binName)

    line = '{0}/{1}\n'.format(pars.combDir, asciiName)
    convFile.write(line)

    convFile.write('EOF\n')
    convFile.close()

    return convName


if __name__ == "__main__":

    label = 'LBNFTgtL150cmFinsBaf'
    nJobs = 100

    nArg = len(sys.argv)
    if (nArg > 1):
        label = sys.argv[1]

    pars = parameters(label)
    run(pars)
