import sys

import numpy as np


# Gibt das numpy array als return value zurück
def return_array():
    arr = np.load('Test.npy')
    return arr


# Darstellung für print statements von numpy arrays (ändert nichts am Array selber)
np.set_printoptions(threshold=sys.maxsize, edgeitems=sys.maxsize)

# Lade das von der Kamera gespeicherte Numpy array


print(arr)
# func call
return_array(arr)
