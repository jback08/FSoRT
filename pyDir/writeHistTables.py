#!/usr/bin/python

# Convert the fluka ascii histogram data files to a more
# readable format:
# z r value

import os
import sys

def run(targetLabel, fileIndex):

    # Create histTables directory if it does not exist
    histDir = 'histTables'
    if (os.path.isdir(histDir) == False):
        print 'Creating {0}'.format(histDir)
        os.makedirs(histDir)

    inFileName = 'converted/{0}001_fort.{1}.txt'.format(targetLabel, fileIndex)

    rMin = 0.0
    rMax = 0.0
    nR = 0
    dR = 0.0
    zMin = 0.0
    zMax = 0.0
    nZ = 0
    dZ = 0.0
    outName = 'output'

    # Read the header binning information from the input file
    with open(inFileName, 'r') as inFile:

        iLine = 0

        for line in inFile:
            iLine += 1

            words = line.rstrip('\n').split()
            print 'iLine = {0}: words = {1}'.format(iLine, words)

            if iLine == 2:

                outName = words[6].replace('"', '')

            elif iLine == 3:

                minR = float(words[3])
                maxR= float(words[5])
                nR = int(words[7])]
                dR = float(words[10])

            elif iLine == 4:

                minZ = float(words[3])
                maxZ = float(words[5])
                nZ = int(words[7])]
                dZ = float(words[10])

            elif iLine > 4:
                break
    
    print 'Name = {0}, r = {1}, {2}, {3}, {4}; z = {5}, {6}, {7}, {8}'.format(outName, minR, maxR, nR, dR,
                                                                              minZ, maxZ, nZ, dZ)

    nTotBins = nR*nZ
    nFullLines = nTotBins/10
    nRemain = nTotBins%10
    print 'nTotBins = {0}, nFullLines = {1}, nRemain = {2}'.format(nTotBins, nFullLines, 
                                                                   nRemain)

    # Process input file again, this time extracting the binned data
    startIdx = 0
    with open(inFileName, 'r') as inFile:

        iLine = 0

        for line in inFile:
            iLine += 1

            if iLine > 8:

                words = line.rstrip('\n').split()
                nWords = len(words)

                for iCol in range(nWords):

                    dataIndex = startIdx + iCol
                    rIndex = dataIndex%nR
                    zIndex = dataIndex/nR

                    r1 = rIndex*dR + minR
                    r2 = r1 + dR
                    z1 = zIndex*dZ + minZ
                    z2 = z1 + dZ

                    value = float(words[iCol])


    #outFileName = 'histTables/{0}'.format(outName)
    #outFile.close()


if __name__ == "__main__":

    targetLabel = 'DoubleTarget'
    fileIndex = 21

    nArg = len(sys.argv)

    if (nArg > 1):
        targetLabel = sys.argv[1]

    if (nArg > 2):
        fileIndex = int(sys.argv[2])

    run(targetLabel, fileIndex)
