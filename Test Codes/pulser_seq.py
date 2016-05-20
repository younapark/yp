import labrad
from labrad.units import WithUnit as U
import time
cxn=labrad.connect()
pulser=cxn.pulser
pulser.stop_sequence()
time.sleep(2)
pulser.new_sequence()
pulser.add_ttl_pulse('TTL4',U(1,'s'),U(1,'s'))
pulser.program_sequence()
pulser.start_number(10000)


