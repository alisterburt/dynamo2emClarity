import numpy as np

def matrix2ZXZeuler(rotation_matrix):
    "Converts rotation matrix ([3,3] numpy array) into ZXZ euler angles ||| taken from dynamo function dynamo_matrix2euler"
    # Set a tolerance because of indetermination in defining narot and tdrot
    tolerance = 1e-4
        
    # Check special cases
    # rm(3,3) != -1
    if np.absolute(rotation_matrix[2,2]-1) < tolerance:
        tdrot = 0
        tilt = 0
        narot = np.arctan2(rotation_matrix[1,0],rotation_matrix[2,2])*180/np.pi
        
        ZXZeuler = np.array([tdrot, tilt, narot])
        return ZXZeuler

        
    # rm(3,3) != -1
    elif np.absolute(rotation_matrix[2,2]+1) < tolerance:
        tdrot = 0
        tilt = 180
        narot = np.arctan2(rotation_matrix[1,0],rotation_matrix[0,0])*180/np.pi
        
        ZXZeuler = np.array([tdrot, tilt, narot])
        return ZXZeuler

            
    # general case
    else:
        tdrot = np.arctan2(rotation_matrix[2,0],rotation_matrix[2,1])*180/np.pi
        tilt = np.arccos(rotation_matrix[2,2])*180/np.pi
        narot = np.arctan2(rotation_matrix[0,2],-rotation_matrix[1,2])*180/np.pi
        
        ZXZeuler = np.array([tdrot, tilt, narot])
        return ZXZeuler

    
    
    