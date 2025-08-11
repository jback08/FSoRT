
#!/usr/bin/python

# Python script to plot particle info at the tracking planes in the
# FLUKA LBNF baffle, TPT & target areas using the "Trk.root" files

import math
import numpy as np
import ROOT

def run():

    createHistos('LBNFTgtL150cmJul25', 1)
    

def createHistos(label = 'LBNFTgtL150cmJul25', option = 1):

    baseDir = 'baffleData'
    rootName = '{0}/{1}_Opt{2}_All/{1}_Opt{2}_Trk.root'.format(baseDir, label, option)
    print('rootName is {0}\n'.format(rootName))
    rootFile = ROOT.TFile.Open(rootName, 'r')
    data = rootFile.Get('Data')

    nData = data.GetEntries()
    print('nData = {0}'.format(nData))

    # PDG: p = 2212, n = 2112, pi = 211, pi0 = 111, mu = 13, K = 321, K0 = 310 or 130 (KL)
    PDGMap = {}
    PDGMap['p'] = 2212
    PDGMap['n'] = 2112
    PDGMap['pi'] = 211
    PDGMap['pi0'] = 111
    PDGMap['mu'] = 13
    PDGMap['K'] = 321
    PDGMap['K0'] = 310

    # Histograms: KE & xy scatterplot at each tracking plane
    
    # Tracking plane locations (cm)
    zPlanes = [-217.47, -60.0, 235.0]

    KEHistMap = {}
    rxyHistMap = {}

    # p, n, pi, mu, K
    PDGArr = [2212, 2112, 211, 13, 321]

    for iz,zVal in enumerate(zPlanes):

        for ip,PDGVal in enumerate(PDGArr):

            histLabel = 'z{0}_{1}'.format(iz, PDGVal)
            KEHist = ROOT.TH1D('KE_{0}'.format(histLabel), '', 100, 0, 0)
            rxyHist = ROOT.TH2D('rxy_{0}'.format(histLabel), '', 100, 0, 0, 100, 0, 0)
            KEHist.SetDirectory(0)
            rxyHist.SetDirectory(0)
            
            KEHistMap[histLabel] = KEHist
            rxyHistMap[histLabel] = rxyHist

    data.SetBranchStatus('*', 0)
    data.SetBranchStatus('KE', 1)
    data.SetBranchStatus('x', 1)
    data.SetBranchStatus('y', 1)
    data.SetBranchStatus('z', 1)
    data.SetBranchStatus('pz', 1)
    data.SetBranchStatus('PDGId', 1)
    data.SetBranchStatus('weight', 1)
    
    for iD in range(nData):

        if iD%100000 == 0:
            print('iD loop {0}'.format(nData-iD))
        
        data.GetEntry(iD)

        # Only consider backscattered particles: negative pz
        pz = getattr(data, 'pz')
        if pz > 0.0:
            continue
        
        KE = getattr(data, 'KE')
        x = getattr(data, 'x')
        y = getattr(data, 'y')
        z = getattr(data, 'z')
        PDGId = abs(getattr(data, 'PDGId'))
        weight = getattr(data, 'weight')        
        
        iz = 0
        if (z > -217.47 and z < 235.0):
            iz = 1
        elif (z > -60.0):
            iz = 2
        
        # Get the required histograms and fill them
        histLabel = 'z{0}_{1}'.format(iz, PDGId)
        KEHist = KEHistMap.get(histLabel)
        rxyHist = rxyHistMap.get(histLabel)

        if KEHist is not None:
            KEHist.Fill(KE, weight)

        if rxyHist is not None:
            rxyHist.Fill(x, y, weight)
        
    rootFile.Close()

    histFileName = '{0}/{1}_Opt{2}_All/{1}_Opt{2}_HistosTrk.root'.format(baseDir, label, option)
    print('histFileName is {0}\n'.format(histFileName))
    histFile = ROOT.TFile(histFileName, 'recreate')
    histFile.cd()
    
    for iz,zVal in enumerate(zPlanes):
        for ip,PDGVal in enumerate(PDGArr):
            
            histLabel = 'z{0}_{1}'.format(iz, PDGVal)
            KEHist = KEHistMap.get(histLabel)
            rxyHist = rxyHistMap.get(histLabel)           
            KEHist.Write()
            rxyHist.Write()
    
    histFile.Close()

    # For plots, could use THStack:
    #KEHistStack = ROOT.THStack('KE', '')
    #KEHistStack.Add(KEHist) etc.
   
    
if __name__ == "__main__":
    run()
