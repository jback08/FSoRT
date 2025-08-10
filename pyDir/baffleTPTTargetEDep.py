#!/usr/bin/python

# Python script to print out the summary baffle, TPT & target EDep info

import math
import numpy as np
import ROOT

def run():

    baseDir = 'baffleData'
    labels = ['LBNFTgtL150cmJul25']
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
                print('allP = {0:.3f} +- {1:.3f} W = {2:4f} +- {3:.3f} kW'.format(allP, allPErr, allP*1e-3, allPErr*1e-3))

                (gas2P, gas2PErr) = getSum(powerArr, powerErrArr, 28, 29)
                print('gas2P = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(gas2P, gas2PErr, gas2P*1e-3, gas2PErr*1e-3))

                (tptGasP, tptGasPErr) = getSum(powerArr, powerErrArr, 29, 31)
                print('tptGasP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptGasP, tptGasPErr, tptGasP*1e-3, tptGasPErr*1e-3))

                (tptCeramP, tptCeramPErr) = getSum(powerArr, powerErrArr, 31, 32)
                print('tptCeramP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptCeramP, tptCeramPErr, tptCeramP*1e-3, tptCeramPErr*1e-3))
                
                (tptP, tptPErr) = getSum(powerArr, powerErrArr, 32, 33)
                print('tptP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptP, tptPErr, tptP*1e-3, tptPErr*1e-3))

                (tptBoxP, tptBoxPErr) = getSum(powerArr, powerErrArr, 33, 34)
                print('tptBoxP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptBoxP, tptBoxPErr, tptBoxP*1e-3, tptBoxPErr*1e-3))

                (tptBracP, tptBracPErr) = getSum(powerArr, powerErrArr, 34, 35)
                print('tptBracP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptBracP, tptBracPErr, tptBracP*1e-3, tptBracPErr*1e-3))

                # The 2nd TPT mount gas region
                (tptGas2P, tptGas2PErr) = getSum(powerArr, powerErrArr, 41, 42)
                print('tptGas2P = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptGas2P, tptGas2PErr, tptGas2P*1e-3, tptGas2PErr*1e-3))

                tptGasPArr = [tptGasP, tptGas2P]
                tptGasPErrArr = [tptGasPErr, tptGas2PErr]
                (tptGasAllP, tptGasAllPErr) = getSum(tptGasPArr, tptGasPErrArr, 0, 2)
                print('tptGasAllP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptGasAllP, tptGasAllPErr, tptGasAllP*1e-3, tptGasAllPErr*1e-3))

                (tptAllP, tptAllPErr) = getSum(powerArr, powerErrArr, 29, 35)
                tptAllP += tptGas2P
                tptAllPErr = math.sqrt(tptAllPErr*tptAllPErr + tptGas2PErr*tptGas2PErr)
                print('tptAllP = {0:.3f} +- {1:.3f} W = {2:4f} +- {3:.3f} kW'.format(tptAllP, tptAllPErr, tptAllP*1e-3, tptAllPErr*1e-3))

                # Start of target & horn region
                (tptMountP, tptMountPErr) = getSum(powerArr, powerErrArr, 35, 36)
                print('** tptMountP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(tptMountP, tptMountPErr, tptMountP*1e-3, tptMountPErr*1e-3))
                #(hornOutP, hornOutPErr) = getSum(powerArr, powerErrArr, 36, 37)
                #print('hornOutP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(hornOutP, hornOutPErr, hornOutP*1e-3, hornOutPErr*1e-3))

                #(hornInP, hornInPErr) = getSum(powerArr, powerErrArr, 37, 38)
                #print('hornInP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(hornInP, hornInPErr, hornInP*1e-3, hornInPErr*1e-3))
                
                #(hornEndP, hornEndPErr) = getSum(powerArr, powerErrArr, 38, 39)
                #print('hornEndP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(hornEndP, hornEndPErr, hornEndP*1e-3, hornEndPErr*1e-3))

                # All horn conductor surfaces
                (hornP, hornPErr) = getSum(powerArr, powerErrArr, 36, 39)
                print('hornP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(hornP, hornPErr, hornP*1e-3, hornPErr*1e-3))

                (hornGasP, hornGasPErr) = getSum(powerArr, powerErrArr, 39, 41)
                print('hornGasP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(hornGasP, hornGasPErr, hornGasP*1e-3, hornGasPErr*1e-3))
                
                (hornCoolP, hornCoolPErr) = getSum(powerArr, powerErrArr, 47, 48)
                print('hornCoolP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(hornCoolP, hornCoolPErr, hornCoolP*1e-3, hornCoolPErr*1e-3))

                (outGasP, outGasPErr) = getSum(powerArr, powerErrArr, 42, 47)
                print('outGasP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(outGasP, outGasPErr, outGasP*1e-3, outGasPErr*1e-3))

                (baffletP, baffletPErr) = getSum(powerArr, powerErrArr, 73, 74)
                print('baffletP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(baffletP, baffletPErr, baffletP*1e-3, baffletPErr*1e-3))

                (baffletContP, baffletContPErr) = getSum(powerArr, powerErrArr, 50, 51)
                print('baffletContP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(baffletContP, baffletContPErr,
                                                                                           baffletContP*1e-3, baffletContPErr*1e-3))

                #(baffletHeP, baffletHePErr) = getSum(powerArr, powerErrArr, 56, 57)
                #print('baffletHeP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(baffletHeP, baffletHePErr,
                #                                                                         baffletHeP*1e-3, baffletHePErr*1e-3))

                (flowP, flowPErr) = getSum(powerArr, powerErrArr, 48, 49)
                print('flowP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(flowP, flowPErr, flowP*1e-3, flowPErr*1e-3))

                (contP, contPErr) = getSum(powerArr, powerErrArr, 49, 50)
                print('contP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(contP, contPErr, contP*1e-3, contPErr*1e-3))

                # Target core & joins
                (targetP, targetPErr) = getSum(powerArr, powerErrArr, 68, 73)
                print('targetP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(targetP, targetPErr, targetP*1e-3, targetPErr*1e-3))

                #(targetJoinP, targetJoinPErr) = getSum(powerArr, powerErrArr, 69, 73)
                #print('targetJoinP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(targetJoinP, targetJoinPErr,
                #                                                                          targetJoinP*1e-3, targetJoinPErr*1e-3))

                (targetFinsP, targetFinsPErr) = getSum(powerArr, powerErrArr, 51, 54)
                print('targetFinsP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(targetFinsP, targetFinsPErr,
                                                                                          targetFinsP*1e-3, targetFinsPErr*1e-3))
                
                (targetHeP, targetHePErr) = getSum(powerArr, powerErrArr, 56, 68)
                print('targetHeP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(targetHeP, targetHePErr,
                                                                                          targetHeP*1e-3, targetHePErr*1e-3))

                (USWinP, USWinPErr) = getSum(powerArr, powerErrArr, 55, 56)
                print('USWinP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(USWinP, USWinPErr, USWinP*1e-3, USWinPErr*1e-3))

                (DSWinP, DSWinPErr) = getSum(powerArr, powerErrArr, 54, 55)
                print('DSWinP = {0:.3f} +- {1:.3f} W = {2:.3f} +- {3:.3f} kW'.format(DSWinP, DSWinPErr, DSWinP*1e-3, DSWinPErr*1e-3))

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
