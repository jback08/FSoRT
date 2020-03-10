Directory containing Fluka files for the simulation of the 3 RAL target options inside the 1st LBNF Horn A:

Option 1: LongTargetDS.inp, the 2.2 m long, single downstream (DS) supported target (cone and spokes)

Option 2: DoubleTarget.inp, two 1 m long targets with supports, including downstream He cone structure

Option 3: SingleTarget.inp, the 1.5 m long cantilevered single target, no downstream support

The Horn A magnetic field is implemented using the magfld.f code in the usermvax subdirectory 
(which uses fieldarray.inc), along with the field map data stored in FieldMap3D.dat.

The text file linkField.txt shows the compilation commands that are needed to link in the B field routine.

==========================================================================================================

The defined energy histograms units are GeV/cc/primary proton, so to get J/cc/pulse each bin needs to be
multiplied by the scaling factor 1.602e-10*7.5e13, where the first factor is for GeV to J and the second
factor is the POT/pulse for a 1.2 sec pulse for a 120 GeV proton beam at 1.2 MW. 

Binning information is given below. The Flair GUI can be used to visualize the geometry and plot histograms.


LongTargetDS (option 1, L = 2.2 m, R = 8 mm): 

fort.21 r = 0 to 30 cm, dr = 1 mm; z = -20 to 240 cm, dz = 1 cm; all regions
              
fort.22 r = 0 to 24 cm, dr = 1 mm; z = -20 to 0 cm, dz = 1 mm; upstream region
	      
fort.23 r = 0 to 2.5 cm, dr = 0.25 mm; z = -20 to 0 cm, dz = 0.25 mm; bafflette
	      
fort.24 r = 0 to 5 cm, dr = 0.25 mm; z = -5 to 230 cm, dz = 0.5 cm; target region
	      
fort.25 r = 0 to 1 cm, dr = 0.25 mm; z = 0 to 220 cm, dz = 0.5 cm; target core
	      
fort.26 r = 0 to 24 cm, dr = 1 mm; z = 225 to 230 cm, dz = 0.5 mm; downstream (DS) region
	      
fort.27 r = 0 to 5 cm, dr = 0.25 mm; z = 225 to 230 cm, dz = 0.25 mm; DS inner cone
	      
fort.28 r = 0 to 24 cm, dr = 1 mm; z = 225.8 to 226.6 cm, dz = 0.25 mm; 72 bins in phi; 1st 3 spokes at z = 226.2 cm
	      
fort.29 r = 0 to 24 cm, dr = 1 mm; z = 228.2 to 229 cm, dz = 0.25 mm; 72 bins in phi; 2nd 3 spokes at z = 228.6 cm

fort.50 Input beam distribution


DoubleTarget (option 2, L = 2 x 1 m, R = 8 mm):

fort.21 r = 0 to 30 cm, dr = 1 mm; z = -20 to 240 cm, dz = 1 cm; all regions

fort.22 r = 0 to 24 cm, dr = 1mm; z = -20 to 0 cm, dz = 1mm; upstream region

fort.23 r = 0 to 2.5 cm, dr = 0.25 mm; z = -20 to 0 cm, dz = 0.25 mm; bafflette

fort.24 r = 0 to 5 cm, dr = 0.25 mm; z = -5 to 115 cm, dz = 5 mm; 1st target region

fort.25 r = 0 to 1 cm, dr = 0.25 mm; z = 0 to 100 cm, dz = 5 mm; 1st target core

fort.26 r = 0 to 5 cm, dr = 0.25 mm; z = 110 ro 235 cm, dz = 5 mm; 2nd target region

fort.27 r = 0 to 1 cm, dr = 0.25 mm; z = 112 to 223 cm, dz = 5 mm; 2nd target core

fort.28 r = 0 to 25 cm, dr = 1 mm; z = 216 to 236 cm, dz = 1 mm; DS support area

fort.29 r = 0 to 5 cm, dr = 0.5 mm; z = 216 to 236 cm, dz = 1 mm; DS support area zoom


fort.31 r = 0 to 0.8 cm, dr = 0.25 mm; z = 112.65 to 222.65 cm, dz = 1 cm; 2nd target core

fort.32 r = 2.7 to 2.8 cm, dr = 0.5 mm; z = 118 to 225, dz = 1 cm; 2nd target flow divider

fort.33 r = 2.8 to 2.88 cm, dr = 0.2 mm; z = 117.8 to 222.65 cm, dz = 1 cm; 2nd target outer can

fort.34 x = 1 to 24 cm, dx = 5 mm; y = -1 to 1 mm, dy = 1 mm; z = 225 to 230.3, dz = 2.65 mm; horizontal fin

fort.35 r = 0 to 2.9 cm, dr = 0.25 mm; z = 116.3 to 118 cm, dz = 0.25 mm; 2nd target entry beam window

fort.36 r = 0 to 20.5 cm, dr = 0.5 mm; z = 222.5 to 232.5 cm, dz = 0.4 mm; tapered DS support

fort.37 r = 20.5 to 24 cm, dr = 1 mm; z = 219.5 to 236 cm, dz = 1 mm; outer support ring

fort.38 r = 0 to 5 cm, dr = 0.25 mm; z = 229.9 to 232.3 cm, dz = 0.25 mm; 2nd target exit beam window

fort.50 Input beam distribution


SingleTarget (option 3, L = 1.5 m, R = 8 mm):

fort.21 r = 0 to 30 cm, dr = 1 mm; z = -20 to 240 cm, dz = 1 cm; all regions

fort.22 r = 0 to 24 cm, dr = 1mm; z = -20 to 0 cm, dz = 1mm; upstream region

fort.23 r = 0 to 2.5 cm, dr = 0.25 mm; z = -20 to 0 cm, dz = 0.25 mm; bafflette

fort.24 r = 0 to 5 cm, dr = 0.25 mm; z = -5 to 160 cm, dz = 5 mm; target region

fort.25 r = 0 to 1 cm, dr = 0.25 mm; z = 0 to 150 cm, dz = 5 mm; target core

fort.50 Input beam distribution
