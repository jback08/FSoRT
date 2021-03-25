#ifndef DECAYS_HH
#define DECAYS_HH

#include "TGeoManager.h"
#include "TString.h"

#include <string>
#include <vector>
#include <map>

using std::string;
using std::vector;
using std::map;

struct nuclide {

  string name;
  int Z, A, m;
  double rate;
  double frac;
  nuclide(string name, int Z, int A, int m, double rate, double frac) :
      name(name), Z(Z), A(A), m(m), rate(rate), frac(frac) {};

  bool operator < (const nuclide& other) const {
    // Sort according to activity rate (descending)
    return rate < other.rate;
  }

  bool operator == (const nuclide& other) const {

    bool result(false);

    if (Z == other.Z && A == other.A && m == other.m) {
      result = true;
    }

    return result;

  }

};

class decays {

 public:

  decays();
  virtual ~decays();

  void readInputFile(string fileName, string outputName);

  void createPlots();

 private:

  vector<string> splitString(string& theString, string& splitter) const;
  void getTotActivity();
  int getIsotopes();
  void plotIsotopeHistos();
  void plotIsotopeGraphs(int maxNGraphs = 10);
  void plotIsotopeMasses(int maxNGraphs = 10);

  string outputName_, theDetector_;
  double yearFactor_, minFrac_;
  TString* detName_;
  TGeoManager* geoManager_;
  TGeoElementTable* elements_;

  typedef map<int, vector<nuclide> > nuclideMap;

  nuclideMap theMap_;
  vector<nuclide> uniqueIsotopes_;
  vector<double> decayTimes_;

};

#endif
