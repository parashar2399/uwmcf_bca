from pymodbus.client.sync import ModbusTcpClient #used to establish connection to modbus
import tkinter as tk #gui 
from tools import Gauge #display meter
from time import time
from convert_data import *
from bca import BCA_Display
def volts_to_current(volts,res = 49730):
    current = volts/res
    return current

update_time = 10#in ms    

#client = ModbusTcpClient('192.168.0.73') #default port 502 
#client.connect()

display = BCA_Display()
beamline_button_names = ['A21', 'Zero', 'B21', 'B50'] #edit this list to modify/add/remove buttons
buttons = display.button_group(beamline_button_names)


gauge1, cbs1 = display.gauge_block(1, 0, 'group1') #increment columns by 10 and rows by 2 when necessary
gauge2, cbs = display.gauge_block(1, 11, 'group2')
#gauge3, cbs = display.gauge_block(1, 21, 'group3')
gauge4, cbs = display.gauge_block(3, 0, 'group4')
gauge5, cbs = display.gauge_block(3, 11, 'group5')
#gauge6, cbs = display.gauge_block(3, 21, 'group6')
def update_gauge():
    start = time()
    volts = 0
    current = volts_to_current(volts, res = 50000)
    for i in range(len(cbs1)):
        var = cbs1[i][0]
        name = cbs1[i][1]
        reg = cbs1[i][2]
        #print(reg)
        if var.get()==1: 
            volts = display.read(int(reg))
            current = current+volts_to_current(volts, res = 50000)
        
    #print(time()-start)    
    #result = client.read_input_registers(26,2)
    #print(volts)
    
    gauge1.set_value(current)
    display.update(update_time, update_gauge)

display.update(update_time, update_gauge)
display.mainloop()
    
 