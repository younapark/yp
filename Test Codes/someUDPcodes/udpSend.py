import socket
import sys

UDP_IP = '127.0.0.1'
UDP_PORT = 2328
MESSAGE = '8'

#MESSAGE='{0:08b}'.format(6)

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE
print 'size:', sys.getsizeof(MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
