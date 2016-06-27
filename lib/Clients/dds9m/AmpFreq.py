import labrad
cxn=labrad.connect()
d = cxn.dds9m
print 'Change Amplitude and Frequency'
d.write('I a')
d.write('V1 1') #set channel 0 at half of max voltage
d.set_freq(1,110) #set channel 0 at 110 MHz