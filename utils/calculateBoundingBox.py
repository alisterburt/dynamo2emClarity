import numpy as np
from . import DynamoTable
def calculateBoundingBox(table):
    "Calculates the minimum bounding box which contains all particle centers in a dynamo table. Output is a [2,3] numpy array containing xyz min and xyz max on the first and second row respectively"
    type_input = type(table)
    if type_input == str and os.path.isfile(table):
        table = utils.dynamoTable(table)

    if type(table) != DynamoTable:
        sys.exit('Item not of type "dynamoTable", desisting...')
    
    xyz = table.xyz()
    xyz_min = np.amin(xyz, axis=0)
    xyz_max = np.amax(xyz, axis=0)
    
    xyz_min_max = np.vstack((xyz_min, xyz_max))

    return xyz_min_max