import time
import json
from enum import Enum
from operator import concat

import base64
import socket

class ControlChoice(str, Enum):
    a = "Brightness"
    b = "Hue"
    c = "Saturation"
    d = "Power"

control_choice_dict = {"a": "Brightness",
                       "b": "Hue",
                       "c": "Saturation",
                       "d": "Power"
}

control_hex_dict = {"Brightness": "2f557637614d46773550326c580000002c666900",
                    "Hue": "2f5468576e787336356c30736a0000002c666900",
                    "Saturation": "2f7936383755345a67796d736a0000002c666900",
                    "Power": "2f5379594f5469586a51426a570000002c6969000000000"
                    }

def send_bytes(ip_address, port):
    """Sends bytes to the specified IP address and port."""

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.connect((ip_address, port))

    try:
        # Send the data


        # THE START 13 BYTES NEED TO CHANGE TO DIFFERENT VALUES
        # 2f557637614d46773550326c580000002c6669003ff0000000000000
        # 2f557637614d46773550326c580000002c666900XYZ0000000000000
        # BRIGHTNESS
        # 6669 -> change value
        # 6969 -> doesn't change value??
        # 3F = ? -> changes the value
        # X -> needs to be 3 to set brightness I think
        # YZ-> brightness value out of 255 I believe
        #
        #val = "2f557637614d46773550326c580000002c6669003ff0000000000000"

        # HUE
        # XX -> needs to be 3d to control hue
        # all 3d then 0's represents red on left of slider
        # 3dff represents orange
        # 3eff represents light blue
        # 3fff represents red on far right of slider
        # BB -> controls blue value
        # GG -> controls green value
        # BB -> controls blue value
        # val = "2f5468576e787336356c30736a0000002c666900" + hex(3932160)[2:] + "0000000000"
        # sock.send(bytearray.fromhex(val))
        # time.sleep(2)
        # val = "2f5468576e787336356c30736a0000002c666900" + hex(4194304)[2:] + "0000000000"
        # sock.send(bytearray.fromhex(val))
        # val = "2f5468576e787336356c30736a0000002c666900" + hex(int((4194304+3932160)/2))[2:] + "0000000000"
        # sock.send(bytearray.fromhex(val))

        import numpy as np

        def scale_number(value, old_min, old_max, new_min, new_max):
            """
            Scales a value from one range to another.
            """
            return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

        while True:
            value_to_control_choice = input("Enter control (a) brightness, (b) hue, (c) saturation (d) power: ")
            if value_to_control_choice in control_choice_dict:
                value_to_control = control_choice_dict[value_to_control_choice]
                chosen_hex = control_hex_dict[value_to_control]
                if "Power" in value_to_control:
                    on_or_off = input("on or off?")
                    concat_hex = chosen_hex
                    concat_hex += "1" if on_or_off == "on" else "0"
                    concat_hex += "00000000"
                    sock.send(bytearray.fromhex(concat_hex))
                else:
                    percentage_entered = input("percentage: ")
                    try:
                        percentage_entered = int(percentage_entered)
                        if not (1 <= percentage_entered <= 100):
                            print("must be 1-100")
                        test_val = .1
                        result = (percentage_entered ** test_val)
                        result = scale_number(result - 1, 0, 100 ** test_val - 1, 3932160, 4160442)

                        percentage_entered = chosen_hex + hex(int(result))[2:] + "0000000000"
                        sock.send(bytearray.fromhex(percentage_entered))

                        print("output val: " + str(result))
                        print("output val (hex): " + str(hex(int(result))))
                    except Exception as e:
                        print("must be an int")




        # SATURATION
        # 2f7936383755345a67796d736a0000002c666900XXYYYY0000000000
        # val = "2f7936383755345a67796d736a0000002c666900" + hex(3932160)[2:] + "0000000000"
        # sock.send(bytearray.fromhex(val))
        # time.sleep(2)
        # val = "2f7936383755345a67796d736a0000002c666900" + hex(4194304)[2:] + "0000000000"
        # sock.send(bytearray.fromhex(val))
        # XX -> 40 maxes out, 3f is like 60%, 3e is like 20%, 3d is like 5%, 3c is like 2%
        # YYYY -> gets within the range of each of the XX's, so looks like:
        #   XXYYYY together represents the range
        # int range seems to be 3932160 - 4194304

        # POWER
        # 2f5379594f5469586a51426a570000002c6969000000000100000000
        # 2f5379594f5469586a51426a570000002c6969000000000X00000000
        # X -> 1 for on, 0 for off
        # off
        # val = "2f5379594f5469586a51426a570000002c6969000000000000000000"
        # sock.send(bytearray.fromhex(val))
        # time.sleep(2)
        # # on
        # val = "2f5379594f5469586a51426a570000002c6969000000000100000000"
        # sock.send(bytearray.fromhex(val))

        # BRIGHTNESS
        # 2f557637614d46773550326c580000002c6669003ff0000000000000
        # HUE
        # 2f557637614d46773550326c580000002c666900
        # SATURATION
        # 2f7936383755345a67796d736a0000002c666900XXYYYY0000000000
        # POWER
        # 2f5379594f5469586a51426a570000002c6969000000000100000000
    finally:
        # Close the socket
        sock.close()


# Example usage
if __name__ == "__main__":
    ip_address = "192.168.86.29"  # Replace with the desired IP address
    port = 6767  # Replace with the desired port

    send_bytes(ip_address, port)
