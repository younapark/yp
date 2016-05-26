import labrad
cxn=labrad.connect()
d = cxn.dds9m
print 'Table Mode'
d.write('I e')
d.write('S')
d.write('M 0')

#d.write('I p')

d.t_add(0,0,10,0)
d.t_add(1,0,10,0)
d.t_add(0,1,20,0)
d.t_add(1,1,20,0)
d.t_add(0,2,30,0)
d.t_add(1,2,30,0)
d.t_add(0,3,40,0)
d.t_add(1,3,40,0)
d.t_add(0,4,50,0)
d.t_add(1,4,50,0)
d.t_last(0,5,60,0)
d.t_last(1,5,60,0)
d.write('M t')

#d.write('I m')
#d.write('I p')
# d.write('ts')
# d.write('ts')
# # d.write('ts')
