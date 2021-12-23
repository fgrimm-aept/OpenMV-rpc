# Remote Control - As The Controller Device
#
# This script remotely controls an OpenMV Cam using the RPC library.
#
# This script is meant to talk to the "popular_features_as_the_remote_device.py" on the OpenMV Cam.

import json
import rpc
import struct
from datetime import datetime

##############################################################
# Choose the interface you wish to control an OpenMV Cam over.
##############################################################

# Uncomment the below lines to setup your OpenMV Cam for controlling over a USB VCP.
#
# * port - Serial Port Name.
#
# print("\nAvailable Ports:\n")
# for port, desc, hwid in serial.tools.list_ports.comports():
#     print("{} : {} [{}]".format(port, desc, hwid))
# sys.stdout.write("\nPlease enter a port name: ")
# sys.stdout.flush()
# interface = rpc.rpc_usb_vcp_master(port=input())
# print("")
# sys.stdout.flush()


# Uncomment the below line to setup your OpenMV Cam for controlling over WiFi.
#
# * slave_ip - IP address to connect to.
# * my_ip - IP address to bind to ("" to bind to all interfaces...)
# * port - Port to route traffic to.
#
interface = rpc.rpc_network_master(slave_ip="192.168.0.120", my_ip="", port=0x1DBA)


# Uncomment the below lines to setup your OpenMV Cam for controlling over a UART (Serial / COM Port).
#
# * port - Serial Port Name.
# * baudrate - Bits per second.
#
# print("\nAvailable Ports:\n")
# for port, desc, hwid in serial.tools.list_ports.comports():
#     print("{} : {} [{}]".format(port, desc, hwid))
# sys.stdout.write("\nPlease enter a port name: ")
# sys.stdout.flush()
# interface = rpc.rpc_uart_master(port=input(), baudrate=115200)
# print("")
# sys.stdout.flush()

# Uncomment the below line to setup your OpenMV Cam for controlling over CAN.
#
# * channel - Kvarser CAN channel number.
# * message_id - 11-bit message ID to use for data transport.
# * bit_rate - CAN baud rate.
# * sampling_point - Sampling point percentage.
#
# from canlib import canlib
# print("\nAvailable Channels:\n")
# for channel in range(canlib.getNumberOfChannels()):
#     chdata = canlib.ChannelData(channel)
#     print("%d. %s (%s / %s)" % (channel, chdata.channel_name, chdata.card_upc_no, chdata.card_serial_no))
# sys.stdout.write("\nPlease enter a channel name: ")
# sys.stdout.flush()
# interface = rpc.rpc_kvarser_can_master(channel=int(input()), message_id=0x7FF, bit_rate=250000, sampling_point=75)
# print("")
# sys.stdout.flush()

##############################################################
# Call Back Handlers
##############################################################

def exe_jpeg_snapshot():
    result = interface.call("jpeg_snapshot")
    if result is not None:
        name = "snapshot-%s.jpg" % datetime.now().strftime("%d.%m.%Y-%H.%M.%S")
        print("Writing jpeg %s..." % name)
        with open(name, "wb") as snap:
            snap.write(result)


# Execute remote functions in a loop. Please choose and uncomment one remote function below.
# Executing multiple at a time may run slowly if the camera needs to change camera modes
# per execution.

while True:
    exe_jpeg_snapshot()
