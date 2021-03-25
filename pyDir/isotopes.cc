// Program to plot combined regional radionuclide decay activities (rates and masses).
// This uses the "Evolution.root" files obtained by running extractNuclides.py
#include "isotopes.hh"

#include "TAxis.h"
#include "TCanvas.h"
#include "TChain.h"
#include "TFile.h"
#include "TGeoManager.h"
#include "TGraphErrors.h"
#include "TLegend.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TText.h"

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <fstream>

// These are static since we only want to define them once for all nuclides
static TGeoManager* m_geoManager = new TGeoManager("GeoManager", "GeoManager for periodic table");
static TGeoElementTable* m_elements = m_geoManager->GetElementTable();

massWeight::massWeight(int A, double weight, double error) :
    m_A(A),
    m_weight(weight),
    m_error(error)
{
}

double massWeight::getFracError() const {

    double fracErr(0.0);
    if (m_weight > 0.0) {
	fracErr = m_error/m_weight;
    }
    return fracErr;    
}

isotopes::isotopes(const TString& fileDir) :
    m_yearFactor(1.0/(60.0*60.0*24.0*365.25)),
    m_fileDir(fileDir),
    m_regions(),
    m_canvas(new TCanvas("theCanvas", "", 900, 600)),
    m_text(new TText())
{
    this->defineRegions();
    gROOT->SetStyle("Plain");
    gStyle->SetOptStat(0);
    gStyle->SetPadGridX(kTRUE);
    gStyle->SetPadGridY(kTRUE);
    //gStyle->SetPadTickY(1); // Add right side tick marks
    m_canvas->UseCurrentStyle();

    m_text->SetTextSize(0.040);
    
}

isotopes::~isotopes() {
    delete m_canvas;
    delete m_text;
}

void isotopes::run() {

    // Loop over regions
    mapStrings::iterator mIter;
    for (mIter = m_regions.begin(); mIter != m_regions.end(); ++mIter) {

	// Combined region name
	TString totName = mIter->first;
	// List of individual volumes it contains
	std::vector<TString> volList = mIter->second;

	// Create histogram of isotope abundance: Z, A or A vs Z
	this->plot1D(totName, volList, isotopes::ZOpt);
	this->plot1D(totName, volList, isotopes::AOpt);

	this->plotAZ(totName, volList);
	
	
    } // region loop
    
}

void isotopes::plot1D(const TString& totName, const std::vector<TString>& volList,
		      const PlotOption& option) const {

    // Create a TChain for the list of volumes
    std::cout<<"Creating TChain for "<<totName<<std::endl;
    TString chainName("ZTree");
    // Atomic number or mass
    TString XName("Z"), xLabel("Atomic number Z");
    if (option == isotopes::AOpt) {
	chainName = "ATree";
	XName = "A";
	xLabel = "Atomic mass A";
    }
    TChain chain(chainName.Data(), chainName.Data());

    std::vector<TString>::const_iterator volIter;
    for (volIter = volList.begin(); volIter != volList.end(); ++volIter) {

	TString fileName(m_fileDir);
	fileName += "/"; fileName += *volIter;
	fileName += "RadNuclides_sum.root";
	chain.Add(fileName.Data());
	
    }

    // TChain variables
    int X(0);
    double w(0.0), fErr(0.0);
    chain.SetBranchAddress(XName.Data(), &X);
    chain.SetBranchAddress("w", &w);
    chain.SetBranchAddress("fErr", &fErr);
  
    size_t nEntries = chain.GetEntries();
    std::cout<<"nEntries = "<<nEntries<<std::endl;

    // Create 1D histograms: weights and fractional errors.
    // Then create a graph from these, combining the chained data
    double XMin = chain.GetMinimum(XName.Data()) - 1.0;
    double XMax = chain.GetMaximum(XName.Data()) + 1.0;
    int NX = XMax - XMin;
    TH1D XHist("XHist", "", NX, XMin, XMax);
    TH1D XErrHist("XErrHist", "", NX, XMin, XMax);
    XHist.SetDirectory(0);
    XErrHist.SetDirectory(0);
    
    for (size_t i = 0; i < nEntries; i++) {

	chain.GetEntry(i);

	double XMid = X + 0.5;
	XHist.Fill(XMid, w);
	XErrHist.Fill(XMid, fErr*w);
	
    }

    // Create graph of weights +- errors
    TGraphErrors XGraph;
    XGraph.SetMarkerStyle(kFullCircle);
    double minY(-1.0), maxY(0.0);
    
    for (int k = 0; k < NX; k++) {

	int XInt = int(XMin) + k;
	double weight = XHist.GetBinContent(k+1);

	if (weight > 0.0) {
	    
	    double error = XErrHist.GetBinContent(k+1);
	    int index = XGraph.GetN();
	    XGraph.SetPoint(index, XInt, weight);
	    XGraph.SetPointError(index, 0.0, error);

	    if (minY < 0.0) {minY = weight;}
	    if (weight < minY) {minY = weight;}
	    if (weight > maxY) {maxY = weight;}
	    
	}
	
    }

    //std::cout<<std::setprecision(6)<<"Hist y: "<<minY<<", "<<maxY<<std::endl;
    
    TH2D nullHist("nullHist", "", 2, XMin, XMax, 2, 0.5*minY, 2.0*maxY);
    nullHist.SetXTitle(xLabel.Data());
    nullHist.SetYTitle("Yield per proton");
    nullHist.GetXaxis()->CenterTitle(kTRUE);
    nullHist.GetYaxis()->CenterTitle(kTRUE);
    
    m_canvas->cd(1);

    nullHist.Draw();
    XGraph.Draw("psame");
    gPad->SetLogy();
    m_canvas->Update();
    
    TString pngFile("pngFiles/");
    pngFile += totName; pngFile += "_";
    pngFile += XName.Data(); pngFile += "Plot.png";
    m_canvas->Print(pngFile.Data());

    std::cout<<"Graph data for "<<totName<<std::endl;
    XGraph.Print();
    std::cout<<std::endl;
    
}

void isotopes::plotAZ(const TString& totName, const std::vector<TString>& volList) const {

    // Create a TChain for the list of volumes
    std::cout<<"Creating TChain for "<<totName<<std::endl;
    TString chainName("AZTree");
    TChain chain(chainName.Data(), chainName.Data());

    std::vector<TString>::const_iterator volIter;
    for (volIter = volList.begin(); volIter != volList.end(); ++volIter) {

	TString fileName(m_fileDir);
	fileName += "/"; fileName += *volIter;
	fileName += "RadNuclides_sum.root";
	chain.Add(fileName.Data());
	
    }

    // TChain variables
    int Z(0), A(0);
    double w(0.0), fErr(0.0);
    chain.SetBranchAddress("A", &A);
    chain.SetBranchAddress("Z", &Z);
    chain.SetBranchAddress("w", &w);
    chain.SetBranchAddress("fErr", &fErr);
  
    size_t nEntries = chain.GetEntries();
    std::cout<<"nEntries = "<<nEntries<<std::endl;

    // Create 2D histogram: A vs Z
    double ZMin = chain.GetMinimum("Z") - 1.0;
    double ZMax = chain.GetMaximum("Z") + 1.0;
    int NZ = ZMax - ZMin;

    double AMin = chain.GetMinimum("A") - 1.0;
    double AMax = chain.GetMaximum("A") + 1.0;
    int NA = AMax - AMin;

    // Weights
    TH2D AZHist("AZHist", "", NZ, ZMin, ZMax, NA, AMin, AMax);
    AZHist.SetXTitle("Atomic number Z");
    AZHist.SetYTitle("Atomic mass A");

    // Uncertainties
    TH2D AZErrHist("AZErrHist", "", NZ, ZMin, ZMax, NA, AMin, AMax);
    AZHist.SetXTitle("Atomic number Z");
    AZHist.SetYTitle("Atomic mass A");

    TAxis* xAxis = AZHist.GetXaxis();
    TAxis* yAxis = AZHist.GetYaxis();
    xAxis->CenterTitle(kTRUE);
    yAxis->CenterTitle(kTRUE);
    xAxis->SetNdivisions(15);
    yAxis->SetNdivisions(15);
    AZHist.SetDirectory(0);
    AZErrHist.SetDirectory(0);
    
    for (size_t i = 0; i < nEntries; i++) {

	chain.GetEntry(i);

	double ZMid = Z + 0.5;
	double AMid = A + 0.5;
	AZHist.Fill(ZMid, AMid, w);
	//std::cout<<"Entry "<<i<<": Z = "<<ZMid<<", "<<AMid<<", "<<w<<std::endl;
	AZErrHist.Fill(ZMid, AMid, w*fErr);
	
    }

    // Write out A-Z values in a text file
    this->writeOutAZValues(totName, AZHist, AZErrHist);
    
    m_canvas->cd(1);
    AZHist.Draw("colz");
    
    gPad->SetLogz();
    gPad->SetLogy(0);
    m_canvas->Update();
    
    TString pngFile("pngFiles/");
    pngFile += totName; pngFile += "_AZPlot.png";
    m_canvas->Print(pngFile.Data());

}

void isotopes::writeOutAZValues(const TString& totName, const TH2D& AZHist,
				const TH2D& AZErrHist) const {
    
    TString txtFile("datFiles/");
    txtFile += totName.Data(); txtFile += "_AZData.txt";

    std::ofstream writeData(txtFile.Data());

    // Each line contains: Z Total A1 A2 A3 ...
    // x axis = atomic number Z, y axis = atomic mass A
    const TAxis* ZAxis = AZHist.GetXaxis();
    const TAxis* AAxis = AZHist.GetYaxis();

    const int nZ = ZAxis->GetNbins();
    const double minZ = ZAxis->GetXmin();
    //const double maxZ = ZAxis->GetXmax();
    const double dZ = ZAxis->GetBinWidth(1);
    const int nA = AAxis->GetNbins();
    const double minA = AAxis->GetXmin();
    //const double maxA = AAxis->GetXmax();
    const double dA = AAxis->GetBinWidth(1);

    writeData<<"Residual nucleon yields per proton with fractional errors in percent\n"<<std::endl;
    
    for (int iZ = 0; iZ < nZ; iZ++) {

	int atomicZ = int(dZ*iZ + minZ);

	std::vector<massWeight> AVect;
	double totWeight(0.0), totError(0.0);
	
	for (int iA = 0; iA < nA; iA++) {

	    int atomicA = int(dA*iA + minA);	    
	    double weight = AZHist.GetBinContent(iZ+1, iA+1);
	    double error = AZErrHist.GetBinContent(iZ+1, iA+1);

	    if (weight > 0.0) {
		massWeight mW(atomicA, weight, error);
		AVect.push_back(mW);
		totWeight += weight;
		totError += error*error;
	    }

	}

	int nVect = AVect.size();
	if (nVect > 0) {

	    totError = sqrt(totError);
	    writeData<<std::scientific<<std::setprecision(3)<<"Z = "<<atomicZ
		     <<" ("<<this->getElementName(atomicZ)<<"): total = ";
	    double totFracErr(0.0);
	    if (totWeight > 0.0) {totFracErr = totError/totWeight;}
	    this->formatOutput(writeData, totWeight, totFracErr);
	    writeData<<std::endl;

	    // Mass isotopes for given Z (there will always be at least 1)
	    for (int iV = 0; iV < nVect; iV++) {
		massWeight mW = AVect[iV];
		writeData<<"A = "<<mW.getA()<<", yield = ";
		this->formatOutput(writeData, mW.getWeight(), mW.getFracError());
		writeData<<std::endl;
	    }
	    writeData<<std::endl;
	    
	}

    }
    
}

void isotopes::formatOutput(std::ofstream& writeData, double value, double fracErr) const {

    if (value < 0.01) {

	writeData<<std::scientific<<std::setprecision(1)<<value<<" +- "
		 <<std::fixed<<std::setprecision(1)<<fracErr*100.0<<"%";
	
    } else {

	writeData<<std::fixed<<std::setprecision(3)<<value<<" +- "
		 <<std::setprecision(1)<<fracErr*100.0<<"%";

    }

}


std::string isotopes::getElementName(const int Z) const {

    const TGeoElement* element = m_elements->GetElement(Z);
    TString isoName = element->GetName();
    // The element name is all capitalised; only do this for the 1st char
    isoName.ToLower();
    isoName[0] = toupper(isoName[0]);

    std::string isoString(isoName.Data());
    return isoString;
    
}

std::string isotopes::getIsotopeName(const int Z, const int A, const int m) const {

    const TGeoElement* element = m_elements->GetElement(Z);
    TString isoName = element->GetName();
    // The element name is all capitalised; only do this for the 1st char
    isoName.ToLower();
    isoName[0] = toupper(isoName[0]);
    isoName += "-";
    isoName += A;
    if (m > 0) {
	isoName += "(";
	isoName += m;
	isoName += ")";
    }

    std::string isoString(isoName.Data());
    return isoString;
    
}

std::string isotopes::breakStringAtCaps(const std::string& input) const {

    // Special cases:
    if (input == "TargetDSWin") {
	return std::string("Target DS Window");
    }

    // For a sentence by adding spaces between capital letters
    std::string newname;
    for (size_t i = 0; i < input.size(); i++) {
        if (isupper(input[i]) && i != 0) {
	    // Add space (not for the 1st letter)
            newname += " ";
	}
        newname += input[i];
    }
    return newname;
}


void isotopes::defineRegions() {

    // Internal map storing each combined region name along with
    // a vector of the individual regions that it contains
    m_regions.clear();
    
    m_regions["TargetCore"] = std::vector<TString>{"Target"};
    m_regions["TargetHelium"] = std::vector<TString>{"TGas1", "TGas2", "TGas3", "BafGas"};
    m_regions["TargetContainer"] = std::vector<TString>{"TCont"};
    m_regions["TargetFlowGuide"] = std::vector<TString>{"TFlow", "BafCont"};
    m_regions["TargetDSWin"] = std::vector<TString>{"TDSWin"};

    m_regions["Bafflet"] = std::vector<TString>{"Baffle"};
    m_regions["HornConductor"] = std::vector<TString>{"H1In", "H1Out", "H1End", "H1Cool", "H1Plate", "H1Ceram"};
    m_regions["HornArgon"] = std::vector<TString>{"H1Gas1", "H1Gas2"};
    m_regions["Nitrogen"] = std::vector<TString>{"BeamGas", "H1Gas3"};

    if (m_fileDir.Contains("Fins")) {
	m_regions["TargetFins"] = std::vector<TString>{"TFins"};

	m_regions["All"] = std::vector<TString>{"Target", "TGas1", "TGas2", "TGas3", "BafGas",
						"TCont", "TFlow", "BafCont", "TDSWin", "Baffle",
						"H1Ceram", "H1In", "H1Out", "H1End", "H1Cool",
						"H1Plate", "H1Gas1", "H1Gas2", "BeamGas",
						"H1Gas3", "TFins"};
    } else {
	m_regions["TargetSpacers"] = std::vector<TString>{"TSpacer1", "TSpacer2", "TSpacer3", "TSpacer4"};

	// Need to make sure H1Plate is added later on (was ascii not binary file, so was missed)
	m_regions["All"] = std::vector<TString>{"Target", "TGas1", "TGas2", "TGas3", "BafGas",
						"TCont", "TFlow", "BafCont", "TDSWin", "Baffle",
						"H1Ceram", "H1In", "H1Out", "H1End", "H1Cool",
						"H1Plate", "H1Gas1", "H1Gas2", "BeamGas", "H1Gas3",
						"TSpacer1", "TSpacer2", "TSpacer3", "TSpacer4"};

    }

}

int main(int argc, char** argv) {

    TString fileDir("LBNFTargetL150cmSpacersAll");
    if (argc > 1) {
	fileDir = TString(argv[1]);
    }

    isotopes a(fileDir);
    a.run();
    
    return 0;

}
