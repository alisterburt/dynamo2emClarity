import os

def mrc_header_xyz(mrc_file):
    if type(mrc_file) == str and os.path.isfile(mrc_file):
        with open(mrc_file, 'rb+') as f:
            # Read NX, NY and NZ positions from mrc file header
            f.seek(0,0)
            NX = f.read(4)
            f.seek(4,0)
            NY = f.read(4)
            f.seek(8,0)
            NZ = f.read(4)
            
            # Convert to integers
            NX = int.from_bytes(NX, byteorder='little')
            NY = int.from_bytes(NY, byteorder='little')
            NZ = int.from_bytes(NZ, byteorder='little')
            
            # Output
            xyz = [NX, NY, NZ]
            return xyz
    else:
        print("Error reading mrc file '{}'".format(mrc_file))
        