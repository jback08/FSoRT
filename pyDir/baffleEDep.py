#!/usr/bin/python

# Python script to print out the summary baffle EDep info

import math
import numpy as np
import ROOT

def run():

    baseDir = 'baffleData'
    labels = ['LBNFBaffleJul25', 'LBNFBaffleTPTJul25', 'LBNFTgtL150cmJul25']
    options = np.array([1, 2, 3, 4])
    probScale = 1.0
    
    for iL,label in enumerate(labels):

        for iO,option in enumerate(options):

            rootName = '{0}/{1}_Opt{2}_All/{1}_Opt{2}_EDep.root'.format(baseDir, label, option)
            print('rootName is {0}\n'.format(rootName))

            # 1% beam scraping cases
            probScale = 1.0
            if option == 2 or option == 3:
                probScale = 0.01            

            print('Option {0} probScale = {1}'.format(option, probScale))
            rootFile = ROOT.TFile.Open(rootName, 'r')
            data = rootFile.Get('Data')

            nData = data.GetEntries()
            for iD in range(nData):

                data.GetEntry(iD)
            
                powerArr = np.array(getattr(data, 'Power'))*probScale
                powerErrArr = np.array(getattr(data, 'PowerErr'))*probScale
                #print('powerArr = {0}'.format(powerArr))

                (mainP, mainPErr) = getSum(powerArr, powerErrArr, 2, 7)
                print('mainP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(mainP, mainPErr, mainP*1e-3, mainPErr*1e-3))

                (finsP, finsPErr) = getSum(powerArr, powerErrArr, 7, 12)
                print('finsP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(finsP, finsPErr, finsP*1e-3, finsPErr*1e-3))

                (ringsP, ringsPErr) = getSum(powerArr, powerErrArr, 12, 18)
                print('ringsP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(ringsP, ringsPErr, ringsP*1e-3, ringsPErr*1e-3))

                (ductP, ductPErr) = getSum(powerArr, powerErrArr, 18, 19)
                print('ductP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(ductP, ductPErr, ductP*1e-3, ductPErr*1e-3))

                (gasP, gasPErr) = getSum(powerArr, powerErrArr, 19, 28)
                print('gasP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(gasP, gasPErr, gasP*1e-3, gasPErr*1e-3))

                (allP, allPErr) = getSum(powerArr, powerErrArr, 2, 28)
                print('allP = {0:.3f} +- {1:.3f} W = {2:4f} +- {3:.3f} kW \n\n'.format(allP, allPErr, allP*1e-3, allPErr*1e-3))
                
            rootFile.Close()


def getSum(powerArr, powerErrArr, index1, index2):

    # Sum array elements from index1 to index2-1 (last index needs to be index2)
    values = powerArr[index1:index2]
    errors = powerErrArr[index1:index2]

    # Sum & its quadrature error
    total = sum(values)
    error = math.sqrt(sum(x*x for x in errors))

    return (total, error)


if __name__ == "__main__":

    run()
