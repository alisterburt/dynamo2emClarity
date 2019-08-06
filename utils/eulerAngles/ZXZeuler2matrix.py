import numpy as np

def ZXZeuler2matrix(ZXZ):
    "Function to convert ZXZ euler triplet ([1,3] numpy array) into a [3,3] rotation matrix defining the same rotation ||| taken from dynamo function dynamo_euler2matrix"
    # meuler=deuler2matrix(tdrot, tilt, narot);
    tdrot = ZXZ[0]
    tilt = ZXZ[1]
    narot = ZXZ[2]
        
    tdrot  = tdrot*np.pi/180;
    narot  = narot*np.pi/180;
    tilt   = tilt*np.pi/180;

    costdrot = np.cos(tdrot);
    cosnarot = np.cos(narot);
    costilt  = np.cos(tilt);
    sintdrot = np.sin(tdrot);
    sinnarot = np.sin(narot);
    sintilt  = np.sin(tilt);

    m11 = costdrot*cosnarot - sintdrot*costilt*sinnarot;
    m12 = - cosnarot*sintdrot - costdrot*costilt*sinnarot;
    m13 = sinnarot*sintilt;
    m21 = costdrot*sinnarot + cosnarot*sintdrot*costilt;
    m22 = costdrot*cosnarot*costilt - sintdrot*sinnarot;
    m23 = -cosnarot*sintilt;
    m31 = sintdrot*sintilt;
    m32 = costdrot*sintilt;
    m33 = costilt;
        
    rotation_matrix = np.array([[m11, m12, m13],[m21, m22, m23],[m31, m32, m33]])
    return rotation_matrix

