#!/usr/bin/python

# Script to convert the combined usrbin histogram files to ascii format

import os
import sys

class parameters(object):

    def __init__(self, label, option):

        self.label = label
        self.option = option
        self.baseDir = '/exp/dune/data/users/jback/FlukaArchive/fluka4-5.0/FSoRT'


def run(pars):
    
    runFile = open('runConvertUsrbin.sh', 'w')

    # Directory where the combined results are located
    combDir = pars.baseDir + '/' + pars.label + '_Opt{0}_'.format(pars.option) + 'All'
    print('combDir = {0}'.format(combDir))

    usrBins = list(range(21,36)) + list(range(41, 55))
    print('usrBins = {0}'.format(usrBins))

    for i,binIdx in enumerate(usrBins):
            
        convName = createScript(binIdx, combDir, pars)
        runFile.write('sh {0}\n'.format(convName))

    runFile.close()
        

def createScript(binIdx, combDir, pars):

    fileName = '{0}001_fort.{1}'.format(pars.label, binIdx)
    asciiName = '{0}.txt'.format(fileName)

    convName = 'convert{0}.sh'.format(binIdx)
    convFile = open(convName, 'w')

    line = '$FLUPRO/bin/usbrea << EOF\n'
    convFile.write(line)

    binName = '{0}/{1}\n'.format(combDir, fileName)
    convFile.write(binName)

    line = '{0}/{1}\n'.format(combDir, asciiName)
    convFile.write(line)

    convFile.write('EOF\n')
    convFile.close()

    return convName


if __name__ == "__main__":

    label = 'LBNFBaffleSept25'
    #label = 'LBNBaffleTPTSept2525'
    #label = 'LBNFTgtL150cmSept25'
    option = 1

    nArg = len(sys.argv)
    if (nArg > 1):
        label = sys.argv[1]
    if (nArg > 2):
        option = sys.argv[2]

    pars = parameters(label, option)
    run(pars)
