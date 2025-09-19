#!/usr/bin/python

# Python script to print out the summary baffle EDep info.
# Includes primary beam window (PBW)

import math
import numpy as np
import ROOT

def run():

    baseDir = 'baffleData'
    labels = ['LBNFBaffleSept25', 'LBNFBaffleTPTSept25', 'LBNFTgtL150cmSept25']
    options = np.array([1])
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
                
                (pwGasP, pwGasPErr) = getSum(powerArr, powerErrArr, 3, 4)
                print('pwGasP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(pwGasP, pwGasPErr, pwGasP*1e-3, pwGasPErr*1e-3))
                
                (pwSteelP, pwSteelPErr) = getSum(powerArr, powerErrArr, 4, 5)
                print('pwSteelP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(pwSteelP, pwSteelPErr,
                                                                                       pwSteelP*1e-3, pwSteelPErr*1e-3))

                (PBWP, PBWPErr) = getSum(powerArr, powerErrArr, 5, 6)
                print('PBWP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(PBWP, PBWPErr, PBWP*1e-3, PBWPErr*1e-3))
                
                (mainP, mainPErr) = getSum(powerArr, powerErrArr, 6, 11)
                print('mainP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(mainP, mainPErr, mainP*1e-3, mainPErr*1e-3))

                (finsP, finsPErr) = getSum(powerArr, powerErrArr, 11, 16)
                print('finsP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(finsP, finsPErr, finsP*1e-3, finsPErr*1e-3))

                (ringsP, ringsPErr) = getSum(powerArr, powerErrArr, 16, 22)
                print('ringsP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(ringsP, ringsPErr, ringsP*1e-3, ringsPErr*1e-3))

                (ductP, ductPErr) = getSum(powerArr, powerErrArr, 22, 23)
                print('ductP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(ductP, ductPErr, ductP*1e-3, ductPErr*1e-3))

                (gasP, gasPErr) = getSum(powerArr, powerErrArr, 23, 32)
                print('gasP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(gasP, gasPErr, gasP*1e-3, gasPErr*1e-3))

                (allP, allPErr) = getSum(powerArr, powerErrArr, 2, 32)
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
