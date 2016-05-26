from pymba import *
import cv2
import numpy as np

vimba = Vimba()

vimba.startup()

system = vimba.getSystem()
system.runFeatureCommand("GeVDiscoveryAllOnce")

cameraIds = vimba.getCameraIds()

camera = vimba.getCamera(cameraIds[0])

camera.openCamera()

# camera.AcquisitionMode = 'Continuous'
camera.TriggerMode = 'On'
# camera.TriggerSource='Freerun'
camera.TriggerSource = 'Line2'
camera.TriggerActivation = 'RisingEdge' #
# camera.PixelFormat = 'Mono8'  # Mono8, Mono12, change np.arrray value from np.uint8 to np.uint16 for Mono12
camera.TriggerSelector='FrameStart' #FrameStart, AcquisitionStart
camera.AcquisitionMode ='Continuous' #Both SingleFrame and Continuous works


camera.closeCamera()
camera.openCamera()
print 'TriggerMode:', camera.TriggerMode
print 'TriggerSource:', camera.TriggerSource
print 'TriggerActivation:', camera.TriggerActivation
print 'TriggerSelector:', camera.TriggerSelector

frame = camera.getFrame()

frame.announceFrame()

camera.startCapture()
camera.runFeatureCommand('AcquisitionStart')
frame.queueFrameCapture()

frame.waitFrameCapture(10000)
camera.runFeatureCommand('AcquisitionStop')
print 'frame 1 captured or timed out '

imgData1 = frame.getBufferByteData()


print 'frames saved'
camera.endCapture()

data1_np = np.ndarray(buffer=imgData1,
                           dtype=np.uint8,
                           shape=(frame.height, frame.width))

rgb = cv2.cvtColor(data1_np, cv2.COLOR_BAYER_RG2RGB)

cv2.imwrite( 'testTrigger.png'.format(1), rgb)
camera.revokeAllFrames()
camera.closeCamera()
print 'frame is saved as png'

