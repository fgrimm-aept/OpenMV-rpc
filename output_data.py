import sys

import numpy as np


# Gibt das numpy array als return value zurück
def return_array():
    arr = np.load('height1920_width1080_grayscale.npy')
    return arr


# Darstellung für print statements von numpy arrays (ändert nichts am Array selber)
np.set_printoptions(threshold=sys.maxsize, edgeitems=sys.maxsize)

# Lade das von der Kamera gespeicherte Numpy array
