#!/usr/bin/python

# Python script to print out the summary baffle & TPT EDep info.
# Includes primary beam window (PBW)

import math
import numpy as np
import ROOT

def run():

    baseDir = 'baffleData'
    labels = ['LBNFBaffleTPTSept25', 'LBNFTgtL150cmSept25']
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

                (gas2P, gas2PErr) = getSum(powerArr, powerErrArr, 32, 33)
                print('gas2P = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(gas2P, gas2PErr, gas2P*1e-3, gas2PErr*1e-3))

                (tptGasP, tptGasPErr) = getSum(powerArr, powerErrArr, 33, 35)
                print('tptGasP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptGasP, tptGasPErr, tptGasP*1e-3, tptGasPErr*1e-3))

                (tptCeramP, tptCeramPErr) = getSum(powerArr, powerErrArr, 35, 36)
                print('tptCeramP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptCeramP, tptCeramPErr, tptCeramP*1e-3, tptCeramPErr*1e-3))
                
                (tptP, tptPErr) = getSum(powerArr, powerErrArr, 36, 37)
                print('tptP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptP, tptPErr, tptP*1e-3, tptPErr*1e-3))

                (tptBoxP, tptBoxPErr) = getSum(powerArr, powerErrArr, 37, 38)
                print('tptBoxP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptBoxP, tptBoxPErr, tptBoxP*1e-3, tptBoxPErr*1e-3))

                (tptBracP, tptBracPErr) = getSum(powerArr, powerErrArr, 38, 39)
                print('tptBracP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptBracP, tptBracPErr, tptBracP*1e-3, tptBracPErr*1e-3))

                # The 2nd TPT gas region can have a different number
                tptGas2Idx = 39
                if label == 'LBNFTgtL150cmSept25':
                    tptGas2Idx = 45
                (tptGas2P, tptGas2PErr) = getSum(powerArr, powerErrArr, tptGas2Idx, tptGas2Idx+1)
                print('tptGas2P = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptGas2P, tptGas2PErr, tptGas2P*1e-3, tptGas2PErr*1e-3))

                tptGasPArr = [tptGasP, tptGas2P]
                tptGasPErrArr = [tptGasPErr, tptGas2PErr]
                (tptGasAllP, tptGasAllPErr) = getSum(tptGasPArr, tptGasPErrArr, 0, 2)
                print('tptGasAllP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptGasAllP, tptGasAllPErr, tptGasAllP*1e-3, tptGasAllPErr*1e-3))

                (tptAllP, tptAllPErr) = getSum(powerArr, powerErrArr, 33, 39)
                tptAllP += tptGas2P
                tptAllPErr = math.sqrt(tptAllPErr*tptAllPErr + tptGas2PErr*tptGas2PErr)
                print('tptAllP = {0:.3f} +- {1:.3f} W = {2:4f} +- {3:.3f} kW'.format(tptAllP, tptAllPErr, tptAllP*1e-3, tptAllPErr*1e-3))

                print('\n')
                
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
