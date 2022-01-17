import omv
import rpc
import sensor
import struct

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.FHD)
sensor.set_auto_gain(False, gain_db=3)
sensor.set_auto_whitebal(False)
sensor.set_auto_exposure(False, exposure_us=168740)

# Source for __write_reg calls: https://github.com/openmv/openmv/issues/887
sensor.__write_reg(0x0E, 0b00000000)
sensor.__write_reg(0x3E, 0b00000000)
sensor.__write_reg(0x01, 0b01111100)
sensor.__write_reg(0x02, 0b01000000)
sensor.__write_reg(0x03, 0b01111100)
sensor.__write_reg(0x2D, 0b00000000)
sensor.__write_reg(0x2E, 0b00000000)
sensor.__write_reg(0x35, 0b10000000)
sensor.__write_reg(0x36, 0b10000000)
sensor.__write_reg(0x37, 0b10000000)
sensor.__write_reg(0x38, 0b10000000)
sensor.__write_reg(0x39, 0b10000000)
sensor.__write_reg(0x3A, 0b10000000)
sensor.__write_reg(0x3B, 0b10000000)
sensor.__write_reg(0x3C, 0b10000000)
sensor.skip_frames(time=2000)
omv.disable_fb(True)
interface = rpc.rpc_usb_vcp_slave()


def jpeg_image_change_val(data):
    pixformat, framesize, exposure, gain = bytes(data).decode().split(",")
    sensor.set_pixformat(eval(pixformat))
    sensor.set_framesize(eval(framesize))
    sensor.set_auto_gain(False, gain_db=eval(gain))
    sensor.set_auto_exposure(False, exposure_us=eval(exposure))
    sensor.skip_frames(time=1000)
    img = sensor.snapshot()
    return struct.pack("<I", img.size())


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


interface.register_callback(jpeg_image_change_val)
interface.register_callback(jpeg_image_snapshot)
interface.register_callback(jpeg_image_read)
interface.loop()
