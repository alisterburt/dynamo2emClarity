import os
import numpy as np
from utils.DynamoTable import DynamoTable

from utils.calculateBoundingBox import calculateBoundingBox
from utils.enlargeBoundingBox import enlargeBoundingBox


def checkBoundingBox(table, particle_sidelength_current_binning=0, current_binning=1):
    "Checks if bounding box of particles in table, enlarged to contain all particles, will fit safely in GPU memory"
    type_input = type(table)
    if type_input == str and os.path.isfile(table):
        table = utils.dynamoTable(table)
    if type(table) != DynamoTable:
        print("'{}' not of type 'dynamoTable, desisting...")

    bounding_box = calculateBoundingBox(table)

    bounding_box = enlargeBoundingBox(bounding_box, particle_sidelength_current_binning, 1.5)

    bounding_box_binned_size = np.ptp(bounding_box, 0)
    bounding_box_unbinned_size = bounding_box_binned_size * current_binning

    nVoxels = np.prod(bounding_box_unbinned_size, 0)

    # Assuming map mode 2
    nBits = nVoxels * 32
    size_GB = nBits * 1.25e-10
    return size_GB <= 8
