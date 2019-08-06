import numpy as np


def enlargeBoundingBox(bounding_box, particle_sidelength_current_binning, padding_factor=1):
    """function to enlarge bounding box as a function of
       current particle sidelength and padding factor
       padding factor is a number of particle sidelengths to add and subtract in each dimension
    """

    bounding_box[0, :] = bounding_box[0, :] - (padding_factor * particle_sidelength_current_binning)
    bounding_box[1, :] = bounding_box[1, :] + (padding_factor * particle_sidelength_current_binning)

    return bounding_box


