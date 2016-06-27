"""
### BEGIN NODE INFO
[info]
name = DDS9m2
version = 0.0
description =
instancename = DDS9m2

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from common.lib.servers.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
import time

SERVERNAME = 'DDS9m2'
TIMEOUT = 1.0
BAUDRATE = 19200

class DDS( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'DDS9m2'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')


    @inlineCallbacks
    def initServer( self ):
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        #port = yield self.getPortFromReg( self.regKey)
        #ports = yield self.getPortFromReg( self.regKey)
        port = 'COM5'
        #port = ports[1]
        self.count = 0
        self.lastAdded = False
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port, baudrate = BAUDRATE )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise


    @setting(1, chan = 'i', freq = 'v', returns= 's')
    def set_freq(self, c, chan, freq):
    ##chan = 0,1,2,3 ; freq = frequency value in MHz
        """Set Frequency of output channel in MHz to nearest 0.1Hz. Maximum setting: 171.1276031MHz. Single tone mode"""
        self.ser.write_line('I a')
        if freq >=  171.1276031:
            return "Set frequency " +str(freq)+ " MHz exceeds the maximum frequency of 171.1276031MHz"
        setVal = 'F' + str(chan) + ' ' + str(freq)
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine
    @setting(2, chan = 'i', N = 'i', returns= 's')
    def set_phase(self,c, chan,N):
        """channels = 0,1,2,3 ; N = 0 to 16383, phase = N* pi/ 8192.
        chan = 0,1,2,3 ; freq = frequency value in MHz"""

        setVal = 'P' + str(chan) + ' ' + str(N)
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()

        phase = N * 3.14/ 8192
        print 'phase is set at ', phase
        return readLine

    @setting(3, enable='b', returns='s')
    def set_echo(self, c, enable):
        """Serial echo control, True = enable, False = disable the echo"""
        if enable == True:
            setVal = 'E' + ' ' + 'E'
        else:
            setVal = 'E' + ' ' + 'D'
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(4, enable='s', returns='s')
    def set_clock_source(self, c, enable):
        """Select clock source. x=E for External clock, x=I for Internal Clock. May require
adjustment of Kp and external filtering of output when an external clock is used. Example: set_clock_source('I') """
        setVal = 'C' + ' ' + enable
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(5, returns='s')
    def reset(self, c, enable):
        """Reset the DDS9m, EEPROM data is preserved and if valid, is used upon restart. This is the same as cycling power.z"""
        setVal = 'R'
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(100, returns='s')
    def clear(self, c):
        """Clear. This command clears the EEPROM valid flag and restores all factory
        default values."""
        setVal = 'CLR'
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine
    @setting(6, enable= 'b', returns='s')
    def output_ctrl(self, c, enable):
        """"CMOS output control. x=E for LVCMOS Enable, x=D for LVCMOS Disable"""
        if enable == True:
            x = 'E'
        else:
            x = 'D'
        setVal = 'A' + ' ' + x
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(7, returns='s')
    def EEPROM(self, c):
        """Saves current state into EEPROM and sets valid flag. State used as default upon
        next power up or reset. Use the CLR command to return to default values"""
        setVal = 'S'
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(8, returns='s')
    def get_status(self, c):
        """Return present frequency, phase and status. Returns a character string of all internal
        settings."""
        setVal = 'QUE'
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(9, enable='b', returns='s')
    def set_mode(self, c, enable):
        """Mode command. Mode 0 is single tone on all channels (default). If N=a, then the
phase is automatically cleared during each command; if N=n, then the phase is not
cleared (default). Incomplete"""
        if enable == True:
            x = 'E'
        else:
            x = 'D'
        setVal = 'A' + ' ' + x
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(10, chan = 'i', N = 'i', returns='s')
    def set_voltage(self, c, chan, N):

        """Set voltage level of channel.
        chan = 0,1,2,3 ; N < 1024 integer; Voltage = N/1023
        In default, the amplitude is set to the maximum. N can range from 0 (off) to 1023 (no
decimal point allowed). Voltage level is scaled by N/1023. n=0, 1, 2, 3 to set the
amplitude on frequency 0, 1, 2 or 3. If N >=1024, the scaling is turned off and the
selected output is set to full scale"""
        if N >= 1024:
            assert "N has to be smaller than 1024"
        setVal = 'V' + str(chan) + ' ' + str(N)
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        voltage = float(N)/1023
        print voltage
        print "voltage level is of channel ", str(chan), " is set at voltage ", str(voltage)
        return readLine

    @setting(11, N='i', returns='s')
    def output_scaling_factor(self, c, N):
        """"Chan = 0,1,2,3; N = 1,2,4,8; Set the output scaling factor. N=1 for full scale, N=2 for half scale, N=4 for one
quarter scale and N=8 for one eighth scale. All channels are scaled equally."""

        setVal = 'Vs' + ' ' + str(N)
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(12, aa = 'i', returns ='s')
    def dds_mult_const(self, c, aa):
        """"Set the DDS on-chip PLL reference multiplier constant. Must be one Hexadecimal
    byte as two characters. Legal values are 1 (bypass PLL) and 4 to 20 (01h, 04h to
    14h). Values of Kp times clock frequency must not be between 160MHz and
    255MHz (for internal clock, this disallows 5<=Kp<= 9). (see paragraph 4.12 for
    other considerations) ** incomplete **"""
        setVal = 'Kp' + ' ' + str(aa)
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(13, x = 's', returns = 's')
    def IO_update_method(self, c, x):
        """Set the I/O update pulse method. If x=a, then an I/O update is issued automatically
at the end of each serial command (such as set_freq or F0 100Hz). If x=m, then a manual I/O update
pulse is expected to be sent by a subsequent I p command. """
        setVal = 'I' + ' ' + str(x)
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(14, byte = 's' , returns = 's')
    def send_byte(self,c, byte):
        """This Byte command allows each register in the DDS chip to be set. Different
registers require a various number of bytes to be written depending upon the
function. Please consult the Analog Devices AD9959 data sheet for details. Note
that it is possible to set the DDS chip into a non-functional mode, requiring a
power cycle to recover. All values are in hexadecimal and no error checking, other
than correct format, is performed.**incomplete**"""
        setVal = 'B' + ' ' + byte
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(15, chan = 'i', seq = 'i', freq = 'i', dwell='i', returns = 's')
    def t_add(self,c,chan,seq,freq,dwell= 0):
        '''t_add(Channel Number [0,1], seq=0,1,... for RAM Adress, frequency in MHz, dwell time in 100 microseconds). Returns values written to the relevant address.'''

        freqNum = float(freq) * 10**7 ##Converts to 0.1Hz
        freqHex = '%08x' % freqNum
        if dwell != 0:
            dwellHex = '%02x' % dwell
        else:
            dwellHex = 'ff'
        addr = '%04d' % seq
        freqHexLine = 't' +str(chan) + ' ' + addr + ' ' + freqHex +',0000,03ff,' + dwellHex
        Dval = 'D'+str(chan)+' '+str(addr)
        print 'freqHexLine Input:', freqHexLine

        self.ser.write_line(freqHexLine)
        self.ser.write('\n')

        self.ser.write_line(Dval)
        ramRead = self.ser.read()
        returnVal = 'RAM Value: ', ramRead
     #   self.count = self.count + 1
        return ramRead


    @setting(16, returns='s')
    def t_new(self,c):
        setVal = 'M 0'
        self.ser.write_line(setVal)
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.lastAdded=False
        return readLine

    @setting(17, chan = 'i', seq = 'i', freq = 'i', dwell='i', returns = 's')
    def t_last(self,c,chan,seq,freq,dwell):
        '''t_last(Channel Number [0,1], seq=0,1,... for RAM Adress, frequency in MHz, dwell time in 100 microseconds). The last table record must be added separately with this function. Returns values written to the relevant address. it will turn off currently running table mode
        '''
        freqNum = float(freq) * 10 ** 7  ##Converts to 0.1Hz
        freqHex = '%08x' % freqNum
        addr = '%04d' % seq
        freqHexLine = 't' + str(chan) + ' ' + addr + ' ' + freqHex + ',0000,03ff,00'
        Dval = 'D' + str(chan) + ' ' + str(addr)
        print 'freqHexLine Input:', freqHexLine

        self.ser.write_line(freqHexLine)
        self.ser.write('\n')

        self.ser.write_line(Dval)
        ramRead = self.ser.read()
        returnVal = 'RAM Value: ', ramRead
        #   self.count = self.count + 1
        self.lastAdded = True


        return ramRead

    @setting(101, returns='s')
    def t_start(self,c):
        '''starts the table mode. '''
        if self.lastAdded == False:
            assert 'Last frequency has not been added.'
        self.ser.write_line('M t')
        self.ser.write_line('ts')
        self.ser.write_line('ts')
        readLine = self.ser.read()
        return readLine


    @setting(200, x='s', returns='s')
    def write(self, c, x):
        """Same as write_line in serial server. """

        self.ser.write_line(str(x))
        self.ser.read_line()
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return readLine

    @setting(102, freqs='*v', returns='s')
    def t_freqs(self, c, freqs):
        """input frequencies as [10,20,30,40,50] MHz. The frequencies can be triggered by hardware triggers pin 10 and pin 14. Trigger 10 and then 14 afterwards."""
        print 'Table Mode'
        self.write(c, 'I m')
        self.write(c, 'I e')
        self.write(c, 'S')
        self.write(c, 'M 0')

        for i in range(len(freqs) - 1):
            self.t_add(c, 0, i, freqs[i], 0)
            self.t_add(c, 1, i, freqs[i], 0)

        lastNum = len(freqs) - 1
        self.t_last(c, 0, lastNum, freqs[lastNum], 0)
        self.t_last(c, 1, lastNum, freqs[lastNum], 0)

        self.write(c, 'M t')
        readLine = self.ser.read_line()
        self.ser.flushinput()
        self.ser.flushoutput()
        return ''

            # @setting(102, freqs='*v', returns='s')
    # def t_freqs(self, c,freqs,freqs2):
    #     """input frequencies as [10,20,30,40,50] MHz. The frequencies can be triggered by hardware triggers pin 10 and pin 14. Trigger 10 and then 14 afterwards."""
    #     print 'Table Mode'
    #     self.write(c,'I m')
    #     self.write(c,'I e')
    #     self.write(c,'S')
    #     self.write(c,'M 0')
    #
    #     for i in range(len(freqs)-1):
    #         self.t_add(c,0,i,freqs[i],0)
    #         self.t_add(c,1,i,freqs[i],0)
    #
    #     lastNum = len(freqs)-1
    #     self.t_last(c,0,lastNum,freqs[lastNum],0)
    #     self.t_last(c,1,lastNum,freqs[lastNum],0)
    #
    #     self.write(c,'M t')
    #     readLine = self.ser.read_line()
    #     self.ser.flushinput()
    #     self.ser.flushoutput()
    #     return ''



        # def errorDecode(self,readline):
    #     if readline == 'OK': return 'Good Command'
    #     elif readline == '?0': return 'Unrecognized Command'
    #     elif readline == '?1': return "Bad Frequency"
    #     elif readline == '?2': return "Bad AM Command"
    #     elif readline == '?3': return "Bad Input line too long"
    #     elif readline == '?4': return "Bad Phase"
    #     elif readline == '?5': return "Bad Time"
    #     elif readline == '?6': return "Bad Mode"
    #     elif readline == '?7': return "Bad Amp"
    #     elif readline == '?f': return "Bad Byte"
    #     else: return readline





if __name__ == "__main__":
    from labrad import util
    util.runServer( DDS() )
