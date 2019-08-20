import numpy as np

def calculate_subarea_geometry(subarea_bounding_box, NXYZ_binned_tomo, binning_factor):
    "Function to calculate unbinned tomographic subarea reconstruction geometry based on bounding_box, NXYZ and binning factor of a binned tomogram"
    # This function assumes that your binned tomograms have not been trimmed (i.e. X and Y extent in tomogram is related to X and Y extent in tilt-series by binning_factor)
    
    # Explicitly define variables
    subarea_bounding_box_unbinned = subarea_bounding_box * binning_factor
    subarea_xmin_unbinned = subarea_bounding_box_unbinned[0,0]
    subarea_xmax_unbinned = subarea_bounding_box_unbinned[1,0]
    subarea_ymin_unbinned = subarea_bounding_box_unbinned[0,1]
    subarea_ymax_unbinned = subarea_bounding_box_unbinned[1,1]
    subarea_zmin_unbinned = subarea_bounding_box_unbinned[0,2]
    subarea_zmax_unbinned = subarea_bounding_box_unbinned[1,2]
    
    NX_orig = NXYZ_binned_tomo[0]
    NY_orig = NXYZ_binned_tomo[1]
    NZ_orig = NXYZ_binned_tomo[2]
       
    # Calculate necessary parameters for IMOD program tilt to reconstruct subarea
    # width of area to reconstruct (X, unbinned, microscope reference frame)
    t1_NX = int(subarea_xmax_unbinned - subarea_xmin_unbinned)
    
    # which slice to start reconstruction with? SLICE float 1 for tilt
    # (tomo is reconstructed one XZ plane at a time to save memory)
    t1_NY1 = int(subarea_ymin_unbinned)
    
    # which slice to end reconstruction with SLICE float 2 for tilt
    # (tomo is reconstructed one XZ plane at a time to save memory)
    t1_NY2 = int(subarea_ymax_unbinned)
    
    # how thick should the reconstruction be in Z? THICKNESS for tilt
    t1_NZ = int(subarea_zmax_unbinned - subarea_zmin_unbinned)

    # Calculate position of shift in X of unbinned version of tomogram in which subareas were defined
    shift_x = int(((NX_orig * binning_factor) / 2.0)-(subarea_xmin_unbinned + (t1_NX / 2.0)))

    # Calcuate the position of shift in Z-center of unbinned version of tomogram in which subareas were defined
    shift_z = (-1 * int(((NZ_orig / 2.0) * binning_factor) - (subarea_zmin_unbinned + (t1_NZ / 2.0))))
    
    # Calculate the origin in Z of unbinned version of tomogram of the subarea to be reconstructed
    origin_z = ((NZ_orig / 2.0) * binning_factor) - (-1.0 * shift_z) - (t1_NZ / 2.0)

    # Calculate origin in X of reconstructed subarea
    origin_x = ((NX_orig * binning_factor) / 2.0) - shift_x - (t1_NX / 2.0)

    return {'NX': t1_NX,
            'SLICE1': t1_NY1,
            'SLICE2': t1_NY2,
            'THICKNESS': t1_NZ,
            'SHIFT1': shift_x,
            'SHIFT2': shift_z,
            'ORIGIN_X': origin_x,
            'ORIGIN_Y': subarea_ymin_unbinned,
            'ORIGIN_Z': origin_z
           }


                   