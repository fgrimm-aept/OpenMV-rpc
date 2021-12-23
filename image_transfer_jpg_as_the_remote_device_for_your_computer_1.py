import omv
import rpc
import sensor
import struct

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.FHD)
sensor.skip_frames(time=2000)
omv.disable_fb(True)
interface = rpc.rpc_usb_vcp_slave()


def jpeg_image_snapshot(data):
    pixformat, framesize = bytes(data).decode().split(",")
    sensor.set_pixformat(eval(pixformat))
    sensor.set_framesize(eval(framesize))
    img = sensor.snapshot()
    return struct.pack("<I", img.size())


def jpeg_image_read_cb():
    interface.put_bytes(sensor.get_fb().bytearray(), 5000)


def jpeg_image_read(data):
    if not len(data):
        interface.schedule_callback(jpeg_image_read_cb)
        return bytes()
    else:
        offset, size = struct.unpack("<II", data)
        return memoryview(sensor.get_fb().bytearray())[offset:offset + size]


interface.register_callback(jpeg_image_snapshot)
interface.register_callback(jpeg_image_read)
interface.loop()
