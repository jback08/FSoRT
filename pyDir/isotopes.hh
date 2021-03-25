#ifndef ISOTOPES_HH
#define ISOTOPES_HH

#include "TH2.h"
#include "TString.h"

#include <map>
#include <string>
#include <vector>

class TCanvas;
class TGeoManager;
class TGeoElementTable;
class TGraph;
class TText;

class massWeight {

public:

    massWeight(int A, double weight, double error);

    int getA() const {return m_A;}
    double getWeight() const {return m_weight;}
    double getError() const {return m_error;}
    double getFracError() const;
    
private:

    int m_A;
    double m_weight;
    double m_error;
    
};

class isotopes {

    enum PlotOption {ZOpt = 0, AOpt = 1};

public:

    isotopes(const TString& fileDir);
    virtual ~isotopes();

    void run();
    
private:

    typedef std::map<TString, std::vector<TString> > mapStrings;
    void defineRegions();

    void plot1D(const TString& totName, const std::vector<TString>& volList,
		const PlotOption& option) const;

    void plotAZ(const TString& totName, const std::vector<TString>& volList) const;

    void writeOutAZValues(const TString& totName, const TH2D& AZHist,
			  const TH2D& AZErrHist) const;

    std::string getElementName(const int Z) const;
    std::string getIsotopeName(const int Z, const int A, const int m) const;
    std::string breakStringAtCaps(const std::string& input) const;
    void formatOutput(std::ofstream& writeData, double value, double fracErr) const;
    
    double m_yearFactor; // How many years are in one second
    TString m_fileDir;
    mapStrings m_regions;
    TCanvas* m_canvas;
    TText* m_text;
    
};

#endif
