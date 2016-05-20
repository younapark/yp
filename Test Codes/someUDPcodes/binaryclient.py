import binascii
import socket
import struct
import sys
#https://pymotw.com/2/socket/binary.html
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)
sock.connect(server_address)
#
# values = (1, 'ab', 2.7)
# packer = struct.Struct('I 2s f')
# packed_data = packer.pack(*values)
values = (1,'a')
packer = struct.Struct('I 1s')
packed_data = packer.pack(*values)

try:

    # Send data
   # print >>sys.stderr, 'sending "%s"' % binascii.hexlify(packed_data), values
 #   sock.sendall(packed_data)
    data='{0:08b}'.format(6)
    sock.send(data)

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()