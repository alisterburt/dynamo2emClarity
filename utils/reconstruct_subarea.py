import os

def recon_coord_read(recon_coords_file):
    with open(recon_coords_file) as file:
        lines = file.readlines()
    basename = lines[0].strip('\n')
    n_subareas = int(lines[1])

    # extract all parameters for each subarea
    NX = [int(line.strip('\n')) for line in lines[2::6]]
    NY1 = [int(line.strip('\n')) for line in lines[3::6]]
    NY2 = [int(line.strip('\n')) for line in lines[4::6]]
    THICKNESS = [int(line.strip('\n')) for line in lines[5::6]]
    SHIFT1 = [int(line.strip('\n')) for line in lines[6::6]]
    SHIFT2 = [int(line.strip('\n')) for line in lines[7::6]]

    # aggregate params
    subarea_parameters = {
        'basename': basename,
        'n_subareas': n_subareas,
        'NX': NX,
        'NY1': NY1,
        'NY2': NY2,
        'THICKNESS': THICKNESS,
        'SHIFT1': SHIFT1,
        'SHIFT2': SHIFT2,
    }

    return subarea_parameters

def reconstruct_subareas_scripts(recon_coords_file,
                                 aligned_stack_file='ALIGNED_STACK_FILE',
                                 tilt_angles_file='TILT_ANGLES_FILE',
                                 binning=1,
                                 output_dir=''
                                 ):
    # Sanity check on output dir
    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'

    # Read subarea geometry
    subarea_geometries = recon_coord_read(recon_coords_file)

    # config tilt command
    output_file = output_dir + subarea_geometries['basename'] + '_{}' +'.rec'
    tilt_command = 'tilt -input {} -TILTFILE {} -output {} -RADIAL 0.475,0.05 -UseGPU 0 -WIDTH {} -SLICE {},{} -THICKNESS {} -RotateBy90 -SHIFT {},{}'

    # get indices for accessing parameters
    indices = range(subarea_geometries['n_subareas'])

    # format tilt commands
    tilt_commands = [tilt_command.format(aligned_stack_file,
                                         tilt_angles_file,
                                         output_file.format((idx+1)),
                                         subarea_geometries['NX'][idx],
                                         subarea_geometries['NY1'][idx],
                                         subarea_geometries['NY2'][idx],
                                         subarea_geometries['THICKNESS'][idx],
                                         subarea_geometries['SHIFT1'][idx],
                                         subarea_geometries['SHIFT2'][idx],
                                        ) for idx in indices]

    # format binvol commands
    binvol_command = 'binvol -binning {} -input {} -output {}'
    binvol_commands = [binvol_command.format(binning,
                                             output_file.format((idx + 1)),
                                             output_file.format((idx + 1)).replace('.rec','_bin{}.rec'.format(binning))
                                             ) for idx in indices]

    # format removal of unbinned reconstructions
    removal_command = 'rm -vf {}'
    removal_commands = [removal_command.format(output_file.format((idx + 1))) for idx in indices]
    
    # format script
    output_script = output_dir + subarea_geometries['basename'] + '_recon.sh'
    with open(output_script,'w') as script:
        script.write('#!/bin/bash\n')
        script.write('# Script for the reconstruction and binning of emclarity subareas\n\n')
        for tilt, binvol, remove in zip(tilt_commands, binvol_commands, removal_commands):
            script.write(tilt + '\n')
            script.write(binvol + '\n')
            script.write(remove + '\n')
            script.write('\n')

