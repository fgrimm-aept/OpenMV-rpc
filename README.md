Function Call_me in PC.py:
    Exposure: set exposure time in microseconds (Range: 1 - 600 000)
            If values above 600 000 -> camera times out and no picture 
            is returned
    Gain: set gain in dB (Range: 1 - 32)
    Resolution: set sensor resolution (use only the name of the resolution, 
            without the "sensor." prefix)
    change_values: If set to "True", calls the function on the camera which
            allows to change the exposure and gain values.
            If set to False, call the function on the camera which takes 
            a picture with the currently set values.
    cutthrough: When cutthrough is False the image will be transferred through the RPC library with CRC and
            retry protection on all data moved. For faster data transfer set cutthrough to True so that
            get_bytes() and put_bytes() are called after an RPC call completes to transfer data
            more quickly from one image buffer to another. Note: This works because once an RPC call
            completes successfully both the master and slave devices are synchronized completely.
    show: Should only be used when the python script is run directly through a console.
            If set to True, displays the camera picture through the Python Image Library
            using the default image viewer for png files
