import labrad
from labrad.units import WithUnit as U

def get_keys(dict):
    x = []
    for i in range(len(dict)):
        x.append(dict[i][0])
    return x

cxn=labrad.connect()
pulser=cxn.pulser
pulser.stop_sequence()
channeldict = pulser.get_channels()
chanKeys = get_keys(channeldict)

pulser.new_sequence()
for i in chanKeys:
    pulser.add_ttl_pulse(i, U(100,'ms'), U(50,'ms'))
pulser.program_sequence()
pulser.start_number(5)



