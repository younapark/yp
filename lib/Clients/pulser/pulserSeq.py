import labrad
from labrad.units import WithUnit as U
cxn=labrad.connect()
p=cxn.pulser
p.stop_sequence()
p.new_sequence()
p.add_ttl_pulse('TTL17',U(100,'ms'),U(20,'ms'))
p.program_sequence()
p.start_number(10)