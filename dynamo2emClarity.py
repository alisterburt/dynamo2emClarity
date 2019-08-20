import os
import numpy as np
import utils

#####################
####### SETUP #######
#####################

### Set table file
table_file = '/ibshome/aburt/dynamo2emClarity/box7_tomo_011_MC/temp_crop.tbl'

### Set dynamo format tomogram table map file (as per https://wiki.dynamo.biozentrum.unibas.ch/w/index.php/Tomogram-table_map_file) ###
table_map_file = '/ibshome/aburt/dynamo2emClarity/box7_tomo_011_MC/table_map.doc'

### Set output directory for CSV and recon_coords files
output_dir = '/ibshome/aburt/dynamo2emClarity/box7_tomo_011_MC/test_output'

### Set IMOD bin directory
IMOD_dir = '/usr/local/IMOD/bin/'

### Set current binning factor of coordinates in dynamo table file
binning_factor = 8

### Set particle sidelength at current binning
particle_sidelength = 32

#####################
###### Running ######
#####################
# Sanity checks on output directory
if not output_dir.endswith('/'):
    output_dir = output_dir + '/'

# Sanity checks on IMOD dir
if not IMOD_dir.endswith('/'):
    IMOD_dir = IMOD_dir + '/'

# make output,recon and convmap directory
os.makedirs('{}'.format(output_dir), exist_ok=True)
os.makedirs('{}recon'.format(output_dir), exist_ok=True)
os.makedirs('{}convmap'.format(output_dir), exist_ok=True)

# Load table file
table = utils.DynamoTable(table_file=table_file)

# Separate table into list of tables, one item per unique tomogram
list_of_tables = table.unique()

# Get number of tomograms
nTomos = len(list_of_tables)


def geometry_check(table_list):
    """Checks bounding boxes for a list of tables"""
    BB_pass = [utils.checkBoundingBox(table, particle_sidelength, binning_factor) for table in table_list]

    # check if any tables in list failed the check
    BB_pass = np.all(BB_pass)
    return BB_pass


# test = geometry_check(list_of_subtables)
# if table list doesn't pass geometry check, split tables RECURSIVE
def checkAndSplit(local_table):
    if utils.checkBoundingBox(local_table, 32, binning_factor):
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
    table.addTableMap(table_map_file)

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
    bounding_box_enlarged = utils.enlargeBoundingBox(bounding_box, particle_sidelength, 1.5)
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
    current_subarea_geom = utils.calculate_subarea_geometry(current_bounding_box, current_xyz_tomo, binning_factor)
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
    utils.emClarity_csv_write(output_dir + 'convmap/',
                              basenames[idx],
                              subarea_numbers[idx],
                              binning_factor,
                              particle_tags[idx],
                              xyz_in_subareas[idx],
                              euler_angles_emClarity[idx],
                              rotation_matrices_emClarity[idx])


# Write out emClarity recon.coords files
last_basename = 0

for idx in indices:
    current_basename = basenames[idx]
    current_subarea_geom = subarea_geometries[idx]
    filename = '{}{}_recon.coords'.format(output_dir + 'recon/', current_basename)
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
for file in os.listdir(output_dir+'recon/'):
    if file.endswith('_recon.coords'):
        recon_coords_files.append(os.path.join((output_dir+'recon/'),file))

# generate scripts for each recon_coords file
for recon_coords_file in recon_coords_files:
    utils.reconstruct_subareas_scripts(recon_coords_file, binning=binning_factor, output_dir=(output_dir + 'recon/'))


# write out .txt files containing xyz coordinates of each particle in binned subarea for easy mod file generation
for idx in indices:
    current_basename = basenames[idx]
    current_subarea = subarea_numbers[idx]
    current_xyz = xyz_in_subareas[idx]

    filename = '{}{}_{}_bin{}.txt'.format(output_dir + 'convmap/', current_basename, current_subarea, binning_factor)
    np.savetxt(filename, current_xyz, '%f', delimiter=' ')

    # try to write model file from txt file
    # point2model
    point2model = IMOD_dir + 'point2model'
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

