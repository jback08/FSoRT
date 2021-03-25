#!/bin/python

# Python script to extract the radionuclide rates (Bq) from
# the X_res.lis outputfiles to a simpler format that can be
# processed by the decays.cc ROOT program

import os
import sys

def run(evoLabel, dirName):

    print('Running extractNuclides for {0}; dir = {1}'.format(evoLabel, dirName))

    resFileName = '{0}/{1}Evolution_res.lis'.format(dirName, evoLabel)
    outFileName = '{0}/{1}Evolution.txt'.format(dirName, evoLabel)
    
    print('Placing info from {0} into {1}'.format(resFileName, outFileName))

    (detector, volume) = getDetector(resFileName)
    print('Detector = {0}, volume = {1} cmc'.format(detector, volume))
    
    # Process and write out the evolution data
    outFile = open(outFileName, 'w')
    outFile.write('Detector is {0}\n'.format(detector))
    outFile.write('Volume is {0} cm3\n'.format(volume))
    
    with open(resFileName, 'r') as resFile:
        
        for line in resFile:

            sLine = line.split()

            if 'Decay time' in line:
                time = float(sLine[3])
                outFile.write('Time is {0} seconds\n'.format(time))

            elif 'Tot. response' in line:
                response = float(sLine[3])
                outFile.write('Total response is {0:.6e}\n'.format(response))

            elif len(sLine) == 8 and sLine[4] == '+/-' and sLine[2] != 'Bq':
                A = int(sLine[0])
                elem = sLine[1]
                Z = int(sLine[2])
                rate = float(sLine[3])
                halfLife = float(sLine[7])
                outFile.write('{0} {1} {2} {3:.6e} {4:.6e}\n'.format(A, elem, Z, rate,
                                                                     halfLife))
            elif len(sLine) == 9 and sLine[5] == '+/-':
                A = int(sLine[0])
                elem = sLine[1]
                Z = int(sLine[2])
                mth = int(sLine[3])
                rate = float(sLine[4])
                halfLife = float(sLine[8])
                outFile.write('Isomer {0} {1} {2} {3} {4:.6e} {5:.6e}\n'.format(A, elem, Z, mth,
                                                                                rate, halfLife))
              
    outFile.close()                


def getDetector(resFileName):

    # Get detector name and volume
    detector = ''
    volume = 0.0
    gotDetector = False
    gotVolume = False
    
    with open(resFileName, 'r') as resFile:
        
        for line in resFile:

            if gotDetector == True and gotVolume == True:
                break
            
            sLine = line.split()
            
            # Get detector
            if 'Detector' in line:
                detector = sLine[3]
                gotDetector = True

            elif 'Volume:' in line:
                volume = float(sLine[3])
                gotVolume = True
                
    return (detector, volume)

    
if __name__ == '__main__':

    evoLabel = 'Target'
    dirName = 'LBNFTargetL150cmSpacers'
    
    nArg = len(os.sys.argv)
    if nArg > 1:
        evoLabel = os.sys.argv[1]
    if nArg > 2:
        dirName = os.sys.argv[2]

    run(evoLabel, dirName)
