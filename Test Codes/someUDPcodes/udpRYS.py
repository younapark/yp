import numpy as np
import SocketServer
from threading import Thread
import ConfigParser

#p=ConfigParser.ConfigParser()
#p.read("testdata.ini")
#dict=p.__dict__

#print dict

#path='/test/'
#file = 'testdata.ini'
#data=open('testdata.ini').read()
#strdata=str(data)



x = np.array([[55., 1000., 45.], [20., 3., 10.]])
y=1
class UDP_Interrupt(SocketServer.BaseRequestHandler):

    def setup(self):
        pass

    def handle(self):
        data = self.request[0].strip()
        print data
        socket = self.request[1]
        print "{}{} wrote:".format(self.client_address[0], self.client_address)
        print data
        print x
       # socket.sendto(x.tostring('C'), self.client_address)
        socket.sendto(x, self.client_address)
       # socket.sendall(strdata)
        #scipy.io.savemat('/Users/empire/Documents/MATLAB/hybridQuadSim/quaternionController/models/mapData.mat', mdict={'mapData': x})

    def finish(self):
        pass

class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):

    pass

if __name__ == "__main__":
    map_server = ThreadedUDPServer(('127.0.0.1', 9090), UDP_Interrupt)





    # terminate with Ctrl-C
    try:
        server_thread = Thread(target=map_server.serve_forever)
        server_thread.daemon = False
        server_thread.start()
        print "Server loop running in thread:", server_thread.name

    except KeyboardInterrupt:
        sys.exit(0)