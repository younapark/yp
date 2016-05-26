import labrad
from labrad.units import WithUnit as U
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks
import time
import os
import sys
import socket
# cxn=labrad.connect()
# pv=cxn.parametervault
# dv=cxn.data_vault
# datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S")
# dv.new('testing'+datasetNameAppend, [('independant label1', 'independant units1'), ('independant label2', 'indpendant units2')],
#        [(['dependant category', 'dependant label', 'dependant units'])], 'f')
#
# pv.reload_parameters()
# pv.refresh_parameters()
# collections=pv.get_collections()
# print collections
#
# for collectionName in collections:
#     parameters=pv.get_parameter_names(collectionName)
#     for parameterName in parameters:
#         pv.refresh_parameters()
#         pv.reload_parameters()
#         value=pv.get_parameter(collectionName,parameterName)
#         dv.add_parameter(collectionName+'_'+parameterName,value)
#         print collectionName, parameterName, value

class save_params(experiment):
    name = 'Save Parameters to Data Vault'
    exp_parameters = []
    exp_parameters.append(('testTTL', 'starttime'))
    exp_parameters.append(('testTTL', 'duration'))
    exp_parameters.append(('testTTL', 'timeSep'))
    @classmethod
    def all_required_parameters(cls):

        return cls.exp_parameters

    def set_scannable_parameters(self):

        '''
        gets parameters, called in run so scan works
        '''
        self.starttime = self.p.testTTL.starttime
        self.duration = self.p.testTTL.duration
        self.cycles = self.p.testTTL.cycles

    def makeDateDir(self, dirappend=''):

        localtime = time.localtime()
        dirappenddate = time.strftime("%Y%m%d", localtime)  # %b=Month name #%m=Month 1-12
        dirappendtime = time.strftime("%H%M%S", localtime)
        mydir = os.getcwd()
        # mydir = os.path.join(os.getcwd(), dirappend, dirappenddate+'.dir')
        mydir = os.path.join('F:\data', dirappend + '.dir', dirappenddate + '.dir')
        if not os.path.exists(mydir):
            os.makedirs(mydir)

        return mydir

    def initialize(self, cxn, context, ident):
        localtime = time.localtime()
        # datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S", localtime)
        # dirappend = [time.strftime("%Y%b%d", localtime), time.strftime("%H%M_%S", localtime)]
        # directory = ['', 'Experiments']
        # directory.extend([self.name])
        # directory.extend(dirappend)
       # directory=self.makeDir()

        self.U = U
        self.ident = ident
        self.cxn = labrad.connect(name='DDS Channel Tester')
        self.dv=self.cxn.data_vault
        self.pv=self.cxn.parametervault
   #     self.datasetNameAppend = time.strftime("%Y%b%d_%H%M_%S")
        self.collections = self.pv.get_collections()
        today = time.strftime('%Y%m%d')
        self.dv.cd(['', 'testcamera', today, 'param_ini'], True)
        dvInfo = self.dv.newMatrix('params',(1,1),'f')
        print 'frames saved into data vault'
        print 'data vault directory and file name:', dvInfo
        counter = dvInfo[1][0:5]
        print 'counter:', str(counter)
        self.counter=counter

        paramDir = self.makeDateDir('testcamera')
        paramDirName = paramDir + '\\'+counter+'_params.txt'
        self.parFile = open(paramDirName,'w')
        print 'New params file created:', paramDirName


    def run(self,cxn,context):

     for self.collectionName in self.collections:
        self.parameters=self.pv.get_parameter_names(self.collectionName)
        for self.parameterName in self.parameters:
            self.pv.refresh_parameters()
            self.pv.reload_parameters()

            parVal=self.pv.get_parameter(self.collectionName,self.parameterName)
            self.dv.add_parameter(self.collectionName+'_'+self.parameterName,parVal)
            print self.collectionName, self.parameterName,parVal
            if type(parVal)==labrad.units.Value:
                value = parVal[parVal.units]
                self.parFile.write('D'+self.parameterName+'=')
                self.parFile.write(str(value)+'\n')
            elif type(parVal)==str:
                self.parFile.write('S'+self.parameterName+'=')
                self.parFile.write(str(parVal)+'\n')
            elif type(parVal)==bool:
                self.parFile.write('B' + self.parameterName + '=')
                self.parFile.write(str(parVal) + '\n')
            elif type(parVal)==long :
                self.parFile.write('D' + self.parameterName + '=')
                self.parFile.write(str(parVal) + '\n')
            elif type(parVal)==labrad.units.DimensionlessFloat:
                self.parFile.write('D' + self.parameterName + '=')
                self.parFile.write(str(parVal) + '\n')
            else:
                print 'could not identify type of parameter value of', self.parameterName

     self.send_counter_udp()



#MESSAGE='{0:08b}'.format(6)
    def send_counter_udp(self):
        UDP_IP = '127.0.0.1'
        UDP_PORT = 2328
        MESSAGE = str(self.counter)
        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT
        print "UDP message:", MESSAGE
     #   print 'size:', sys.getsizeof(MESSAGE)

        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = save_params(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)


