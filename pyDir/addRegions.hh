#ifndef ADDREGIONS_HH
#define ADDREGIONS_HH

#include "TString.h"

#include <map>
#include <string>
#include <vector>

class TCanvas;
class TGeoManager;
class TGeoElementTable;
class TGraph;
class TText;

enum graphOpt {Rate = 0, Mass = 1};

class nuclide {

public:

    nuclide(const std::string& name, const int Z, const int A, const int m,
	    const std::vector<double>& times);

    virtual ~nuclide();
    nuclide(const nuclide& copy);
    
    void addRate(const int iTime, const double rate);
    double getRate(const int iTime) const;

    double getMassMu(const double rate) const;
    double getMassMu(const int iTime) const;
    
    const std::string getName() const {return m_name;}
    const int getZ() const {return m_Z;}
    const int getA() const {return m_A;}
    const int getm() const {return m_m;}

    const size_t getNTimes() const {return m_nTimes;}
    std::vector<double> getTimes() const {return m_times;}
    std::vector<double> getRates() const {return m_rates;}

    double getMaxRate() const;

    void print() const;

    bool sameIsotope(const int Z, const int A, const int m) const;

    bool operator < (const nuclide& other) const;
    bool operator == (const nuclide& other) const;
    
    // Return the decay rates or masses as graphs
    TGraph* getGraph(const graphOpt& option) const;

private:

    std::string m_name;
    int m_Z;
    int m_A;
    int m_m;
    std::vector<double> m_times;
    int m_nTimes;
    std::vector<double> m_rates;

};

// For sorting nuclide pointers in a list
bool compareNuclides(nuclide *lhs, nuclide* rhs) {
    return (*lhs) < (*rhs);
}


class addRegions {

public:

    addRegions(const TString& fileDir);
    virtual ~addRegions();

    void run();
    
private:

    typedef std::map<TString, std::vector<TString> > mapStrings;
    void defineRegions();

    std::vector<nuclide*> getNuclideList(const TString& totName,
					 const std::vector<TString>& volList);

    std::string getIsotopeName(const int Z, const int A, const int m) const;
    std::string breakStringAtCaps(const std::string& input) const;
    
    void createPlots(const TString& totName,
		     const std::vector<nuclide*>& nuclideList,
		     const graphOpt& option,
		     const int maxNGraphs = 10);

    double m_yearFactor; // How many years are in one second
    double m_BqToCurie; // Bq to Curie unit conversion
    TString m_fileDir;
    mapStrings m_regions;
    TCanvas* m_canvas;
    TText* m_text;
    
};

#endif
