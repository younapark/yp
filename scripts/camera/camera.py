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


    def makeDateDir(self,dirappend='',dirappend2=''):

        localtime = time.localtime()
        dirappenddate = time.strftime("%Y%m%d", localtime)    #%b=Month name #%m=Month 1-12
        dirappendtime = time.strftime("%H%M%S", localtime)
        mydir = os.getcwd()
        dir1=''
        dir2=''
        if dirappend != '':
            dir1=dirappend+'.dir'
        if dirappend2 != '':
            dir2 = dirappend2 + '.dir'
       # mydir = os.path.join(os.getcwd(), dirappend, dirappenddate+'.dir')
        mydir = os.path.join('F:\data',dir1,dirappenddate+ '.dir',dir2)
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

            # camera.AcquisitionMode = 'Continuous'
            # camera.TriggerMode = 'On'
           # camera.TriggerSource='Line2'
            camera.PixelFormat='Mono8' #Mono8, Mono12, make sure to change np.arrray value np.uint8 to np.uint16
           # camera.TriggerSelector='AcquisitionStart' #FrameStart, AcquisitionStart
           # camera.AcquisitionMode='SingleFrame' #Continuous, SingleFrame
           # camera.SensorShutterMode='GlobalReset'
    #        camera.TriggerActivation='AnyEdge'
        #    camera.StrobeSource='LineIn2'
      #      camera.TriggerDelay=0


            frame = camera.getFrame()
            frame2= camera.getFrame()

            frame.announceFrame()
            frame2.announceFrame()

            camera.startCapture()
            camera.runFeatureCommand('AcquisitionStart')
            frame.queueFrameCapture()
            frame2.queueFrameCapture()

            frame.waitFrameCapture(30000)

            print 'frame 1 captured or timed out '

            frame2.waitFrameCapture(30000)

            print 'frame 2 captured or timed out'
            camera.runFeatureCommand('AcquisitionStop')

            self.imgData1=frame.getBufferByteData()
            self.imgData2=frame2.getBufferByteData()

            print 'frames saved'
            camera.endCapture()
            self.frame = frame
            self.frame2= frame2
            self.camera = camera

    def save_pictures(self): ##saves pictures as data vault and  .npy binary file
            self.data1_np = np.ndarray(buffer = self.imgData1,
                                       dtype = np.uint8,
                                       shape = (self.frame.height,self.frame.width))
            self.data2_np = np.ndarray(buffer=self.imgData2,
                                       dtype=np.uint8,
                                       shape=(self.frame2.height, self.frame2.width))
            framefloat1 = self.data1_np.astype(float)
            framefloat2 = self.data2_np.astype(float)
            print 'frame shape: ', framefloat1.shape

            today = time.strftime('%Y%m%d')
            ##save into data vault
            self.dv.cd(['', 'testcamera', today, 'csv','withatoms'], True)
            dvInfo = self.dv.newMatrix('withatoms',framefloat1.shape,'f')
            self.dv.cd(['', 'testcamera', today,'csv','noatoms'], True)
            dvInfo2 = self.dv.newMatrix('noatoms', framefloat2.shape, 'f')
          # dv.add will store the frames into .csv, but we won't need them as we will use the binary files .npy.
          # self.dv.add(framefloat1)
          # self.dv.add(framefloat2)

            print 'frames saved into data vault'
            print 'data vault directory and file name:', dvInfo
            counter = dvInfo[1][0:5]
            print 'counter:', str(counter)

            ###make npy files

            npyDir=self.makeDateDir('testcamera')

            np.save(npyDir + '\\' + str(counter) + '_' + 'withatoms', self.data1_np)
            np.save(npyDir + '\\' + str(counter) + '_' + 'noatoms', self.data2_np)

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
        pngDir = self.makeDateDir('testcamera','png')
        rgb = cv2.cvtColor(self.data1_np, cv2.COLOR_BAYER_RG2RGB)
        rgb2 = cv2.cvtColor(self.data2_np, cv2.COLOR_BAYER_RG2RGB)
        cv2.imwrite(pngDir + '\\'+ self.counter + '_withatoms1.png'.format(1), rgb)
        cv2.imwrite(pngDir + '\\'+ self.counter + '_noatoms2.png'.format(1), rgb2)
        'frames saved as png'

    def sequence(self):
            pulser=self.pulser

           # pulser.switchAuto=('TTL2',True)

            time.sleep(1)
            pulser.stop_sequence()
            pulser.new_sequence()

            #second image not saved
            pulser.add_ttl_pulse('TTL2',U(100,'ms'),U(100,'ms'))
            pulser.add_ttl_pulse('TTL2',U(300,'ms'), U(100,'ms'))
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

    exp_parameters = []
    exp_parameters.append(('testTTL', 'starttime'))
    exp_parameters.append(('testTTL', 'duration'))
    exp_parameters.append(('testTTL','timeSep'))

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

    def initialize(self, cxn, context, ident):
        self.t=take_pic()

    def run(self,cxn,context):
        self.t.start_threads()
        for t in self.t.threads: ##not sure whether they need to be joined? :')
            while t.isAlive():
                t.join(5)
        self.t.save_pictures()
  #      self.t.send_udp()
        self.t.save_png()




if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = camera(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)