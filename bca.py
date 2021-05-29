import numpy as np
from pymodbus.client.sync import ModbusTcpClient
import yaml
import tkinter as tk
from tools import Gauge
import tkinter.font as fonts
import random
from convert_data import *
from PIL import ImageTk, Image

class BCA_Display:
    def __init__(self, config_file = 'beam_current_configs.yaml'):
        '''
        initialize the display
        parameters:
            - update_time (ms): rate at which the gauge updates
        '''
        #load IP address of ADCs
        #device_file = open('device_addresses.yaml')
        #self.addresses = yaml.load(device_file, Loader=yaml.FullLoader)['addresses']
        #connect to ADCs
        #self.adc_clients = [ModbusTcpClient(address) for address in self.addresses]
        self.adc_clients = ModbusTcpClient('192.168.0.73')
        print(1)
        try:
            client.connect()
            print(1)
        except:
            pass
        config = open(config_file)
        self.configs = yaml.load(config, Loader=yaml.FullLoader)['display'] # returns a dictionary
        self.root = tk.Tk()
        self.root.title("Beam Current Signal Display")
        self.root.configure(background = 'lightgrey')
        self.root.resizable(False, False)
        
        #s = tk.ttk.Style()
        #s.configure('TCheckbutton', background= 'white')
    
    def read(self, register_num):
        #result = self.adc_clients[0].read_input_registers(register_num,2)
        result = self.adc_clients.read_input_registers(register_num,2)
        #print(result.registers)
        return data_to_float32(result.registers)[0]
    
    def get_register_names(self):
        names = self.addresses['192.168.0.73']
        return names
    def _gauge(self):
        gauge = Gauge(self.root, label='Current', unit='A', window_size_for_avg = 10)
        gauge.grid(row = 0, column = 0,columnspan=2)
        return gauge
    
    def _checkbutton(self, text,v, command):
        cb = tk.Checkbutton(self.root,bg = '#FAF9F6', text=text, font = ('calibri', 42), variable = v)
        return cb
    def gauge_block(self, row, col, group_name):
        #img = tk.PhotoImage(file = 'U_check.gif')
        group = self.configs[group_name]
        gauge = self._gauge()
        check_buttons = []
        variables = []
        gauge.grid(row = row, column = col,columnspan=10)
        for i in range(len(group)):
            print(group)
            name = group[i][0]
            reg = group[i][1]
            v = tk.IntVar()
            variables.append((v, name,reg)) #each checkbutton has a (variable, name)
            cb = self._checkbutton(name, v, '')
            check_buttons.append(cb)
            cb.grid(row = row+1, column = col+2*i, padx = 10, pady = 10, columnspan = 3)
        return gauge, variables
    
    def button_group(self, text_list):
        bgroup = [] 
        size = 150,78
        try: #if image exists in directory
            img = ImageTk.PhotoImage(Image.open("radiation-oncology.jpeg").resize(size))
            label = tk.Label(self.root, text="Beamline", image = img, font = ('calibri', 20))
            label.image = img
        
        except: #if image does not exist in directory
            label = tk.Label(self.root, text="Beamline",font = ('calibri', 20))
        
        label.grid(row = 0, column = 0,columnspan =2, pady = 10)
        for i in range(len(text_list)):
            bgroup.append(tk.Button(self.root, text = text_list[i],height = 5, width = 10))
            bgroup[i].grid(row = 0,column = 2*i+2,columnspan =2)
        return bgroup
            
    def update(self, update_time, command, arg = None):
        self.root.after(update_time, command)
        
    def mainloop(self):
        self.root.mainloop()
        
        
        
        
            
            