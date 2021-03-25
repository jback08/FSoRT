// Program to plot combined regional radionuclide decay activities (rates and masses).
// This uses the "Evolution.root" files obtained by running extractNuclides.py
#include "addRegions.hh"

#include "TAxis.h"
#include "TCanvas.h"
#include "TChain.h"
#include "TFile.h"
#include "TGaxis.h"
#include "TGeoManager.h"
#include "TGraph.h"
#include "TH2.h"
#include "TLegend.h"
#include "TList.h"
#include "TMultiGraph.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TText.h"

#include <algorithm>
#include <iostream>

// These are static since we only want to define them once for all nuclides
static TGeoManager* m_geoManager = new TGeoManager("GeoManager", "GeoManager for periodic table");
static TGeoElementTable* m_elements = m_geoManager->GetElementTable();

nuclide::nuclide(const std::string& name, const int Z, const int A, const int m,
		 const std::vector<double>& times) :
    m_name(name),
    m_Z(Z),
    m_A(A),
    m_m(m),
    m_times(times),
    m_nTimes(int(times.size())),
    m_rates()
{
    // Initialize rates to zero
    m_rates = std::vector<double>(m_nTimes, 0.0);
}

nuclide::~nuclide() {
}

nuclide::nuclide(const nuclide &copy) :
    m_name(copy.m_name),
    m_Z(copy.m_Z),
    m_A(copy.m_A),
    m_m(copy.m_m),
    m_times(copy.m_times),
    m_nTimes(copy.m_nTimes),
    m_rates()
{    
    std::vector<double>::const_iterator iter;
    m_rates = std::vector<double>(m_nTimes, 0.0);
    for (int i = 0; i < m_nTimes; i++) {
	m_rates[i] = copy.m_rates[i];
    }

}

void nuclide::addRate(const int iTime, const double rate) {

    if (iTime >= 0 && iTime < m_nTimes) {
	m_rates[iTime] += rate;
    } else {
	std::cout<<"Error. Could not add decay rate for iTime = "<<iTime<<std::endl;
    }    
}

double nuclide::getRate(const int iTime) const {

    double rate(0.0);
    if (iTime >= 0 && iTime < m_nTimes) {
	rate = m_rates[iTime];
    }
    return rate;
}

double nuclide::getMassMu(const int iTime) const {

    // Get the mass by dividing the decay rate with the specific activity:
    // Activity R = dN/dt = ln(2)*N/tHalf
    // Specific activity RSpec = ln(2)*N_A/(tHalf*A) = activity of 1 gram
    // So total mass of isotope (grams) = R/RSpec.
    // M = (dN/dt)*tHalf*A/(N_A*ln2)
    
    double rate = this->getRate(iTime);
    double massMu = this->getMassMu(rate);
    return massMu;

}

double nuclide::getMassMu(const double rate) const {

    double massMu(0.0);
    
    const TGeoElementRN* radNucl = m_elements->GetElementRN(m_A, m_Z, m_m);
    if (radNucl) {

	double sActivity = radNucl->GetSpecificActivity();
	if (rate > 0.0 && sActivity > 0.0) {
	    // Mass in micrograms
	    massMu = rate*1e6/sActivity;
	}
    }

    return massMu;
}

double nuclide::getMaxRate() const {

    double maxRate(0.0);
    std::vector<double>::const_iterator iter;
    for (iter = m_rates.begin(); iter != m_rates.end(); ++iter) {
	double rate = *iter;
	if (rate > maxRate) {maxRate = rate;}
    }

    return maxRate;

}

bool nuclide::operator<(const nuclide& other) const {

    double maxRate = this->getMaxRate();
    double otherMaxRate = other.getMaxRate();

    return (maxRate < otherMaxRate);

}

bool nuclide::operator==(const nuclide& other) const {

    bool isEqual(false);
    // Compare atomic, mass and isomer numbers
    if (m_Z == other.m_Z && m_A == other.m_A && m_m == other.m_m) {
	isEqual = true;
    }
    
    return isEqual;
    
}

void nuclide::print() const {

    std::cout<<"Nuclide: Z = "<<m_Z<<", A = "<<m_A<<", m = "<<m_m<<std::endl;
    for (int i = 0; i < m_nTimes; i++) {
	std::cout<<"Decay time "<<m_times[i]<<" has rate = "<<m_rates[i]
		 <<" and mass = "<<this->getMassMu(m_rates[i])<<std::endl;
    }
}

bool nuclide::sameIsotope(const int Z, const int A, const int m) const {

    bool same(false);
    if (m_Z == Z && m_A == A && m_m == m) {same = true;}    
    return same;

}

TGraph* nuclide::getGraph(const graphOpt& option) const {

    // Return the decay rates or masses as graphs (vs time)
    TString graphName(m_name.c_str());
    if (option == graphOpt::Rate) {
	graphName += "Rate";
    } else {
	graphName += "Mass";
    }

    TGraph* theGraph = new TGraph();
    theGraph->SetName(graphName.Data());
    theGraph->SetTitle(graphName.Data());

    for (int i = 0; i < m_nTimes; i++) {

	if (i == 0) {continue;}
	
	const double time = m_times[i];
	const double rate = this->getRate(i);
	const int nP = theGraph->GetN();
	//std::cout<<"i = "<<i<<", time = "<<time<<", rate = "<<rate<<": nP = "<<nP<<std::endl;

	if (rate > 0.0) {
	    if (option == graphOpt::Rate) {
		// Decay activity
		theGraph->SetPoint(nP, time, rate);
	    } else {
		// Mass abundance (micrograms)
		const double massMu = this->getMassMu(rate);
		theGraph->SetPoint(nP, time, massMu);
	    }
	}
	
    }

    //theGraph->Print();
    //std::cout<<"Done graph "<<graphName<<std::endl;
    
    return theGraph;

}


addRegions::addRegions(const TString& fileDir) :
    m_yearFactor(1.0/(60.0*60.0*24.0*365.25)),
    m_BqToCurie(1.0/3.7e10),
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

addRegions::~addRegions() {
    delete m_canvas;
    delete m_text;
}

void addRegions::run() {

    const int maxNGraphs(20);
    
    // Loop over regions
    mapStrings::iterator mIter;
    for (mIter = m_regions.begin(); mIter != m_regions.end(); ++mIter) {

	// Combined region name
	TString totName = mIter->first;
	// List of individual volumes it contains
	std::vector<TString> volList = mIter->second;

	// Get the combined list of nuclides, sorted by descending activity
	std::vector<nuclide*> nuclideList = this->getNuclideList(totName, volList);

	this->createPlots(totName, nuclideList, graphOpt::Rate, maxNGraphs);
	this->createPlots(totName, nuclideList, graphOpt::Mass, maxNGraphs);
	
    } // region loop
    
}

void addRegions::createPlots(const TString& totName,
			     const std::vector<nuclide*>& nuclideList,
			     const graphOpt& option, const int maxNGraphs) {

    std::cout<<"Creating plot for "<<totName<<" with option "<<option<<std::endl;
    TString graphName(totName);
    if (option == graphOpt::Rate) {
	graphName += "MultiRate";
    } else {
	graphName += "MultiMass";
    }
    TMultiGraph theGraphs(graphName, graphName);

    // Styles and colours (unique up to 10 plots)
    const int colours[5] = {kBlack, kRed, kBlue, kGreen+2, kMagenta};
    const int styles[4]  = {kFullCircle, kFullCross, kFullSquare, kFullDiamond};

    // Keep track of y axis limits
    double yMinTot(-1.0), yMaxTot(0.0);

    // Graph legend
    TLegend legend(0.785, 0.60, 0.875, 0.90, "");
    legend.SetTextSize(0.03);
    legend.SetFillColor(0);

    int iN(0);
    std::vector<nuclide*>::const_iterator nuclideIter;
    for (nuclideIter = nuclideList.begin();
	 nuclideIter != nuclideList.end(); ++nuclideIter) {

	nuclide* aNuclide = *nuclideIter;
	if (iN >= maxNGraphs) {break;}
	
	// Each nuclide makes one graph
	TGraph* graph = aNuclide->getGraph(option);

	// Skip graph if it has no points
	if (graph->GetN() == 0) {continue;}

	const int colour = colours[iN%5];
	const int style = styles[iN/5];
	
	graph->SetMarkerColor(colour);
	graph->SetLineColor(colour);
	graph->SetMarkerStyle(style);
	graph->SetMarkerSize(1.35);
	
	theGraphs.Add(graph);

	// Add graph to legend
	const std::string nuclideName = aNuclide->getName();
	legend.AddEntry(graph, nuclideName.c_str(), "pl");

	double xP(0.0), yP(0.0);
	for (int iP = 0; iP < graph->GetN(); iP++) {
	    graph->GetPoint(iP, xP, yP);	    
	    if (yMinTot < 0.0) {yMinTot = yP;}
	    if (yP < yMinTot) {yMinTot = yP;}
	    if (yP > yMaxTot) {yMaxTot = yP;}
	}

	// Print out tritium production values (near "t = 0")
	if (nuclideName.find("H-3") != std::string::npos) {
	    graph->GetPoint(0, xP, yP);
	    const std::string graphName(graph->GetName());
	    if (option == graphOpt::Rate) {
		const double rateCi = yP*m_BqToCurie;
		std::cout<<totName<<" "<<nuclideName<<" initial activity = "
			 <<yP<<" Bq or "<<rateCi<<" Ci"<<std::endl;
	    } else {
		std::cout<<totName<<" "<<nuclideName<<" initial mass = "
			 <<yP*1e-3<<" mgrams"<<std::endl;
	    }
	}
	
	// Increment number of non-empty graphs
	iN++;

    }

    // Draw empty 2D histogram for x axis, especially for the time axis.
    // Otherwise the multigraph does not plot the very small decay times.
    // x axis = decay time (log scale), y axis = mass (log scale)
    //std::cout<<"Y range: "<<yMinTot<<" to "<<yMaxTot<<std::endl;
    
    TH2F* nullHist = new TH2F("nullHist", "", 8, 1e-4, 1e3, 2, yMinTot*0.5, yMaxTot*2.0);
    nullHist->SetXTitle("Decay time (years) after 1 run yr");
    if (option == graphOpt::Rate) {
	nullHist->SetYTitle("Activity (Bq)");
    } else {
	nullHist->SetYTitle("Isotope mass quantity (#mug)");
    }
    nullHist->SetTitleOffset(1.25, "X");
    nullHist->GetXaxis()->CenterTitle(kTRUE);

    m_canvas->cd(1);    
    nullHist->Draw();

    // Draw multigraph on log-log scale
    theGraphs.Draw("p");
    gPad->SetLogx();
    gPad->SetLogy();

    // Extend size of legend if required
    if (theGraphs.GetListOfGraphs()->GetEntries() > 10) {
	legend.SetY1(0.25);
    } else {
	legend.SetY1(0.60);
    }
    legend.Draw("same");

    // For rates (masses), show units in Curies (mgrams) on the right hand y axis
    TAxis* xAxis = nullHist->GetXaxis();
    const double xMaxAxis = xAxis->GetXmax();
    TAxis* yAxis = nullHist->GetYaxis();
    const double yMinAxis = yAxis->GetXmin();
    const double yMaxAxis = yAxis->GetXmax();
    const double minRateCi = yMinAxis*m_BqToCurie;
    const double maxRateCi = yMaxAxis*m_BqToCurie;
    double otherMinY = yMinAxis;
    double otherMaxY = yMaxAxis;
    TString otherLabel("");
    // Option G = log scale
    if (option == graphOpt::Rate) {
	otherMinY = minRateCi;
	otherMaxY = maxRateCi;
	otherLabel = "Activity (Ci)";
    } else {
	otherMinY = yMinAxis*1e-3;
	otherMaxY = yMaxAxis*1e-3;
	otherLabel = "Mass (mg)";
    }
    TGaxis otherAxis(xMaxAxis, yMinAxis, xMaxAxis, yMaxAxis, otherMinY, otherMaxY, 510, "+LG");
    otherAxis.SetTitle(otherLabel.Data());
    otherAxis.Draw("same");    
    
    // Indicate useful low-year numbers
    const double daySec = 60.0*60.0*24.0;
    m_text->DrawText(m_yearFactor*3600.0, yMaxTot*2.1, "1 hr");
    m_text->DrawText(m_yearFactor*daySec, yMaxTot*2.1, "1 day");
    m_text->DrawText(m_yearFactor*daySec*7.0, yMaxTot*2.1, "1 wk");
    m_text->DrawText(1.0/12.0, yMaxTot*2.1, "1 mth");

    // Also print the volume region name on the top right
    const std::string totString(totName.Data()); 
    const std::string plotLabel = this->breakStringAtCaps(totString);
    // introduce a space for any capital letter after the 1st one    
    m_text->DrawText(10.0, yMaxTot*2.1, plotLabel.c_str());
    
    m_canvas->Update();

    // Print graphs
    TString pngFile("pngFiles/");
    pngFile += graphName;
    pngFile += ".png";
    m_canvas->Print(pngFile.Data());    
    
    /*TString epsFile("epsFiles/");
    epsFile += graphName;
    epsFile += ".eps";
    m_canvas->Print(epsFile.Data());*/
    
    delete nullHist;
}

std::vector<nuclide*> addRegions::getNuclideList(const TString& totName,
						 const std::vector<TString>& volList) {

    // Vector of unique nuclides
    std::vector<nuclide*> nuclideList;
    std::vector<nuclide*>::iterator nuclideIter;
    
    // Create a TChain for the list of volumes
    std::cout<<"Creating TChain for "<<totName<<std::endl;
    TChain chain("Data", "Data");

    std::vector<TString>::const_iterator volIter;
    for (volIter = volList.begin(); volIter != volList.end(); ++volIter) {

	TString fileName(m_fileDir);
	fileName += "/"; fileName += *volIter;
	fileName += "Evolution.root";
	chain.Add(fileName.Data());
	
    }

    // TChain variables
    int iTime(0), Z(0), A(0), m(0);
    double time(0.0), rate(0.0), total(0.0);
    chain.SetBranchAddress("iTime", &iTime);
    chain.SetBranchAddress("time", &time);
    chain.SetBranchAddress("Z", &Z);
    chain.SetBranchAddress("A", &A);
    chain.SetBranchAddress("m", &m);
    chain.SetBranchAddress("rate", &rate);
    chain.SetBranchAddress("total", &total);
    
    // All of the chained trees will have the same decay time range
    // i.e. time and iTime mean the same thing for all of them
    size_t nEntries = chain.GetEntries();
    std::cout<<"nEntries = "<<nEntries<<std::endl;

    size_t nTimes(0);
    if (nEntries > 0) {
	nTimes = chain.GetMaximum("iTime") + 1;
    }
    std::cout<<"nTimes = "<<nTimes<<std::endl;
    
    // Get the list of decay times
    std::vector<int> decayIntTimes;
    std::vector<double> decayTimes;
    decayIntTimes.reserve(nTimes);
    decayTimes.reserve(nTimes);

    for (size_t i = 0; i < nEntries; i++) {

	chain.GetEntry(i);

	// Stop if we have the expected time values
	if (decayIntTimes.size() == nTimes) {break;}
	
	if (std::find(decayIntTimes.begin(), decayIntTimes.end(), iTime)
	    == decayIntTimes.end()) {
	    // Add the decay time (converted from seconds to years)
	    decayIntTimes.push_back(iTime);
	    decayTimes.push_back(time*m_yearFactor);
	}
	
    }

    /*std::vector<double>::iterator tIter;
    for (tIter = decayTimes.begin(); tIter != decayTimes.end(); ++tIter) {
        std::cout<<"Time = "<<*tIter<<std::endl;
    }*/

    // Create the unique list of isotopes and set their decay rates vs time
    for (size_t i = 0; i < nEntries; i++) {

	chain.GetEntry(i);

	bool gotNuclide(false);
	// Iterate over nuclide list entries made so far
	for (nuclideIter = nuclideList.begin();
	     nuclideIter != nuclideList.end(); ++nuclideIter) {

	    nuclide* aNuclide = *nuclideIter;
	    // Check if this nuclide is already in the list
	    if (aNuclide && aNuclide->sameIsotope(Z, A, m)) {
		gotNuclide = true;
		// Add the decay rate for the given time bin
		aNuclide->addRate(iTime, rate);
		break;
	    }	
	}
	
	if (!gotNuclide) {
	    // Define the new nuclide
	    const std::string isoName = this->getIsotopeName(Z, A, m);
	    nuclide* theNuclide = new nuclide(isoName, Z, A, m, decayTimes);
	    // Add the decay rate for the given time bin
	    theNuclide->addRate(iTime, rate);
	    // Add it to the unique list
	    nuclideList.push_back(theNuclide);
	}
	
    }
    
    // Sort nuclides in ascending maximum activity
    std::sort(nuclideList.rbegin(), nuclideList.rend(), compareNuclides);

    return nuclideList;

}

std::string addRegions::getIsotopeName(const int Z, const int A, const int m) const {

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

std::string addRegions::breakStringAtCaps(const std::string& input) const {

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


void addRegions::defineRegions() {

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
    
    addRegions a(fileDir);
    a.run();
    
    return 0;

}
