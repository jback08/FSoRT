#! /usr/bin/python
# Python script to plot the nuclide rates for combined regions
# that have been processed by decays.cc and mergeDecayPlots.py

import ctypes
import os
import math
import ROOT
import sys

class parameters(object):
    ''' 
    Simple object to store initial parameters
    '''
    def __init__(self, dirName):
        # Directory name
        self.baseDir = 'FlukaArchive/fluka2020_v0p3/flair-2.3/FSoRT'
        self.dirName = dirName
        self.fileDir = '{0}/{1}'.format(self.baseDir, self.dirName)

        # Factor to say how many years are in one second
        self.yearFactor = 1.0/(60.0*60.0*24.0*365.25)      
        # Number of seconds in 1 day
        self.daySec = 60.0*60.0*24.0


def run(pars):

    regions = ['TGas']

    for iR,regName in enumerate(regions):

        fileName = '{0}/{1}Nuclides.root'.format(pars.fileDir, regName)
        plotGraphs(fileName, regName, 'isotopeRatesSum', pars)
        plotGraphs(fileName, regName, 'isotopeMassesSum', pars)

    
def plotGraphs(fileName, regName, multiGraphName, pars):

    print('Running plotGraphs for file {0}, region {1} and graphs {2}'.format(fileName, regName,
                                                                              multiGraphName))
    
    legend = ROOT.TLegend(0.785, 0.60, 0.875, 0.90, '')
    legend.SetTextSize(0.03)
    legend.SetFillColor(0)

    colours = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta]
    styles  = [ROOT.kFullCircle, ROOT.kFullCross]

    theFile = ROOT.TFile.Open(fileName, 'read')
    if not theFile:
        print('Could not open {0}'.format(fileName))
        return

    # Get the multigraph of the isotope rates
    multiGraph = theFile.Get(multiGraphName)

    # To print the legend and to set the y axis limits, we unfortunately
    # have to loop over the graphs again since this information is not saved
    graphList = multiGraph.GetListOfGraphs()
    nGraphs = graphList.GetEntries()
    
    minY = -1.0
    maxY = 0.0
    xP = ctypes.c_double(0.0)
    yP = ctypes.c_double(0.0)

    # Loop over the individual graphs to find the y limits and to set
    # the graph legend entries
    for iG in range(nGraphs):

        graph = graphList.At(iG)
        nPoints = graph.GetN()

        # Add graph to legend. First get its name, which should be
        # "Z-AX", where Z (A) = atomic (mass) number and X = "Rate" or "Mass"
        graphName = graph.GetName()
        # Just keep the isotope name
        graphName = graphName.replace('Rate', '')
        graphName = graphName.replace('Mass', '')

        legend.AddEntry(graph, graphName, 'pl')
        # Marker size
        graph.SetMarkerSize(1.25)
        
        # Update y limits
        for iP in range(nPoints):
            graph.GetPoint(iP, xP, yP)
            yVal = yP.value
            if yVal < 1e-10:
                continue
            if minY < 0.0:
                minY = yVal
            if yVal < minY:
                minY = yVal
            if yVal > maxY:
                maxY = yVal
        
    print('minY = {0}, maxY = {1}'.format(minY, maxY))

    # Plot the graphs
    ROOT.gROOT.SetStyle('Plain')
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPadGridX(True)
    ROOT.gStyle.SetPadGridY(True)
    ROOT.gStyle.SetPadTickY(1) # Add right side tick marks

    theCanvas = ROOT.TCanvas('theCanvas', '', 900, 600)
    theCanvas.UseCurrentStyle()
    theCanvas.cd(1)

    # Draw empty 2D histogram for x axis, especially for the time axis.
    # Otherwise the multigraph does not plot the very small decay times.
    # x axis = decay time (log scale), y axis = rate (log scale)
    nullHist = ROOT.TH2F('nullHist', '', 8, 1e-4, 1e3, 2, minY*0.5, maxY*2.0)
    nullHist.SetXTitle('Decay time (years) after 1 run yr')
    if 'Rate' in multiGraphName:
        nullHist.SetYTitle('Activity (Bq)')
    else:
        nullHist.SetYTitle('Isotope mass quantity (mg)')
    nullHist.SetTitleOffset(1.25, 'X')
    nullHist.GetXaxis().CenterTitle(True)
    nullHist.Draw()
    
    multiGraph.Draw('p')
    ROOT.gPad.SetLogx()
    ROOT.gPad.SetLogy()
    legend.Draw('same')

    # Indicate what the low-valued yearly decay times are
    text = ROOT.TText()
    text.SetTextSize(0.03)
    
    text.DrawText(pars.yearFactor*3600.0, maxY*2.1, '1 hr')
    text.DrawText(pars.yearFactor*pars.daySec, maxY*2.1, '1 day')
    text.DrawText(pars.yearFactor*pars.daySec*7.0, maxY*2.1, '1 wk')
    text.DrawText(1.0/12.0, maxY*2.1, '1 mth')
    
    theCanvas.Update()

    pngFileName = 'pngFiles/{0}_{1}.png'.format(regName, multiGraphName)
    theCanvas.Print(pngFileName)
    
    
    
if __name__ == "__main__":

    dirName = 'LBNFTargetL150cmAll'
    nArg = len(os.sys.argv)
    if nArg > 1:
        dirName = os.sys.argv[1]

    pars = parameters(dirName)
    run(pars)
