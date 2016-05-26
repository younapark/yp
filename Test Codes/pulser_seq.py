import labrad
from labrad.units import WithUnit as U
import time
cxn=labrad.connect()
pulser=cxn.pulser
pulser.stop_sequence()
time.sleep(2)
pulser.new_sequence()
pulser.add_ttl_pulse('TTL3',U(0.5,'s'),U(1,'s'))
pulser.add_ttl_pulse('TTL3',U(2.0,'s'),U(0.3,'s'))
pulser.add_ttl_pulse('TTL2',U(0.5,'s'),U(0.5,'s'))
pulser.add_ttl_pulse('TTL2',U(1.2,'s'),U(0.2,'s'))
pulser.program_sequence()
pulser.start_number(10000)


