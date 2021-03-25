# FSoRT
Fluka Simulation of the RAL/LBNF Target

This contains FLUKA input files and user routines for simulating various RAL
designs for the LBNF/DUNE target and first magnetic focusing horn system.

### Conceptual graphite target designs

1. `LongTargetDS.inp` : 2.2 m long single downstream (DS) supported target
2. `DoubleTarget.inp` : two 1 m long targets, including downstream He gas cone
3. `SingleTarget.inp` : 1.5 m long single target, no downstream support

For these, the Horn A magnetic field is implemented using the `usermvax/map_magfld.f` code,
which must be renamed as `magfld.f` before running the commands in `linkField.txt`, along
with `fieldarray.inc` and the field map data stored in `FieldMap3D.dat` (after it's unzipped).

### Preliminary graphite target designs

1. `LBNFTargetL150cm.inp` : 1.5 m cantilevered target with Horn A upstream inner conductor cone
2. `LBNFTargetL150cmSpacers.inp` : based on `LBNFTargetL150cm.inp` with target spacer supports
3. `LBNFTargetL150cmFins.inp` : based on `LBNFTargetL150cm.inp` with target fin supports
4. `LBNFTargetL150cmFinsOff1.inp` : based on `LBNFTargetL150cmFins.inp` with off-centred beam (1 sigma)
5. `LBNFTargetL150cmFinsOff2.inp` : based on `LBNFTargetL150cmFins.inp` with off-centred beam (2 sigma)
6. `LBNFTargetL150cmFinsOff3.inp` : based on `LBNFTargetL150cmFins.inp` with off-centred beam (3 sigma)

For these, the Horn A magnetic field is implemented using the `usermvax/magfld.f` code, which
uses the theoretical function `B = 0.02*I/r T` (a very good approximation), where `I` is
the horn current (kA) and `r` is the radius (cm). The current `I` is set within `FieldPars.dat`,
along with the field direction integer (1 for neutrino running, -1 for anti-neutrino running).

### Baffle

These simulate just the 2.5 m long graphite baffle that is upstream of the target and horn A region.
The beam has a maximum horizontal offset of 2.5 cm.

1. `LBNFBaffle.inp` : fins with edges that point to the origin; +2 deg phi rotation for usrbin alignment
2. `LBNFBaffle_WedgeFins.inp` : fins with edges that point to the origin, with no additional phi rotation
3. `LBNFBaffle_ParFins.inp` : fins with edges that are parallel to their mid-centre radial lines.
