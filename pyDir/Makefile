# check that ROOTSYS is defined
ifndef ROOTSYS
  ROOTSYS = $(shell root-config --prefix)
  ifeq ($(ROOTSYS), )
    $(error running of root-config failed or reported null value)
  endif
endif

ROOTCFLAGS    = $(shell ${ROOTSYS}/bin/root-config --cflags)
ROOTLIBS      = $(shell ${ROOTSYS}/bin/root-config --libs)
ROOTGLIBS     = $(shell ${ROOTSYS}/bin/root-config --glibs)

CXX           = g++
CXXFLAGS      = -g -Wall -fPIC
LD            = g++
LDFLAGS       = -g
SOFLAGS       = -shared

CXXFLAGS      += $(ROOTCFLAGS)
LIBS           = $(ROOTLIBS) 
NGLIBS         = $(ROOTGLIBS) 
NGLIBS        += -lMinuit -lGeom
GLIBS          = $(filter-out -lNew, $(NGLIBS))

.SUFFIXES: .cc,.C

# ================================================================================
all: decays addRegions isotopes

decays: decays.o
	$(LD) $(LDFLAGS) -o decays decays.o $(GLIBS)

addRegions: addRegions.o
	$(LD) $(LDFLAGS) -o addRegions addRegions.o $(GLIBS)

isotopes: isotopes.o
	$(LD) $(LDFLAGS) -o isotopes isotopes.o $(GLIBS)

.cc.o:
	$(CXX) $(CXXFLAGS) -c $<
clean:
	rm -f decays addRegions isotopes *.o core
