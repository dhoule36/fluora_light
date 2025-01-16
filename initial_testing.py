import time
import json
from protobuf_decoder.protobuf_decoder import Parser
import base64

test = bytearray.fromhex("450000384ad1000040110262c0a85614c0a8561dc6ff1a6f00247dee2f5468576e787336356c30736a0000002c6669003ed1555400000000")

test2 = bytearray.fromhex("45000038cf39000040117df9c0a85614c0a8561dc5911a6f00244fab2f557637614d46773550326c580000002c6969000000000000000000")

print(len(test2))

import socket

def dump(x):
    return ''.join([type(x).__name__, "('",
                    *['\\x'+'{:02x}'.format(i) for i in x], "')"])

def send_bytes(ip_address, port, data):
    """Sends bytes to the specified IP address and port."""

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.connect((ip_address, port))

    try:
        # Send the data

        print('here')
        print(len('2f557637614d46773550326c580000002c6669003ff0000000000000'))

        hex_string = "2f5379594f5469586a51426a570000002c6969000000000100000000"
        parsed_data = Parser().parse("2f5379594f5469586a51426a570000002c6969000000000100000000")
        hex_string = base64.b64decode(hex_string)


        # print('here2')
        # for i in range(1):
        #     print(hex_string)
        #     nex_hex = hex_string
        #
        #     print('here')
        #     encodings = ['utf-7', 'utf-8', 'utf-8-sig',
        #                  'utf-16', 'utf-16-be', 'utf-16-le',
        #                  'utf-32', 'utf-32-be', 'utf-32-le',
        #                  'ASCII', 'latin-1', 'iso-8859-1']
        #     for enc in encodings:
        #         try:
        #             print(
        #                 '[' + enc + ']: \t\t' + nex_hex.decode(
        #                     enc))
        #         except Exception as e:
        #             print('[' + enc + ']: \t\t' + str(e))


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
        # 2f557637614d46773550326c580000002c666900XXBBGGBB00000000
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

        x_values = [2, 5, 20, 60, 100]
        y_values = [1, 2, 3, 4, 5]

        coefficients = np.polyfit(x_values, y_values, 4)
        while True:
            val = input("percentage: ")
            try:
                val = int(val)
                if not (1 <= val <= 100):
                    print("must be 1-100")
                test_val = .1
                result = (val**test_val)
                result = scale_number(result-1, 0, 100**test_val - 1, 3932160, 4160442)

                val = "2f557637614d46773550326c580000002c666900" + hex(int(result))[2:] + "0000000000"
                sock.send(bytearray.fromhex(val))
                # XX -> 40 maxes out, 3f is like 60%, 3e is like 20%, 3d is like 5%, 3c is like 2%

                print("output val: " + str(result))
                print("output val (hex): " + str(hex(int(result))))
            except Exception as e:
                print(e)
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
        # 2f557637614d46773550326c580000002c666900XXBBGGBB00000000
        # SATURATION
        # 2f7936383755345a67796d736a0000002c666900XXYYYY0000000000
        # POWER
        # 2f5379594f5469586a51426a570000002c6969000000000100000000


  ###### HUGE DISCOVERY, IT APPEARS THAT THE VALUES ARE SCALED ALMOST EXACTLY BY A FACTOR OF val**0.1!
    finally:
        # Close the socket
        sock.close()


# Example usage
if __name__ == "__main__":
    ip_address = "192.168.86.29"  # Replace with the desired IP address
    port = 6767  # Replace with the desired port

    send_bytes(ip_address, port, test)
