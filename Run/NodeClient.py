import labrad
import time
cxn = labrad.connect()
node = cxn.node_lab_pc_1

node.start('Pulser')
node.start('Data Vault')
node.start('ParameterVault')
node.start('ScriptScanner')
node.start('Serial Server cg')
node.start('DDS9m')
node.start('DDS9m2')