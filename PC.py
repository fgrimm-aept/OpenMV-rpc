# Image Transfer - As The Controller Device
#
# This script is meant to talk to the "image_transfer_jpg_as_the_remote_device_for_your_computer.py" on the OpenMV Cam.
#
# This script shows off how to transfer the frame buffer to your computer as a jpeg image.

# import io

import numpy as np
# import pygame
import rpc
import struct
import sys

# The RPC library above is installed on your OpenMV Cam and provides multiple classes for
# allowing your OpenMV Cam to control over USB or WIFI.

##############################################################
# Choose the interface you wish to control an OpenMV Cam over.
##############################################################

# Uncomment the below lines to setup your OpenMV Cam for controlling over a USB VCP.
#
# * port - Serial Port Name.
#
interface = rpc.rpc_usb_vcp_master(port="COM4")
sys.stdout.flush()


# Uncomment the below line to setup your OpenMV Cam for controlling over WiFi.
#
# * slave_ip - IP address to connect to.
# * my_ip - IP address to bind to ("" to bind to all interfaces...)
# * port - Port to route traffic to.
#
# interface = rpc.rpc_network_master(slave_ip="xxx.xxx.xxx.xxx", my_ip="", port=0x1DBA)

##############################################################
# Call Back Handlers
##############################################################

def get_frame_buffer_call_back(pixformat_str, framesize_str, exposure, cutthrough, silent):
    if not silent:
        print("Getting Remote Frame...")

    result = interface.call("jpeg_image_snapshot", "%s,%s,%s" % (pixformat_str, framesize_str, exposure))
    if result is not None:

        size = struct.unpack("<I", result)[0]
        image = bytearray(size)

        if cutthrough:
            # Fast cutthrough data transfer with no error checking.

            # Before starting the cut through data transfer we need to sync both the master and the
            # slave device. On return both devices are in sync.
            result = interface.call("jpeg_image_read")
            if result is not None:
                # GET BYTES NEEDS TO EXECUTE NEXT IMMEDIATELY WITH LITTLE DELAY NEXT.

                # Read all the image data in one very large transfer.
                interface.get_bytes(image, 5000)  # timeout

        else:
            # Slower data transfer with error checking.

            # Transfer 32 KB chunks.
            chunk_size = (1 << 15)

            if not silent:
                print("Reading %d bytes..." % size)
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

        return image

    else:
        if not silent:
            print("Failed to get Remote Frame!")

    return None


#
# pygame.init()
# screen_w = 640
# screen_h = 480
# try:
#     screen = pygame.display.set_mode((screen_w, screen_h), flags=pygame.RESIZABLE)
# except TypeError:
#     screen = pygame.display.set_mode((screen_w, screen_h))
# pygame.display.set_caption("Frame Buffer")
# clock = pygame.time.Clock()


def call_me(exposure):
    arr = None
    img = None
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
        img = get_frame_buffer_call_back("sensor.GRAYSCALE", "sensor.QVGA", f"{exposure}", cutthrough=False,
                                         silent=False)  # 168740
        if img is not None:
            arr = np.array(list(img))
            print(arr)
            np.savetxt("Test.txt", arr, fmt="%.0d")
            # print(img[-6], img[-5], img[-4], img[-3], img[-2], img[-1])
            # arr = np.frombuffer(img, dtype='uint16')
            # print(arr)
            # np.savetxt("Test.txt", arr, fmt='%.0d')

        #     try:
        #         screen.blit(pygame.transform.scale(pygame.image.load(io.BytesIO(img), "jpg"),
        #                                            (screen_w, screen_h)), (0, 0))
        #         pygame.display.update()
        #         clock.tick()
        #     except pygame.error:
        #         pass
        #
        # print(clock.get_fps())
        #
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         quit()
    return arr


call_me(168740)
