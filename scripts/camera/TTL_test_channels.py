import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks
import time
class TTL_test_channels(experiment):

    name = 'TTL Channel Tester'

    exp_parameters = []
    exp_parameters.append(('testTTL', 'starttime'))
    exp_parameters.append(('testTTL', 'duration'))
    #exp_parameters.append(('testTTL', 'frequency'))
    exp_parameters.append(('testTTL', 'cycles'))
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
        from labrad.units import WithUnit as U

        self.U = U
        self.ident = ident
        self.cxn = labrad.connect(name='DDS Channel Tester')
        self.pulser = self.cxn.pulser
        channeldict= self.pulser.get_channels()
        self.chanKeys = self.get_keys(channeldict)

        self.starttime = self.U(100, 'ms')
        self.p = self.parameters



    def run(self, cxn, context):
        from labrad.units import WithUnit as U
        channelDict = self.pulser.get_channels()
        self.chanKeys = self.get_keys(channelDict)

        self.pulser.stop_sequence()

        self.pulser.new_sequence()
        for i in self.chanKeys:
            self.pulser.add_ttl_pulse(i, self.p.testTTL.starttime, self.p.testTTL.duration)
        self.pulser.program_sequence()
        self.pulser.start_number(int(self.p.testTTL.cycles))
        time.sleep(3)


    def finalize(self, cxn, context):
        self.pulser.stop_sequence()

        self.cxn.disconnect()

    def get_keys(self, dict):
        self.x = []
        for i in range(len(dict)):
            self.x.append(dict[i][0])
        return self.x
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TTL_test_channels(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)

