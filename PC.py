# Image Transfer - As The Controller Device
#
# This script is meant to talk to the "image_transfer_jpg_as_the_remote_device_for_your_computer.py" on the OpenMV Cam.
#
# This script shows off how to transfer the frame buffer to your computer as a jpeg image.

# import io

import struct
import sys
import time

import numpy as np
from PIL import Image

import rpc

interface = rpc.rpc_usb_vcp_master(port="COM4")
sys.stdout.flush()


def get_frame_buffer_call_back(pixformat_str: str = 'sensor.GRAYSCALE', framesize_str: str = 'sensor.FHD',
                               exposure: str = "200_000", gain: str = "3", cutthrough: bool = False,
                               silent: bool = False, change_values: bool = False):
    if not silent:
        print("Getting Remote Frame...")
    if change_values:
        result = interface.call("jpeg_image_change_val", "%s,%s,%s,%s" % (pixformat_str, framesize_str, exposure, gain))
    else:
        result = interface.call("jpeg_image_snapshot", "%s,%s" % (pixformat_str, framesize_str))
    if result is not None:

        size = struct.unpack("<I", result)[0]
        image = bytearray(size)

        if cutthrough:
            t0 = time.time()
            # Fast cutthrough data transfer with no error checking.

            # Before starting the cut through data transfer we need to sync both the master and the
            # slave device. On return both devices are in sync.
            result = interface.call("jpeg_image_read")
            if result is not None:
                # GET BYTES NEEDS TO EXECUTE NEXT IMMEDIATELY WITH LITTLE DELAY NEXT.

                # Read all the image data in one very large transfer.
                interface.get_bytes(image, 5000)  # timeout
            t1 = time.time()
        else:
            # Slower data transfer with error checking.

            # Transfer 32 KB chunks.
            chunk_size = (1 << 15)

            if not silent:
                print("Reading %d bytes..." % size)
            t0 = time.time()
            for i in range(0, size, chunk_size):
                ok = False
                for j in range(3):  # Try up to 3 times.
                    result = interface.call("jpeg_image_read", struct.pack("<II", i, chunk_size))
                    if result is not None:
                        image[i:i + chunk_size] = result  # Write the image data.
                        if not silent:
                            print("%.2f%%" % ((i * 100) / size))
                        ok = True
                        break
                    if not silent:
                        print("Retrying... %d/2" % (j + 1))
                if not ok:
                    if not silent:
                        print("Error!")
                    return None
            t1 = time.time()
        print(t1 - t0)
        return image

    else:
        if not silent:
            print("Failed to get Remote Frame!")

    return None


def call_me(exposure: int = 200_000, gain: int = 3, resolution: str = 'FHD', cutthrough: bool = True,
            change_values: bool = False, show=False):
    arr = None
    img = None

    exposure = sorted([1, exposure, 600_000])[1]
    gain = sorted([1, gain, 32])[1]

    while img is None:

        sys.stdout.flush()

        # You may change the pixformat and the framesize of the image transfered from the remote device
        # by modifying the below arguments.
        #
        # When cutthrough is False the image will be transferred through the RPC library with CRC and
        # retry protection on all data moved. For faster data transfer set cutthrough to True so that
        # get_bytes() and put_bytes() are called after an RPC call completes to transfer data
        # more quickly from one image buffer to another. Note: This works because once an RPC call
        # completes successfully both the master and slave devices are synchronized completely.
        # 320x240
        img = get_frame_buffer_call_back("sensor.GRAYSCALE", f"sensor.{resolution}", f"{exposure}", f"{gain}",
                                         cutthrough=cutthrough, silent=False, change_values=change_values)

        resolution_dict = {"QQCIF": (88, 72),
                           "QCIF": (176, 144),
                           "CIF": (352, 288),
                           "QQSIF": (88, 60),
                           "QSIF": (176, 120),
                           "SIF": (352, 240),
                           "QQQQVGA": (40, 30),
                           "QQQVGA": (80, 60),
                           "QQVGA": (160, 120),
                           "QVGA": (320, 240),
                           "VGA": (640, 480),
                           "HQQQQVGA": (30, 20),
                           "HQQQVGA": (60, 40),
                           "HQQVGA": (120, 80),
                           "HQVGA": (240, 160),
                           "HVGA": (480, 320),
                           "SVGA": (800, 600),
                           "XGA": (1024, 768),
                           "SXGA": (1280, 1024),
                           "UXGA": (1600, 1200),
                           "HD": (1280, 720),
                           "FHD": (1920, 1080),
                           "QHD": (2560, 1440),
                           "QXGA": (2048, 1536),
                           "WQXGA": (2560, 1600),
                           "WQXGA2": (2592, 1944)}

        if img is not None:
            arr = np.array(list(img))
            if show:
                img = bytes(img)
                height, width = resolution_dict[resolution]
                pic = Image.frombytes(data=img, mode='L', size=(height, width))
                pic.show()

    return arr


call_me(exposure=600000, gain=10, resolution="FHD", change_values=False, cutthrough=True)
