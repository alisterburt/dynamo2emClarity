import os
import numpy as np


def emClarity_csv_write(output_dir, basename, subarea_number, current_binning, particle_tags, XYZ_binned, ZXZ_eulers,
                        rotation_matrices):
    """Write out emClarity format csv file"""

    nParticles = particle_tags.shape[0]

    # Initialise output
    csv = np.zeros([nParticles, 26])

    # Set CCC values to 1
    csv[:, 0] = np.ones([nParticles])

    # Set binning values to current binning (seem to be used only to relate model file to csv to check for kept particles)
    csv[:, 1] = np.ones([nParticles]) * current_binning

    # Set column 4 to tag from dynamo table
    csv[:, 3] = particle_tags

    # 5:9 = 1 (n/a 30/07/19)
    csv[:, 4:9] = np.ones([nParticles, 5])

    # Set columns 11:13 to unbinned XYZ coordinates
    csv[:, 10:13] = XYZ_binned * current_binning

    # set columns 14:16 to ZXZ euler angles (particle to reference)
    csv[:, 13:16] = ZXZ_eulers

    # set columns 17:25 to rotation matrices (done explicitly to make sure format is correct...)
    csv[:, 16] = rotation_matrices[:, 0, 0]
    csv[:, 17] = rotation_matrices[:, 1, 0]
    csv[:, 18] = rotation_matrices[:, 2, 0]
    csv[:, 19] = rotation_matrices[:, 0, 1]
    csv[:, 20] = rotation_matrices[:, 1, 1]
    csv[:, 21] = rotation_matrices[:, 2, 1]
    csv[:, 22] = rotation_matrices[:, 0, 2]
    csv[:, 23] = rotation_matrices[:, 1, 2]
    csv[:, 24] = rotation_matrices[:, 2, 2]

    # set column 26 (class idx) to 1
    csv[:, 25] = np.ones([nParticles])

    # Set file name and generate csv file
    filename = "{}{}_{}_bin{}.csv".format(output_dir, basename, subarea_number, current_binning)
    formatting = ['%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%d', '%f', '%f', '%f', '%f', '%f', '%f', '%f',
                  '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%d']
    np.savetxt(filename, csv, formatting, delimiter=' ')
