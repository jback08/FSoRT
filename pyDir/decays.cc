#include "decays.hh"

#include "TFile.h"
#include "TTree.h"
#include "TGraph.h"
#include "TH2.h"
#include "TAxis.h"

#include "TCanvas.h"
#include "TROOT.h"
#include "TStyle.h"

#include "TLatex.h"
#include "TLine.h"
#include "TLegend.h"
#include "TMultiGraph.h"

#include <cmath>
#include <iostream>
#include <cstdlib>
#include <fstream>

#include <algorithm>

using std::cout;
using std::endl;
using std::pair;

decays::decays() {

  outputName_ = "";
  theDetector_ = "";
  // Factor to say how many years are in one second
  yearFactor_ = 1.0/(60.0*60.0*24.0*365.25);
  minFrac_ = 0.01;

  geoManager_ = new TGeoManager("GeoManager", "GeoManager for periodic table");
  elements_ = geoManager_->GetElementTable();

}

decays::~decays() {
}

void decays::readInputFile(string fileName, string outputName) {

  std::ifstream getData(fileName.c_str());

  string whiteSpace(" ");
  
  int iTime(-1), A(-1), Z(-1), m(-1);
  double time(-1.0), rate(0.0), total(0.0), volume(0.0);

  TString* detString = new TString("");
  TString* element = new TString("");

  outputName_ = outputName;

  TFile* outFile = TFile::Open(outputName_.c_str(), "recreate");
  if (!outFile) {
      cout<<"Could not create file "<<outputName_<<endl;
      return;
  } else {
      cout<<"Creating file "<<outputName_<<endl;
  }
  TTree* theTree = new TTree("Data", "Data");
  theTree->SetDirectory(outFile);

  theTree->Branch("detector", &detString, 16000, 0); // Do not "split" the string

  theTree->Branch("iTime", &iTime, "iTime/I");
  theTree->Branch("time", &time, "time/D");

  theTree->Branch("A", &A, "A/I");
  theTree->Branch("Z", &Z, "Z/I");
  theTree->Branch("element", &element, 16000, 0);
  theTree->Branch("m", &m, "m/I");
  theTree->Branch("rate", &rate, "rate/D");

  theTree->Branch("total", &total, "total/D");
  theTree->Branch("volume", &volume, "volume/D");

  while (getData.good()) {

    // Read various input lines
    if (getData.peek() == '\n') {
      
      // Finish reading line
      char c;
      getData.get(c);

      // Stop while loop if we have reached the end of the file
      if (getData.eof()) {break;}

    } else if (getData.peek() == '#') {

      // Skip comment line
      getData.ignore(1000, '\n');
      getData.putback('\n');
      
      // Stop while loop if we have reached the end of the file
      if (getData.eof()) {break;}

    } else {

      // Read data line
      char line[100];
      getData.getline(line, 100);

      // Stop while loop if we have reached the end of the file
      if (getData.eof()) {break;}

      string lineString(line);
      vector<string> lineVect = splitString(lineString, whiteSpace);

      int nVect = static_cast<int>(lineVect.size());

      if (nVect < 1) {break;}

      if (nVect == 3 && lineVect[0] == "Detector") {

	theDetector_ = lineVect[2];
	string reducedName(theDetector_);
	reducedName.erase(0, 2); // Remove the first two letters ("RN")
	*detString = reducedName.c_str();	

      } else if (nVect == 4) {

	if (lineVect[0] == "Time") {
	  
	  time = atof(lineVect[2].c_str());
	  //cout<<"Time = "<<time<<" seconds"<<endl;
	  iTime++;

	} else if (lineVect[0] == "Total") {

	  total = atof(lineVect[3].c_str());

	} else if (lineVect[0] == "Volume") {

	  volume = atof(lineVect[2].c_str());

	}

      } else if (nVect == 5) {

	// Nuclide line
	A = atoi(lineVect[0].c_str());
	Z = atoi(lineVect[2].c_str());
	m = 0; // not an isomer

	*element = lineVect[1].c_str();

	rate = atof(lineVect[3].c_str());
	//cout<<"Element "<<symbol<<": "<<Z<<", "<<A<<" has rate = "<<rate<<" Bq/g"<<endl;

	theTree->Fill();
	
      } else if (nVect == 7) {

	// Isomer line
	A = atoi(lineVect[1].c_str());
	Z = atoi(lineVect[3].c_str());
	m = atof(lineVect[4].c_str());

	*element = lineVect[2].c_str();

	rate = atof(lineVect[5].c_str());
	//cout<<"Isomer "<<symbol<<": "<<Z<<", "<<A<<" (m = "
	//    <<m<<") has rate = "<<rate<<" Bq/g"<<endl;

	theTree->Fill();

      }

    }

  }

  outFile->cd();
  theTree->Write();
  outFile->Close();

}

void decays::createPlots() {

  getTotActivity();
  int nUniqueIsotopes = getIsotopes();

  if (nUniqueIsotopes) {
      plotIsotopeHistos();
      plotIsotopeGraphs();
      plotIsotopeMasses();
  }

}

int decays::getIsotopes() {

  int nUnique(0);

  TFile* theFile = TFile::Open(outputName_.c_str(), "read");
  if (!theFile) {
      cout<<"Could not open file "<<outputName_<<endl;
      return nUnique;
  }
  TTree* theTree = dynamic_cast<TTree*>(theFile->Get("Data"));

  int iTime(0);
  double time(0.0), rate(0.0), total(0.0);
  int Z(0), A(0), m(0);
  detName_ = 0;
  TString* element = new TString("");

  theTree->SetBranchAddress("iTime", &iTime);
  theTree->SetBranchAddress("time", &time);
  theTree->SetBranchAddress("Z", &Z);
  theTree->SetBranchAddress("A", &A);
  theTree->SetBranchAddress("m", &m);
  theTree->SetBranchAddress("element", &element);
  theTree->SetBranchAddress("rate", &rate);
  theTree->SetBranchAddress("total", &total);
  theTree->SetBranchAddress("detector", &detName_);

  int nEntries = static_cast<int>(theTree->GetEntries());

  int i(0), jTime(0);
  
  // For each iTime value store the isotope rates in a vector,
  // ordered in decreasing activity

  vector<nuclide> nuclideList;

  theMap_.clear();
  decayTimes_.clear();
  nuclideList.clear();

  double prevTime(-1.0);

  for (i = 0; i < nEntries; i++) {

    theTree->GetEntry(i);

    string isotopeName(element->Data());
    double frac(0.0);
    if (total > 0.0) {frac = rate/total;}
    nuclide theIsotope(isotopeName, Z, A, m, rate, frac);

    if (iTime != jTime) {

      // We have a new iTime value. Store the previous results in the map
      // and start processing the next batch of isotopes

      theMap_[jTime] = nuclideList;
      nuclideList.clear();
      jTime = iTime;

      // Also store the previous time
      cout<<"Within loop. Adding time "<<prevTime<<endl;
      decayTimes_.push_back(prevTime);

    }

    prevTime = time;

    // Only add the isotope if the fraction is > minFrac_
    if (frac > minFrac_) {

      nuclideList.push_back(theIsotope);

      // Sort the vector of nuclides according to the yield rate (descending order)
      std::sort(nuclideList.rbegin(), nuclideList.rend());

    }

  }

  // Store the final iTime nuclide list
  int maxITime = theTree->GetMaximum("iTime");
  if (maxITime > 0) {
    theMap_[iTime] = nuclideList;
    cout<<"Final time "<<prevTime<<endl;
    decayTimes_.push_back(prevTime);
  }

  // Print out the map info
  nuclideMap::iterator mapIter;

  // Store a vector of all of the unique isotopes for a time history plot.
  // This will define how many bins there will be for the "x" axis.
  // y axis = time; z axis (vertical) will be the isotope rate.
  uniqueIsotopes_.clear();

  for (mapIter = theMap_.begin(); mapIter != theMap_.end(); ++mapIter) {

    int iTime = mapIter->first;
    if (iTime == 0) {continue;} // Skip t = 0 results

    vector<nuclide> nuclideVect = mapIter->second;

    cout<<"For iTime = "<<iTime<<" there are "<<nuclideVect.size()<<" isotopes"<<endl;

    vector<nuclide>::iterator vectIter;
    for (vectIter = nuclideVect.begin(); vectIter != nuclideVect.end(); ++vectIter) {

      nuclide theIsotope = (*vectIter);

      cout<<"Isotope "<<theIsotope.name<<"-"<<theIsotope.A
	  <<"("<<theIsotope.m<<") has a rate "<<theIsotope.rate
	  <<" ("<<theIsotope.frac*100.0<<"%)"<<endl;

      // Store the isotope in the unique list as required
      bool gotNewIsotope(true);
      vector<nuclide>::iterator uniqueIter;
      for (uniqueIter = uniqueIsotopes_.begin(); uniqueIter != uniqueIsotopes_.end(); ++uniqueIter) {

	nuclide tempIsotope = (*uniqueIter);

	if (tempIsotope == theIsotope) {gotNewIsotope = false; break;}

      }
      
      if (gotNewIsotope == true) {
	uniqueIsotopes_.push_back(theIsotope);
      }

    }

  }

  nUnique = uniqueIsotopes_.size();
  cout<<"There are "<<nUnique<<" unique isotopes"<<endl;
  for (i = 0; i < nUnique; i++) {

    nuclide theIsotope = uniqueIsotopes_[i];
    cout<<"isotope "<<theIsotope.name<<"-"<<theIsotope.A<<"("<<theIsotope.m<<")"<<endl;

  }

  theFile->Close();

  // Return the number of unique isotopes
  return nUnique;
  
}

void decays::plotIsotopeHistos() {

  // Generate a "3D" plot of the isotope production. Axes are:
  // x = isotope name (1 bin per new isotope)
  // y = decay time
  // z (height) = yield rate

  // Use the uniqueIsotopes vector to find out the number of x bins
  // Then get the nuclide map to plot z vs y for each isotope x bin.
  gROOT->SetStyle("Plain");
  gStyle->SetOptStat(0);
  //gStyle->SetPalette(1);

  TCanvas* theCanvas = new TCanvas("theCanvas", "", 900, 600);
  theCanvas->UseCurrentStyle();
  theCanvas->cd(1);

  int nXBins = uniqueIsotopes_.size();

  // Create the y binning using an array containing the starting positions
  // of the bins such that they are equidistant in log(10). This means
  // we need to have bins at 1, 10, 100, 1000, etc..
  const int nYBins = decayTimes_.size();
  double yBins[nYBins+1];
  int i;

  for (i = 0; i < nYBins; i++) {

    double decayTime = decayTimes_[i]*yearFactor_; // Decay time in years

    if (i == 0 && decayTime < 1.0e-4) {
      yBins[i] = 1.0e-4;
    } else {
      yBins[i] = decayTime;
    }

    //cout<<"Setting yBins["<<i<<"] = "<<yBins[i]<<endl;

  }

  yBins[nYBins] = yBins[nYBins-1]*2.0;
  //cout<<"Last bin is "<<yBins[nYBins]<<endl;

  TH2F* histo = new TH2F("isotopePlot", "", nXBins+2, -1.0, nXBins+1.0, nYBins, yBins);
  histo->SetMarkerStyle(8);
  // Reduce number of tick marks on the x axis
  histo->GetXaxis()->SetNdivisions(5);

  TLatex* text = new TLatex();

  map<TString, pair<double, double> > stringMap;

  double minRate(1.0e20);

  // Loop over all unique isotopes
  for (i = 0; i < nXBins; i++) {

    nuclide theIsotope = uniqueIsotopes_[i];
    bool writtenLabel(false);

    // For each unique isotope, get all possible rate values (vs decay time)
    nuclideMap::iterator mapIter;
    for (mapIter = theMap_.begin(); mapIter != theMap_.end(); ++mapIter) {

      int iTime = mapIter->first;
      if (iTime == 0) {continue;}

      double timeYrs = decayTimes_[iTime]*yearFactor_;
      if (timeYrs < 1e-4) {timeYrs = 1e-4;}

      vector<nuclide> nuclideVect = mapIter->second;
      vector<nuclide>::iterator nuclideIter;
      for (nuclideIter = nuclideVect.begin(); nuclideIter != nuclideVect.end(); ++nuclideIter) {

	nuclide theNuclide = (*nuclideIter);
	if (theNuclide == theIsotope) {

	  // Add the isotope information to the plot
	  double rate = theNuclide.rate;

	  //cout<<"Histogram: "<<theNuclide.name<<"-"<<theNuclide.A<<", time, rate="<<timeYrs<<", "<<rate<<endl;

	  histo->Fill(i*1.0, timeYrs, rate);

	  if (rate < minRate) {minRate = rate;}

	  // Set a label denoting the isotope name

	  if (writtenLabel == false) {

	    TString nuclideName = theNuclide.name;
	    nuclideName += "-"; nuclideName += theNuclide.A;

	    if (theNuclide.m > 0) {
	      nuclideName += "("; nuclideName += theNuclide.m; nuclideName += ")";
	    }

	    text->SetTextAngle(90.0);
	    double xCoord = i + 0.55;
	    double yCoord = timeYrs*1.25;
	    //cout<<"Label is "<<nuclideName.Data()<<" at "<<xCoord<<", "<<yCoord<<endl;
	    pair<double, double> coords(xCoord, yCoord);

	    stringMap[nuclideName] = coords;
	    writtenLabel = true;

	  }

	} // Matching nuclide

      } // All nuclides for this time interval

    } // Time interval loop

  } // Number of unique nuclides/isotopes

  histo->SetXTitle("Isotope Index (descending activity)");
  histo->SetYTitle("Decay time (years) after 1 run yr");
  histo->SetZTitle("Activity (Bq)");
  //histo->SetZTitle("Specific Activity (Bq/g)");
  histo->GetZaxis()->CenterTitle();
  histo->GetXaxis()->CenterTitle();
  histo->SetTitleOffset(1.25, "Y");
  histo->SetTitleOffset(1.25, "X");

  gPad->SetLogy(1);
  gPad->SetLogz(1);
  gPad->SetRightMargin(0.125);

  //cout<<"Minimum decay rate is "<<minRate<<endl;
  histo->SetMinimum(minRate*0.9); // Needed to avoid min = 1 always for z colour axis
  histo->Draw("colz");

  // Place dotted horizontal lines to indicate the decay time intervals
  int nTimes = decayTimes_.size();
  text->SetTextSize(0.025);
  text->SetTextAngle(0.0);
  
  for (i = 0; i < nTimes; i++) {

    double timeYrs = decayTimes_[i]*yearFactor_;
    TLine* line = new TLine(-1.0, timeYrs, nXBins+1.0, timeYrs);
    line->SetLineColor(kBlack);
    line->SetLineStyle(2);
    line->SetLineWidth(1);
    line->Draw();
  
    string timeLabel("");

    if (i == 1) {
      timeLabel = "1 hr";
    } else if (i == 3) {
      timeLabel = "1 day";
    } else if (i == 4) {
      timeLabel = "1 wk";
    } else if (i == 5) {
      timeLabel = "1 mth";
    }

    text->DrawText((nXBins + 1.0)*0.925, timeYrs, timeLabel.c_str());

  }

  // Finally, print out the isotope names for each nuclide bin
  text->SetTextAngle(90.0);
  double textSize = 0.045 - 0.0005*nXBins;
  text->SetTextSize(textSize);

  map<TString, pair<double, double> >::iterator nameIter;
  for (nameIter = stringMap.begin(); nameIter != stringMap.end(); ++nameIter) {

    TString nuclideName = nameIter->first;
    pair<double, double> coords = nameIter->second;

    double xCoord = coords.first;
    double yCoord = coords.second;

    //cout<<"Label "<<nuclideName.Data()<<": "<<xCoord<<", "<<yCoord<<endl;
    text->DrawText(xCoord, yCoord, nuclideName.Data());

  }
  
  if (detName_) {
      TString psFileName("pngFiles/");
      psFileName += detName_->Data();
      psFileName += "Isotopes.png";      
      theCanvas->Print(psFileName.Data());
  }

  // Write out histogram: these don't store the isotope names
  /*TFile* theFile = TFile::Open(outputName_.c_str(), "update");
  if (theFile) {
      histo->Write();
      theFile->Close();
      }*/
  
  delete theCanvas;
  
}

void decays::plotIsotopeGraphs(int maxNGraphs) {

    // Plot the activity of isotopes as a function of decay time
    int nIsotopes = uniqueIsotopes_.size();

    TLegend* legend = new TLegend(0.80, 0.60, 0.90, 0.90, "");
    legend->SetTextSize(0.03);
    legend->SetFillColor(0);

    TMultiGraph* isoGraphs = new TMultiGraph();
    isoGraphs->SetName("isotopeRates");
    isoGraphs->SetTitle("isotopeRates");
    
    int nTimes = decayTimes_.size();
    double minRate(-1.0), maxRate(0.0);

    int colours[5] = {kBlack, kRed, kBlue, kGreen+2, kMagenta};
    int styles[2] = {kFullCircle, kFullCross};
    
    // Loop over isotopes (up to a maximum number to avoid too many graphs)
    for (int i = 0; i < nIsotopes; i++) {

	if (i >= maxNGraphs) {
	    std::cout<<"Reached max number of graphs: " <<maxNGraphs
		     <<". Ignoring the remaining "<<nIsotopes-maxNGraphs
		     <<" isotopes"<<endl;
	    break;
	}

	TGraph* graph = new TGraph(nTimes-1);
	graph->SetMarkerStyle(styles[i/5]);
	graph->SetMarkerColor(colours[i%5]);
	graph->SetLineColor(colours[i%5]);

	nuclide theIsotope = uniqueIsotopes_[i];
	TString isotopeName = theIsotope.name;
	isotopeName += "-"; isotopeName += theIsotope.A;

	if (theIsotope.m > 0) {
	    isotopeName += "("; isotopeName += theIsotope.m; isotopeName += ")";
	}

	// Set the graph name
	TString graphName(isotopeName); graphName += "Rate";
	graph->SetName(graphName);
	graph->SetTitle(graphName);
	
	// Loop over all decay times (except t = 0)
	for (int iTime = 1; iTime < nTimes; iTime++) {

	    double timeYrs = decayTimes_[iTime]*yearFactor_;
	    if (timeYrs < 1e-4) {timeYrs = 1e-4;}

	    // Get the list of nuclides available for the given time
	    vector<nuclide> nuclideVect = theMap_[iTime];

	    // Find the isotope
	    vector<nuclide>::iterator iter = std::find(nuclideVect.begin(), nuclideVect.end(),
						       theIsotope);
	    double rate(0.0);
	    if (iter != nuclideVect.end()) {
		
		// Add the isotope rate to the graph
		rate = iter->rate;

		// Keep track of min and max isotope rates
		if (minRate < 0.0) {minRate = rate;}
		if (rate > maxRate) {maxRate = rate;}
		if (rate < minRate) {minRate = rate;}
		
	    } // find nuclide rate

	    graph->SetPoint(iTime, timeYrs, rate);

	} // loop over decay times

	// Append to multigraph
	isoGraphs->Add(graph);

	// Add graph to the legend
	if (graph->GetN() > 0) {
	    legend->AddEntry(graph, isotopeName.Data(), "pl");
	}

    } // isotope loop 

    // Plot the graphs
    gROOT->SetStyle("Plain");
    gStyle->SetOptStat(0);
    gStyle->SetPadGridX(kTRUE);
    gStyle->SetPadGridY(kTRUE);
    gStyle->SetPadTickY(1); // Add right side tick marks
    TCanvas* theCanvas = new TCanvas("theCanvas", "", 900, 600);
    theCanvas->UseCurrentStyle();
    theCanvas->cd(1);

    //cout<<"minRate = "<<minRate<<", maxRate = "<<maxRate<<endl;
    // Draw empty 2D histogram for x axis, especially for the time axis.
    // Otherwise the multigraph does not plot the very small decay times.
    // x axis = decay time (log scale), y axis = rate (log scale)
    TH2F* nullHist = new TH2F("nullHist", "", 8, 1e-4, 1e3, 2, minRate*0.5, maxRate*2.0);
    nullHist->SetXTitle("Decay time (years) after 1 run yr");
    nullHist->SetYTitle("Activity (Bq)");
    nullHist->SetTitleOffset(1.25, "X");
    nullHist->GetXaxis()->CenterTitle(kTRUE);
    nullHist->Draw();
    
    isoGraphs->Draw("p");
    gPad->SetLogx();
    gPad->SetLogy();
    legend->Draw("same");

    TText* text = new TText();
    text->SetTextSize(0.025);

    double daySec = 60.0*60.0*24.0;
    text->DrawText(yearFactor_*3600.0, maxRate*2.1, "1 hr");
    text->DrawText(yearFactor_*daySec, maxRate*2.1, "1 day");
    text->DrawText(yearFactor_*daySec*7.0, maxRate*2.1, "1 wk");
    text->DrawText(1.0/12.0, maxRate*2.1, "1 mth");
    
    theCanvas->Update();

    if (detName_) {
	TString pngFile("pngFiles/");
	pngFile += detName_->Data();
	pngFile += "GraphIsotopes.png";
	theCanvas->Print(pngFile.Data());
    }

    TFile* theFile = TFile::Open(outputName_.c_str(), "update");
    if (theFile) {
	isoGraphs->Write();
	theFile->Close();
    }

    delete text;
    delete legend;
    delete isoGraphs;
    delete nullHist;
    delete theCanvas;
    
}

void decays::plotIsotopeMasses(int maxNGraphs) {

    // Plot the isotope masses as a function of decay time
    // from the (specific) activities

    int nIsotopes = uniqueIsotopes_.size();
    
    TLegend* legend = new TLegend(0.80, 0.60, 0.90, 0.90, "");
    legend->SetTextSize(0.03);
    legend->SetFillColor(0);

    TMultiGraph* isoGraphs = new TMultiGraph();
    isoGraphs->SetName("isotopeMasses");
    isoGraphs->SetTitle("isotopeMasses");

    int nTimes = decayTimes_.size();
    double minMass(-1.0), maxMass(0.0);

    int colours[5] = {kBlack, kRed, kBlue, kGreen+2, kMagenta};
    int styles[2] = {kFullCircle, kFullCross};
    
    // Loop over isotopes and set graph points
    for (int i = 0; i < nIsotopes; i++) {

	if (i >= maxNGraphs) {
	    std::cout<<"Reached max number of graphs: " <<maxNGraphs
		     <<". Ignoring the remaining "<<nIsotopes-maxNGraphs
		     <<" isotopes"<<endl;
	    break;
	}

	TGraph* graph = new TGraph(nTimes-1);	
	graph->SetMarkerStyle(styles[i/5]);
	graph->SetMarkerColor(colours[i%5]);
	graph->SetLineColor(colours[i%5]);

	nuclide theIsotope = uniqueIsotopes_[i];
	TString isotopeName = theIsotope.name;
	isotopeName += "-"; isotopeName += theIsotope.A;

	if (theIsotope.m > 0) {
	    isotopeName += "("; isotopeName += theIsotope.m; isotopeName += ")";
	}

	// Label the graph with the isotope name
	TString graphName(isotopeName); graphName += "Mass";
	graph->SetName(graphName.Data());
	graph->SetTitle(graphName.Data());
	
	// Retrieve the material database info to get the radionuclide
	// specific activity via the half life
	const TGeoElementRN* radNucl = elements_->GetElementRN(theIsotope.A, theIsotope.Z,
							       theIsotope.m);
	// Activity R = dN/dt = ln(2)*N/tHalf
	// Lower (higher) tHalf => higher (lower) activity
	// Specific activity RSpec = ln(2)*N_A/(tHalf*A) = activity of 1 gram
	// So total mass of isotope (grams) = R/RSpec
	double sActivity(0.0);
	if (radNucl) {sActivity = radNucl->GetSpecificActivity();}

	// Loop over all decay times (except t = 0)
	for (int iTime = 1; iTime < nTimes; iTime++) {

	    double timeYrs = decayTimes_[iTime]*yearFactor_;
	    if (timeYrs < 1e-4) {timeYrs = 1e-4;}

	    // Get the list of nuclides available for the given time
	    vector<nuclide> nuclideVect = theMap_[iTime];

	    // Find the isotope
	    std::vector<nuclide>::iterator iter = std::find(nuclideVect.begin(), nuclideVect.end(),
							    theIsotope);
	    double massmg(0.0);
	    if (iter != nuclideVect.end()) {
	    
		// Add the isotope mass information to the graph
		double rate = iter->rate;
		if (rate > 0.0 && sActivity > 0.0) {
		    // mass in milligrams
		    massmg = rate*1000.0/sActivity;
		}

		// Keep track of min and max isotope rates
		if (minMass < 0.0) {minMass = massmg;}
		if (massmg > maxMass) {maxMass = massmg;}
		if (massmg < minMass) {minMass = massmg;}
		    
	    } // find nuclide

	    graph->SetPoint(iTime, timeYrs, massmg);

	} // loop over decay times

	// Append to multigraph
	isoGraphs->Add(graph);

	// Add graph to the legend
	if (graph->GetN() > 0) {
	    legend->AddEntry(graph, isotopeName.Data(), "pl");
	}

    } // isotope loop 

    // Plot the graphs
    gROOT->SetStyle("Plain");
    gStyle->SetOptStat(0);
    gStyle->SetPadGridX(kTRUE);
    gStyle->SetPadGridY(kTRUE);
    gStyle->SetPadTickY(1); // Add right side tick marks
    TCanvas* theCanvas = new TCanvas("theCanvas", "", 900, 600);
    theCanvas->UseCurrentStyle();
    theCanvas->cd(1);

    //cout<<"minMass = "<<minMass<<", maxMass = "<<maxMass<<endl;
    // Draw empty 2D histogram for x axis, especially for the time axis.
    // Otherwise the multigraph does not plot the very small decay times.
    // x axis = decay time (log scale), y axis = mass (log scale)
    TH2F* nullHist = new TH2F("nullHist", "", 8, 1e-4, 1e3, 2, minMass*0.5, maxMass*2.0);
    nullHist->SetXTitle("Decay time (years) after 1 run yr");
    nullHist->SetYTitle("Isotope mass quantity (mg)");
    nullHist->SetTitleOffset(1.25, "X");
    nullHist->GetXaxis()->CenterTitle(kTRUE);
    nullHist->Draw();
    
    isoGraphs->Draw("p");
    gPad->SetLogx();
    gPad->SetLogy();
    legend->Draw("same");

    TText* text = new TText();
    text->SetTextSize(0.025);

    double daySec = 60.0*60.0*24.0;
    text->DrawText(yearFactor_*3600.0, maxMass*2.1, "1 hr");
    text->DrawText(yearFactor_*daySec, maxMass*2.1, "1 day");
    text->DrawText(yearFactor_*daySec*7.0, maxMass*2.1, "1 wk");
    text->DrawText(1.0/12.0, maxMass*2.1, "1 mth");
    
    theCanvas->Update();

    if (detName_) {
	TString pngFile("pngFiles/");
	pngFile += detName_->Data();
	pngFile += "MassIsotopes.png";
	theCanvas->Print(pngFile.Data());
    }

    TFile* theFile = TFile::Open(outputName_.c_str(), "update");
    if (theFile) {
	isoGraphs->Write();
	theFile->Close();
    }
    
    delete text;
    delete legend;
    delete isoGraphs;
    delete nullHist;
    delete theCanvas;
    
}

void decays::getTotActivity() {

  gROOT->SetStyle("Plain");
  gStyle->SetOptStat(0);
  //gStyle->SetPalette(1);

  TCanvas* theCanvas = new TCanvas("theCanvas", "", 900, 600);
  theCanvas->UseCurrentStyle();
  theCanvas->cd(1);

  TFile* theFile = TFile::Open(outputName_.c_str(), "update");
  if (!theFile) {
      cout<<"Could not open file "<<outputName_<<endl;
      return;
  }
  TTree* theTree = dynamic_cast<TTree*>(theFile->Get("Data"));

  int iTime(0);
  double time(0.0), total(0.0);
  detName_ = 0;

  theTree->SetBranchAddress("iTime", &iTime);
  theTree->SetBranchAddress("time", &time);
  theTree->SetBranchAddress("total", &total);
  theTree->SetBranchAddress("detector", &detName_);

  double minTotal = theTree->GetMinimum("total");
  double maxTotal = theTree->GetMaximum("total");

  int nEntries = static_cast<int>(theTree->GetEntries());

  TGraph* totalGraph = new TGraph();

  int i(0), iPoint(0), jTime(-1);

  for (i = 0; i < nEntries; i++) {

    theTree->GetEntry(i);

    if (time > 0.0 && iTime != jTime) {

      double timeYrs = time*yearFactor_;

      totalGraph->SetPoint(iPoint, timeYrs, total);

      jTime = iTime;
      iPoint++;

    }

  }
  
  gPad->SetLogx();
  gPad->SetLogy();
  
  int iyMax = static_cast<int>(log10(maxTotal));
  double histMax = pow(10.0, iyMax+1.2);
  int iyMin = static_cast<int>(log10(minTotal));
  double histMin = pow(10.0, iyMin-1);
  
  TString nullName("null_");
  if (detName_) {nullName += detName_->Data();}
  nullName += "Hist";
  TH2F* nullHist = new TH2F(nullName.Data(), "", 2, 1e-4, 1e3, 2, histMin*0.999, histMax);
  nullHist->SetXTitle("Decay time (years) after 1 run yr");
  nullHist->SetYTitle("Total activity (Bq)");
  //nullHist->SetYTitle("Total specific activity (Bq/g)");
  nullHist->GetXaxis()->CenterTitle();
  nullHist->GetYaxis()->CenterTitle();
  nullHist->SetTitleOffset(1.25, "X");
  nullHist->SetTitleOffset(1.25, "Y");
  nullHist->Draw();

  // Put labels above points
  // Points are arranged in the following order: 
  // 1hr, 8hrs, 1day, 1week, 1mnt, 6 mnt, 1yr, then 2, 3, 5, 10, 50, 100 years
  TLatex* text = new TLatex();
  text->SetTextSize(0.035);

  int nPoints = static_cast<int>(totalGraph->GetN());
  for (i = 0; i < nPoints; i++) {

    double xPoint(0.0), yPoint(0.0);
    totalGraph->GetPoint(i, xPoint, yPoint);
    yPoint *= 2.0;
    xPoint *= 0.75;

    string timeLabel("");

    if (i == 0) {
      timeLabel = "1 hour";
    } else if (i == 2) {
      timeLabel = "1 day";
    } else if (i == 3) {
      timeLabel = "1 week";
      yPoint *= 1.25;
    } else if (i == 4) {
      timeLabel = "1 month";
      yPoint *= 0.75;
    } else if (i == 6) {
      timeLabel = "1 year";
    } else if (i == 10) {
      timeLabel = "10 years";
    }

    text->DrawText(xPoint, yPoint, timeLabel.c_str());

  }

  //text->SetTextColor(kBlue);
  //text->SetTextSize(0.05);
  //text->DrawTextNDC(0.75, 0.75, detName_->Data());

  totalGraph->SetMarkerStyle(8);
  totalGraph->Draw("cp same");

  if (detName_ && totalGraph->GetN() > 0) {
      TString plotName("pngFiles/"); 
      plotName += detName_->Data();
      plotName += "TotActivity.png";
      theCanvas->Print(plotName.Data());
  }

  gPad->SetLogx(0);
  gPad->SetLogy(0);
  
  // Store the graph in the output file
  if (detName_) {
      TString graphName(detName_->Data());
      graphName += "TotActivity";
      totalGraph->SetName(graphName.Data());
      totalGraph->Write(graphName.Data());
  }

  delete totalGraph;
  delete nullHist;

  theFile->Close();

  delete theCanvas;

}

vector<string> decays::splitString(string& theString, string& splitter) const {

  // Code from STLplus
  vector<string> result;

  if (!theString.empty() && !splitter.empty()) {
    
    for (string::size_type offset = 0;;) {

      string::size_type found = theString.find(splitter, offset);

      if (found != string::npos) {
	string tmpString = theString.substr(offset, found-offset);
	if (tmpString.size() > 0) {result.push_back(tmpString);}
        offset = found + splitter.size();
      } else {
	string tmpString = theString.substr(offset, theString.size()-offset);
	if (tmpString.size() > 0) {result.push_back(tmpString);}
        break;
      }
    }
  }

  return result;
}

int main(int argc, char** argv) {

  decays myDecay;
  string dirName("LBNFTargetL150cmSpacersAll");
  string label("Target");

  if (argc > 1) {dirName = string(argv[1]);}
  if (argc > 2) {label = string(argv[2]);}
  
  TString fileName(dirName.c_str());
  fileName += "/"; fileName += label.c_str();
  fileName += "Evolution.txt";

  TString outputName(fileName);
  outputName.ReplaceAll(".txt", ".root");

  myDecay.readInputFile(fileName.Data(), outputName.Data());
  myDecay.createPlots();

  return 0;

}
