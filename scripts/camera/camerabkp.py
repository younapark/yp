import threading
from time import sleep

from pymba import *
import numpy as np
import cv2
import time
import labrad
from labrad.units import WithUnit as U

from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks
from subprocess import Popen
import sys
import socket

import os



class take_pic(object):

    def __init__(self):
        self.threads=[]
        self.running=True
        self.cxn=labrad.connect()
        self.pulser=self.cxn.pulser
        self.dv = self.cxn.data_vault
        self.pv = self.cxn.parametervault
    def dateSeq(self):
        self.pv.reload_parameters()
        self.previousDate = self.pv.get_parameter('DateSeq', 'Date')
        self.currentDate = time.strftime('%Y%m%d')
        self.seq = self.pv.get_parameter('DateSeq', 'Seq')

        if self.previousDate == self.currentDate:
            self.pv.set_parameter('DateSeq', 'Date', ('string', self.currentDate), True)
            print 'Same Date:', self.currentDate

        else:
            self.pv.set_parameter('DateSeq', 'Date', ('string', self.currentDate), True)
            #  self.seq = 0
            print 'New Date:'   , self.currentDate, self.seq
        self.pv.save_parameters_to_registry()
        return self.currentDate

    def makeDateDir(self,dirappend=''):

        localtime = time.localtime()
        dirappenddate = time.strftime("%Y%m%d", localtime)    #%b=Month name #%m=Month 1-12
        dirappendtime = time.strftime("%H%M%S", localtime)
        mydir = os.getcwd()
       # mydir = os.path.join(os.getcwd(), dirappend, dirappenddate+'.dir')
        mydir = os.path.join('F:\data',dirappend +'.dir',dirappenddate+ '.dir')
        if not os.path.exists(mydir):
            os.makedirs(mydir)

        return mydir






    def hardwareTrigger(self):

            vimba=Vimba()

            vimba.startup()

            system = vimba.getSystem()
            system.runFeatureCommand("GeVDiscoveryAllOnce")

            cameraIds = vimba.getCameraIds()

            camera = vimba.getCamera(cameraIds[0])

            camera.openCamera()

        #    camera.AcquisitionMode = 'Continuous'
            camera.TriggerMode = 'On'
            camera.TriggerSource='Line2'
            camera.PixelFormat='Mono12'
            camera.TriggerSelector='FrameStart'
            camera.AcquisitionMode='Continuous'
           # camera.SensorShutterMode='GlobalReset'
    #        camera.TriggerActivation='AnyEdge'
        #    camera.StrobeSource='LineIn2'
      #      camera.TriggerDelay=0


            frame = camera.getFrame()
            frame2= camera.getFrame()

            frame.announceFrame()
            frame2.announceFrame()

            camera.startCapture()

            frame.queueFrameCapture()
            frame2.queueFrameCapture()

            frame.waitFrameCapture(5000)

            print 'frame 1 captured or timed out '

            frame2.waitFrameCapture(5000)

            print 'frame 2 captured or timed out'


            self.imgData1=frame.getBufferByteData()
            self.imgData2=frame2.getBufferByteData()

            print 'frames saved'
            camera.endCapture()
            self.frame = frame
            self.frame2= frame2
            self.camera = camera

    def save_pictures(self): ##saves pictures as data vault and  .npy binary file
            self.data1_np = np.ndarray(buffer = self.imgData1,
                                       dtype = np.uint16,
                                       shape = (self.frame.height,self.frame.width))
            self.data2_np = np.ndarray(buffer=self.imgData2,
                                       dtype=np.uint16,
                                       shape=(self.frame2.height, self.frame2.width))
            framefloat1 = self.data1_np.astype(float)
            framefloat2 = self.data2_np.astype(float)
            print 'frame shape: ', framefloat1.shape

            today = time.strftime('%Y%m%d')
            ##save into data vault
            self.dv.cd(['', 'testcamera', today, 'csv','withatoms'], True)
            dvInfo = self.dv.newMatrix('withatoms',framefloat1.shape,'f')
            self.dv.add(framefloat1)
            self.dv.cd(['', 'testcamera', today,'csv','noatoms'], True)
            dvInfo2 = self.dv.newMatrix('noatoms', framefloat2.shape, 'f')
            self.dv.add(framefloat2)

            print 'frames saved into data vault'
            print 'data vault directory and file name:', dvInfo
            counter = dvInfo[1][0:5]
            print 'counter:', str(counter)

            ###make npy files

            npyDir=self.makeDateDir('testcamera')

        #    np.save(npyDir + '\\' + str(counter) + '_' + 'withatoms', self.data1_np)
        #    np.save(npyDir + '\\' + str(counter) + '_' + 'noatoms', self.data2_np)

            print 'frames saved as binary files:' , npyDir

            self.counter = counter #for usage in other functions

    def send_udp(self):
        UDP_IP = '127.0.0.1'
        UDP_PORT = 2328
        MESSAGE = str(self.counter)
        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT
        print "UDP message:", MESSAGE
      #  print 'size:', sys.getsizeof(MESSAGE)

        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    def save_png(self):
        pngDir = self.makeDateDir('png')
        rgb = cv2.cvtColor(self.data1_np, cv2.COLOR_BAYER_RG2RGB)
        rgb2 = cv2.cvtColor(self.data2_np, cv2.COLOR_BAYER_RG2RGB)
        cv2.imwrite(pngDir + '\\'+ self.counter + 'withatoms1.png'.format(1), rgb)
        cv2.imwrite(pngDir + '\\'+ self.counter + 'noatoms2.png'.format(1), rgb2)
        'frames saved as png'

    def sequence(self):
            pulser=self.pulser

           # pulser.switchAuto=('TTL2',True)

            time.sleep(2)
            pulser.stop_sequence()
            pulser.new_sequence()

            #second image not saved
            pulser.add_ttl_pulse('TTL2',U(100,'ms'),U(50,'ms'))
            pulser.add_ttl_pulse('TTL2',U(200,'ms'), U(50,'ms'))
            pulser.add_ttl_pulse('TTL3',U(110,'ms'), U(50,'ms'))
            pulser.add_ttl_pulse('TTL3',U(210,'ms'), U(50,'ms'))

            pulser.program_sequence()

            pulser.start_number(1)


    def start_threads(self):
        t1=threading.Thread(target=self.hardwareTrigger)
        t1.start()
        time.sleep(1)
        t2=threading.Thread(target=self.sequence)
        t2.start()
        self.threads.append(t1)
        self.threads.append(t2)

    def stop(self):
        time.sleep(1)
        self.pulser.stop_sequence()
        self.camera.revokeAllFrames()
        self.camera.closeCamera()


class camera(experiment):
    name = 'Take Two Pictures'



    def initialize(self, cxn, context, ident):
        self.t=take_pic()

    def run(self,cxn,context):
        self.t.start_threads()
        for t in self.t.threads: ##not sure whether they need to be joined? :')
            while t.isAlive():
                t.join(10)
        self.t.save_pictures()
  #      self.t.send_udp()
        self.t.save_png()




if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = camera(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)