import numpy as np

def nextpow2(i):
    """
    Find next power of 2 after i:

    1023 => 1024
    """
    l = np.log2(i)
    l = np.ceil(l)
    return 2**l
