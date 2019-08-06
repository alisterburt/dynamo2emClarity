# dynamo2emClarity
A tool for conversion between subtomogram averaging softwares Dynamo and emClarity

Tested and working with python 3.7 and numpy 1.17 (should work with any version of python3 and numpy)

## Files needed
* Dynamo format table file as per the [dynamo table convention](https://wiki.dynamo.biozentrum.unibas.ch/w/index.php/Table_convention)
* Dynamo format table map file as per the [convention](https://wiki.dynamo.biozentrum.unibas.ch/w/index.php/Tomogram-table_map_file)

## How to run
Download or clone the whole repository
Open the dynamo2emClarity.py file and change the variables as necessary in the SETUP section (lines 5-26)
In a terminal run `python dynamo2emClarity.py` making sure `python` points to a python3 interpreter with numpy installed


## Known issues
* Tomograms in which dynamo particles are defined must exist, their size is checked.
* Tomograms in which dynamo particles are defined must be full reconstructions, not trimmed or shiften in X, Y or Z
* Tomograms in which dynamo particles are defined must be rotated by 90 degrees around the X axis for volume reorientation, not Y-Z flipped
