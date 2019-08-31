import os
import sys
import getopt
import numpy as np
import utils

# Usage explanation
usage = """
USAGE: dynamo2emClarity.py (argument1) <input1> (argument2) <input2> etc...
    Abbreviation    Argument                 Input                   Default
    -t              (--table_file)           <dynamo_table_file>
    -o              (--output_dir)           <output_directory>
    -m              (--table_map_file)       <table_map_file>               
    -b              (--binning_table)        <binning_table>    
    -s              (--particle_sidelength)  <particle_sidelength>                     
    N/A             (--IMOD_bin_dir)         <IMOD_bin_dir>          default=/usr/local/IMOD/bin
"""


#####################
####### SETUP #######
#####################

### Set table file
TABLE_FILE = None

### Set dynamo format tomogram table map file (as per https://wiki.dynamo.biozentrum.unibas.ch/w/index.php/Tomogram-table_map_file) ###
TABLE_MAP_FILE = None

### Set output directory for CSV and recon_coords files
OUT_DIR = None

### Set IMOD bin directory
IMOD_BIN_DIR = '/usr/local/IMOD/bin/'

### Set current binning factor of coordinates in dynamo table file
BINNING_FACTOR_TABLE = None

### Set particle sidelength at current binning
SIDELENGTH_PARTICLE = None

if len(sys.argv) > 1:

    options, remainder = getopt.getopt(sys.argv[1:], 't:m:o:b:s:', ['table=',
                                                                   'table_map=',
                                                                   'output_dir=',
                                                                   'binning_table=',
                                                                   'particle_sidelength=',
                                                                   'IMOD_bin_dir'
                                                                   ])
    for opt, arg in options:
        if opt in ('-t', '--table_file'):
            TABLE_FILE = arg
        elif opt in ('-m', '--table_map_file'):
            TABLE_MAP_FILE = arg
        elif opt in ('-o', '--output_dir'):
            OUT_DIR = arg
        elif opt in ('-b', '--binning_table'):
            BINNING_FACTOR_TABLE = int(arg)
        elif opt in ('-s', '--particle_sidelength'):
            SIDELENGTH_PARTICLE = int(arg)
        elif opt == '--IMOD_bin_dir':
            IMOD_BIN_DIR = arg

    print("Running dynamo2emClarity.py using command line arguments...")

else:
    print(usage)
    print('Desisting...')
    sys.exit(0)

#####################
###### Running ######
#####################
if any(v is None for v in [TABLE_FILE, TABLE_MAP_FILE, OUT_DIR, BINNING_FACTOR_TABLE, SIDELENGTH_PARTICLE]):
    print(usage)
    print('Missing some necessary arguments, desisting...')
    sys.exit(0)

# Sanity checks on output directory
if not OUT_DIR.endswith('/'):
    OUT_DIR = OUT_DIR + '/'

# Sanity checks on IMOD dir
if not IMOD_BIN_DIR.endswith('/'):
    IMOD_BIN_DIR = IMOD_BIN_DIR + '/'

# make output,recon and convmap directory
os.makedirs('{}'.format(OUT_DIR), exist_ok=True)
os.makedirs('{}recon'.format(OUT_DIR), exist_ok=True)
os.makedirs('{}convmap'.format(OUT_DIR), exist_ok=True)

# Load table file
table = utils.DynamoTable(table_file=TABLE_FILE)

# Separate table into list of tables, one item per unique tomogram
list_of_tables = table.unique()

# Get number of tomograms
nTomos = len(list_of_tables)


def geometry_check(table_list):
    """Checks bounding boxes for a list of tables"""
    BB_pass = [utils.checkBoundingBox(table, SIDELENGTH_PARTICLE, BINNING_FACTOR_TABLE) for table in table_list]

    # check if any tables in list failed the check
    BB_pass = np.all(BB_pass)
    return BB_pass


# test = geometry_check(list_of_subtables)
# if table list doesn't pass geometry check, split tables RECURSIVE
def checkAndSplit(local_table):
    if utils.checkBoundingBox(local_table, 32, BINNING_FACTOR_TABLE):
        return [local_table]
    else:
        tmp_list_of_tables = local_table.split()
        result = checkAndSplit(tmp_list_of_tables[0])
        result.extend(checkAndSplit(tmp_list_of_tables[1]))
        return result


final_list = []
for table in list_of_tables:
    final_list.extend(checkAndSplit(table))

# Final list of tables now contains list of tables which will each need a subarea in emClarity
# For each table we need to change the reference frame
# We also need to know which tomogram each table comes from to count number of subareas per tomogram

nTables = len(final_list)
indices = range(nTables)

table_idx = []
euler_angles_emClarity = []
rotation_matrices_emClarity = []
# xyz coordinates are relative to origin of tomogram in which they were defined
# will be shifted relative to bounding box
xyz_binned = []
particle_tags = []
tomogram_files = []
bounding_boxes = []

for table in final_list:
    # Output table idx for each table
    table.tomos()
    table_idx.append(table.unique_ids)

    # add table map file for each table
    table.addTableMap(TABLE_MAP_FILE)

    # Read from table map the tomogram file and append to output list
    tomogram_files.append(table.table_map[int(table.unique_ids)])

    # Read eulers into table object
    table.eulers()

    # Change reference frame of eulers to convert dynamo (ZXZ ref -> particle) to emClarity (ZXZ particle -> ref)
    table.eulers.change_reference_frame()

    # Output euler angles for emClarity
    euler_angles_emClarity.append(table.eulers.euler_angles)

    # Output rotation matrices for emClarity
    rotation_matrices_emClarity.append(table.eulers.rotation_matrices)

    # Output XYZ (binned) for all particles in table
    xyz_binned.append(table.xyz())

    # output bounding boxes for all tables
    bounding_boxes.append(utils.calculateBoundingBox(table))

    # Output particle tags for all particles in table
    particle_tags.append(table.tags())


# Get basename from tomogram file name
def get_basenames(list_tomogram_files):
    # get basename of each tomo
    basenames = [os.path.basename(tomogram_file) for tomogram_file in list_tomogram_files]

    # remove extension in basenames
    basenames = [os.path.splitext(basename)[0] for basename in basenames]

    return basenames


basenames = get_basenames(tomogram_files)


# calculate subarea numbers from list of table idx
def calculate_subarea_numbers(list_table_idx):
    nTables = len(list_table_idx)
    indices = range(0, nTables)
    subarea_numbers = []
    subarea_number = 1
    for idx in indices:
        current_table_idx = list_table_idx[idx]
        subarea_numbers.append(subarea_number)

        if idx == indices[-1]:
            subarea_number += 1
        elif current_table_idx == list_table_idx[idx + 1]:
            subarea_number += 1
        else:
            subarea_number = 1

    return subarea_numbers


subarea_numbers = calculate_subarea_numbers(table_idx)

# calculate enlarged bounding boxes for each bounding box
enlarged_bounding_boxes = []

for bounding_box in bounding_boxes:
    bounding_box_enlarged = utils.enlargeBoundingBox(bounding_box, SIDELENGTH_PARTICLE, 1.5)
    bounding_box_enlarged = bounding_box_enlarged.astype(int)
    enlarged_bounding_boxes.append(bounding_box_enlarged)



# Calculate xyz coordinates of each tomogram file
xyz_tomo_binned = [utils.mrc_header_xyz(tomogram_file) for tomogram_file in tomogram_files]

# Calculate subarea geometries for each bounding box
subarea_geometries = []
for idx in indices:
    current_bounding_box = enlarged_bounding_boxes[idx]
    current_xyz = xyz_binned[idx]
    current_xyz_tomo = xyz_tomo_binned[idx]
    current_subarea_geom = utils.calculate_subarea_geometry(current_bounding_box, current_xyz_tomo, BINNING_FACTOR_TABLE)
    subarea_geometries.append(current_subarea_geom)

# calculate xyz position relative to enlarged bounding box
xyz_in_subareas = []

for idx in indices:
    current_bounding_box = enlarged_bounding_boxes[idx]
    current_xyz = xyz_binned[idx]
    # calculate xyz in subarea
    xyz_out = current_xyz
    xyz_out = xyz_out - current_bounding_box[0, :]
    xyz_in_subareas.append(xyz_out)
# Write out emClarity csv files

for idx in indices:
    utils.emClarity_csv_write(OUT_DIR + 'convmap/',
                              basenames[idx],
                              subarea_numbers[idx],
                              BINNING_FACTOR_TABLE,
                              particle_tags[idx],
                              xyz_in_subareas[idx],
                              euler_angles_emClarity[idx],
                              rotation_matrices_emClarity[idx])


# Write out emClarity recon.coords files
last_basename = 0

for idx in indices:
    current_basename = basenames[idx]
    current_subarea_geom = subarea_geometries[idx]
    filename = '{}{}_recon.coords'.format(OUT_DIR + 'recon/', current_basename)
    if last_basename != current_basename:
        nsubregions = table_idx.count(table_idx[idx])
        with open(filename, 'w') as recon_coords:
            recon_coords.write(current_basename + '\n')
            recon_coords.write(str(nsubregions) + '\n')
            recon_coords.write(str(current_subarea_geom['NX']) + '\n')
            recon_coords.write(str(current_subarea_geom['SLICE1']) + '\n')
            recon_coords.write(str(current_subarea_geom['SLICE2']) + '\n')
            recon_coords.write(str(current_subarea_geom['THICKNESS']) + '\n')
            recon_coords.write(str(current_subarea_geom['SHIFT1']) + '\n')
            recon_coords.write(str(current_subarea_geom['SHIFT2']) + '\n')
        last_basename = current_basename
    else:
        with open(filename, 'a') as recon_coords:
            recon_coords.write(str(current_subarea_geom['NX']) + '\n')
            recon_coords.write(str(current_subarea_geom['SLICE1']) + '\n')
            recon_coords.write(str(current_subarea_geom['SLICE2']) + '\n')
            recon_coords.write(str(current_subarea_geom['THICKNESS']) + '\n')
            recon_coords.write(str(current_subarea_geom['SHIFT1']) + '\n')
            recon_coords.write(str(current_subarea_geom['SHIFT2']) + '\n')
        last_basename = current_basename

# Write scripts for reconstructing subareas
# Get list of recon_coords files
recon_coords_files = []
for file in os.listdir(OUT_DIR + 'recon/'):
    if file.endswith('_recon.coords'):
        recon_coords_files.append(os.path.join((OUT_DIR + 'recon/'), file))

# generate scripts for each recon_coords file
for recon_coords_file in recon_coords_files:
    utils.reconstruct_subareas_scripts(recon_coords_file, binning=BINNING_FACTOR_TABLE, output_dir=(OUT_DIR + 'recon/'))


# write out .txt files containing xyz coordinates of each particle in binned subarea for easy mod file generation
for idx in indices:
    current_basename = basenames[idx]
    current_subarea = subarea_numbers[idx]
    current_xyz = xyz_in_subareas[idx]

    filename = '{}{}_{}_bin{}.txt'.format(OUT_DIR + 'convmap/', current_basename, current_subarea, BINNING_FACTOR_TABLE)
    np.savetxt(filename, current_xyz, '%f', delimiter=' ')

    # try to write model file from txt file
    # point2model
    point2model = IMOD_BIN_DIR + 'point2model'
    args = '-circle 3 -sphere 2 -scat -thick 2 -color 80,191,255'
    if os.path.isfile(point2model):
        os.system(point2model + ' ' + args + ' ' + filename + ' ' + filename.replace('.txt', '.mod'))


print(
    """
        |-----------|    |-----------|
        |  DYNAMO   |    |   THANKS  |
        |    2      |    |    FOR    |
        | EMCLARITY |    |  STOPPING |
        |   DONE!   |    |    BY     |
        |-----------|    |-----------|
        (\__/) ||            || (\__/)
        (•ㅅ•) ||             || (•ㅅ•)
        / 　 づ             　 || |\ /| 
        
        """)

