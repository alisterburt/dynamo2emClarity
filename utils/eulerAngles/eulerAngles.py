import os
import numpy as np

# importing conversion functions
from . import ZXZeuler2matrix
from . import matrix2ZXZeuler

class eulerAngles:
    "Euler angles"
    def __init__(self, data=[], convention='not_defined', reference_frame='not_defined'):
        # numpy array [N,3]
        self.euler_angles = data
        
        # Euler angle convention triplet e.g. 'ZXZ', 'ZYZ'
        self.convention = convention
        
        # Euler angle reference frame, either 'particle' or 'template'
        # This defines whether the euler angles define rotations of particles onto templates (particle)
        # or templates onto particles (template)
        self.reference_frame = reference_frame

        
    def calculate_rotation_matrices(self):
        "Write out an [N,3,3] numpy arrays containing a 3x3 rotation matrix for each of N particles"
        nParticles = self.euler_angles.shape[0]
        rotation_matrices = np.empty([nParticles, 3, 3])
        
        # ZXZ Convention
        if self.convention == 'ZXZ':
            counter = 0
            for triplet in self.euler_angles:
                rotation_matrix = ZXZeuler2matrix(triplet) 
                rotation_matrices[counter,:,:] = rotation_matrix
                counter += 1
            
            self.rotation_matrices = rotation_matrices
            return self.rotation_matrices
        
        else:
            print("Rotation matrix calculation not yet implemented for euler angles in {} convention".format(self.convention))
            
    
    
    def calculate_euler_angles(self):
        "Calculate euler angles from rotation matrices"
        nParticles = self.rotation_matrices.shape[0]
        euler_angles = np.zeros([nParticles, 3])
        
        # ZXZ convention
        if self.convention == 'ZXZ':
            
            counter = 0
            for rotation_matrix in self.rotation_matrices:
                euler_angles[counter,0:3] = matrix2ZXZeuler(rotation_matrix)
                counter += 1
            
            self.euler_angles = euler_angles
            return self.euler_angles    
                              
    
    def change_reference_frame(self):
        "Changes reference frame for euler angles from particle to template or vice-versa, recalculating the euler angles"
        
        # ZXZ convention
        if self.convention == 'ZXZ':
                
            # Calulate rotation matrices
            self.calculate_rotation_matrices()
            
            # Transpose rotation matrices (changes reference frame)
            counter = 0
            for rotation_matrix in self.rotation_matrices:
                self.rotation_matrices[counter,:,:] = np.transpose(rotation_matrix)
                counter += 1
            
            # Recalculate euler angles from transposed rotation matrices
            self.calculate_euler_angles()
            
            # Update reference frame
            
            if self.reference_frame == 'particle':
                print("Reference frame changed from 'particle' to 'template'")
                self.reference_frame = 'template'
            elif self.reference_frame == 'template':
                self.reference_frame = 'particle'
                print("Reference frame changed from 'template' to 'particle'")
                
            