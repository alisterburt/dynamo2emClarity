# dynamo2emClarity
A tool for conversion between subtomogram averaging softwares Dynamo and emClarity

This script takes a set of particle positions and orientations from a dynamo table, calculates subareas of the full tomograms containing particles which will fit in GPU memory and produces all the relevant metadata required to start an emClarity alignment project.

Tested and working with python 3.7 and numpy 1.17 (should work with any version of python3 and numpy)

## Files needed
* Dynamo format table file as per the [dynamo table convention](https://wiki.dynamo.biozentrum.unibas.ch/w/index.php/Table_convention)
* Dynamo format table map file as per the [convention](https://wiki.dynamo.biozentrum.unibas.ch/w/index.php/Tomogram-table_map_file)

## How to run
Download or clone the whole repository

In a terminal run `python dynamo2emClarity.py -arguments <inputs>` making sure `python` points to a python3 interpreter with numpy installed

USAGE: `dynamo2emClarity.py (argument1) <input1> (argument2) <input2>` etc...

    Abbreviation    Argument                 Input                   Default
    -t              (--table_file)           <dynamo_table_file>
    -o              (--output_dir)           <output_directory>
    -m              (--table_map_file)       <table_map_file>               
    -b              (--binning_table)        <binning_table>    
    -s              (--particle_sidelength)  <particle_sidelength>                     
    N/A             (--IMOD_bin_dir)         <IMOD_bin_dir>          default=/usr/local/IMOD/bin

## Output
The output folder you specified will contain two folders, recon and convmap

These folders can be copied directly into an emClarity project directory and the project can be initialised

## Known issues
* Tomograms in which dynamo particles are defined must exist, their size is checked.
* Tomograms in which dynamo particles are defined must be full reconstructions, not trimmed or shifted in X, Y or Z
* Tomograms in which dynamo particles are defined must be rotated by 90 degrees around the X axis for volume reorientation, not Y-Z flipped
