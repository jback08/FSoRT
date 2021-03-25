#!/usr/bin/python

# Script to convert the combined usrbin histogram files to ascii format

import os
import sys

def run(targetLabel):
    
    runFile = open('runConvertUsrbin.sh', 'w')

    # Create converted directory if it does not exist
    convDir = 'converted'
    if (os.path.isdir(convDir) == False):
        print 'Creating {0}'.format(convDir)
        os.makedirs(convDir)

    usrBins = ['21', '22', '23', '24', '25', '26', '27', '28', '29', 
               '31', '32', '33', '34', '35', '36', '37', '38', '50']

    for i,iFile in enumerate(usrBins):
            
        convName = createScript(iFile, targetLabel)
        runFile.write('sh {0}\n'.format(convName))

    runFile.close()
        
def createScript(iFile, targetLabel):

    fileName = '{0}001_fort.{1}'.format(targetLabel, iFile)
    asciiName = '{0}.txt'.format(fileName)

    convName = 'convert{0}.sh'.format(iFile)
    convFile = open(convName, 'w')

    line = '$FLUPRO/flutil/usbrea << EOF\n'
    convFile.write(line)

    binName = 'combined/{0}\n'.format(fileName)
    convFile.write(binName)

    line = 'converted/{0}\n'.format(asciiName)
    convFile.write(line)

    convFile.write('EOF\n')
    convFile.close()

    return convName


if __name__ == "__main__":

    targetLabel = 'DoubleTarget'
    nArg = len(sys.argv)

    if (nArg > 1):
        targetLabel = sys.argv[1]

    run(targetLabel)
