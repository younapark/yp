from pymba import *

vimba = Vimba()

vimba.startup()

system = vimba.getSystem()
system.runFeatureCommand("GeVDiscoveryAllOnce")

cameraIds = vimba.getCameraIds()

camera = vimba.getCamera(cameraIds[0])

camera.openCamera()

camera.AcquisitionMode = 'Continuous'
camera.TriggerMode = 'On'
camera.TriggerSource = 'Line2'
camera.PixelFormat = 'Mono8'  # Mono8, Mono12, make sure to change np.arrray value np.uint8 to np.uint16
camera.TriggerSelector = 'AcquisitionStart'  # FrameStart, AcquisitionStart
camera.ExposureTimeAbs = 5000
system.getFeaturenames()
camera.getFeatureNames()