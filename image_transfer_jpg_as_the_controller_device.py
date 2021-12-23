import io
import pygame
import rpc
import struct
import sys

interface = rpc.rpc_usb_vcp_master(port='COM4')


# TODO: auto_gain and exposure manually
# TODO: return GRAYSCALE values as numpy array or list
# TODO: 1920 x 1080

def get_frame_buffer_call_back(pixformat_str: str, framesize_str: str, cutthrough: bool, silent: bool):
    """
    :param pixformat_str: Sets the pixel format for the camera module.
        sensor.GRAYSCALE: 8-bits per pixel.
        sensor.RGB565: 16-bits per pixel.
        sensor.BAYER: 8-bits per pixel bayer pattern.
        sensor.JPEG: Compressed JPEG data. Only for the OV2640/OV5640.
    :param framesize_str: Sets the frame size for the camera module.
        https://docs.openmv.io/library/omv.sensor.html#sensor.sensor.set_framesize
    :param cutthrough: When cutthrough is False the image will be transferred through the RPC library with CRC and
        retry protection on all data moved. For faster data transfer set cutthrough to True so that
        get_bytes() and put_bytes() are called after an RPC call completes to transfer data
        more quickly from one image buffer to another. Note: This works because once an RPC call
        completes successfully both the master and slave devices are synchronized completely.
    :param silent: if True, prints log messages to stdout
    :return: image
    """
    result = interface.call("jpeg_image_snapshot", "%s,%s" % (pixformat_str, framesize_str))
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
                print(f"Reading {size} bytes...")
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


pygame.init()
screen_w = 640
screen_h = 480
try:
    screen = pygame.display.set_mode((screen_w, screen_h), flags=pygame.RESIZABLE)
except TypeError:
    screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption("Frame Buffer")
clock = pygame.time.Clock()
counter = 0

while True:
    sys.stdout.flush()
    counter += 1
    # You may change the pixformat and the framesize of the image transfered from the remote device
    # by modifying the below arguments.
    #
    # When cutthrough is False the image will be transferred through the RPC library with CRC and
    # retry protection on all data moved. For faster data transfer set cutthrough to True so that
    # get_bytes() and put_bytes() are called after an RPC call completes to transfer data
    # more quickly from one image buffer to another. Note: This works because once an RPC call
    # completes successfully both the master and slave devices are synchronized completely.
    #

    # img = get_frame_buffer_call_back("sensor.GRAYSCALE", "sensor.HVGA", cutthrough=False, silent=False)
    # img = get_frame_buffer_call_back("sensor.GRAYSCALE", "sensor.HVGA", cutthrough=False, silent=False)
    img = get_frame_buffer_call_back("sensor.GRAYSCALE", "sensor.FHD", cutthrough=False, silent=False)
    if img is not None:
        try:
            screen.blit(pygame.transform.scale(pygame.image.load(io.BytesIO(img), "jpg"), (screen_w, screen_h)), (0, 0))
            pygame.display.update()
            clock.tick()
        except pygame.error:
            pass

    print(clock.get_fps())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
