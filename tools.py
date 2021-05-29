'''
Adapted from the tk_tools package
Source: https://tk-tools.readthedocs.io/en/latest/
Github: https://github.com/slightlynybbled/tk_tools
        https://github.com/slightlynybbled/tk_tools/blob/7a31da6695bc6c2759b0e563bdde4ad00cb1c7d1/tk_tools/canvas.py#L182
        
Please install the following libraries to use this class:
    1. engineering_notation
    2. statistics
'''

import tkinter as tk
import tkinter.ttk as ttk
from collections import deque
from statistics import mean
from engineering_notation import EngUnit
class Gauge(ttk.Frame):
    """
    Shows a gauge

        gauge = Gauge(root, max_value=100.0,
                      label='speed', unit='km/h')
        gauge.grid()
        gauge.set_value(10)

    :param parent: tkinter parent frame
    :param width: canvas width
    :param height: canvas height
    :param min_value: the minimum value
    :param max_value: the maximum value
    :param label: the label on the scale
    :param unit: the unit to show on the scale
    :param divisions: the number of divisions on the scale
    :param yellow: the beginning of the yellow (warning) zone in percent
    :param red: the beginning of the red (danger) zone in percent
    :param yellow_low: in percent warning for low values
    :param red_low: in percent if very low values are a danger
    :param window_size_for_avg: list size for running mean. See the 'readout' function for more information
    :param bg: background
    """
    def __init__(self, parent, width: int = 500, height: int = 250,
                 min_value=0.0, max_value=100.0, label='', unit='',
                 divisions=10, yellow=100, red=100, yellow_low=0,
                 red_low=0, window_size_for_avg = 10, reset_when = 5, bg='#FAF9F6'):
        self._parent = parent
        self._width = width
        self._height = height
        self._label = label
        self._unit = unit
        self._divisions = divisions
        self._min_value = min_value
        self._max_value = max_value
        self._value = self._min_value
        self._average_value = (max_value + min_value) / 2
        self._yellow = yellow * 0.01
        self._red = red * 0.01
        self._yellow_low = yellow_low * 0.01
        self._red_low = red_low * 0.01
        self._reset_when = reset_when * 0.01
        self._upper_lim = self._max_value * (1-self._reset_when)
        self._lower_lim = self._max_value * self._reset_when
        self.window = deque([])
        for i in range(window_size_for_avg):
            self.window.append(0.0)
        super().__init__(self._parent)

        self._canvas = tk.Canvas(self, width=self._width,
                                 height=self._height, bg=bg)
        self._canvas.grid(row=0, column=0, sticky='news')
        self.font = 'Courier New'
        self._redraw()

    def _redraw(self):
        font_size = 14
        self._canvas.delete('all')
        max_angle = 120.0
        value_as_percent = ((self._value - self._min_value) /
                            (self._max_value - self._min_value))
        value = float(max_angle * value_as_percent)
        # no int() => accuracy
        # create the tick marks and colors across the top
        for i in range(self._divisions):
            extent = (max_angle / self._divisions)
            start = (150.0 - i * extent)
            rate = (i+1)/(self._divisions+1)
            if rate < self._red_low:
                bg_color = 'red'
            elif rate <= self._yellow_low:
                bg_color = 'yellow'
            elif rate <= self._yellow:
                bg_color = 'white'
            elif rate <= self._red:
                bg_color = 'yellow'
            else:
                bg_color = 'red'

            self._canvas.create_arc(
                0, int(self._height * 0.15),
                self._width, int(self._height * 1.8),
                start=start, extent=-extent, width=2,
                fill=bg_color, style='pie'
            )
        bg_color = 'white'
        red = '#c21807'
        ratio = 0.06
        self._canvas.create_arc(self._width * ratio,
                                int(self._height * 0.25),
                                self._width * (1.0 - ratio),
                                int(self._height * 1.8 * (1.0 - ratio * 1.1)),
                                start=150, extent=-120, width=2,
                                fill=bg_color, style='pie')
        # readout & title
        self.readout(self._value, 'black')  # BG black if OK

        # display lowest value
        value_text = EngUnit(self._min_value)
        self._canvas.create_text(
            self._width * 0.06, self._height * 0.65,
            font=(self.font, font_size), text=value_text)
        # display greatest value
        value_text = EngUnit(self._max_value)
        self._canvas.create_text(
            self._width * 0.94, self._height * 0.65,
            font=(self.font, font_size), text=value_text)
        # display center value
        value_text = EngUnit(self._average_value)
        self._canvas.create_text(
            self._width * 0.5, self._height * 0.1,
            font=(self.font, font_size), text=value_text)
        # display quarter value
        value_text = EngUnit(self._average_value/2)
        self._canvas.create_text(
            self._width * 0.25, self._height * 0.2,
            font=(self.font, font_size), text=value_text)
        # display three-quarter value
        value_text = EngUnit(self._average_value+self._average_value/2)
        self._canvas.create_text(
            self._width * 0.75, self._height * 0.19,
            font=(self.font, font_size), text=value_text)
        # create first half (black needle)
        self._canvas.create_arc(0, int(self._height * 0.15),
                                self._width, int(self._height * 1.8),
                                start=150, extent=-value, width=3,
                                outline='black')

        # create inset black
        self._canvas.create_arc(self._width * 0.35, int(self._height * 0.75),
                                self._width * 0.65, int(self._height * 1.2),
                                start=150, extent=-120, width=1,
                                outline='grey', fill='black', style='pie')

        # create the overlapping border
        self._canvas.create_arc(0, int(self._height * 0.15),
                                self._width, int(self._height * 1.8),
                                start=150, extent=-120, width=4,
                                outline='#343434')

    def readout(self, raw_value, bg):  # value, BG color
        '''
        This function takes a running mean of the current values and displays it on the readout.
        The running mean acts smooothes out the noisy inputs. 
        To stabiliize the readout, increase the window size. A smaller window size will result
        in readouts that fluctuate more. 
        NOTE: a window size too large will have a very slow response. recommended window size 15+/-5.
        '''
        r_width = 110
        r_height = 35
        r_offset = 8 #rectangle offset
        text_offset = r_offset + 10 #text offset
        font_size = 18
        xfactor = 0.85
        yfactor = 0.85
        self.window.popleft()
        self.window.append(raw_value)
        #new_window = [float(i) for i in self.window]
        value = mean(self.window)
        self._canvas.create_rectangle(
            self._width*xfactor - r_width/2,
            self._height*yfactor - r_height/2 + r_offset,
            self._width*xfactor + r_width/2,
            self._height*yfactor + r_height/2 + r_offset,
            fill=bg, outline='grey'
        )
        # the digital readout
        self._canvas.create_text(
            self._width * xfactor, self._height * yfactor - text_offset,
            font=(self.font, font_size), text=self._label)

        value_text = f"{EngUnit(value)}{self._unit}"
        self._canvas.create_text(
            self._width * xfactor, self._height * yfactor+ r_offset,
            font=(self.font, font_size), text=value_text, fill='white')

    def set_value(self, value):
        self._value = value
        if self._min_value * 1.02 < value < self._max_value * 0.98:
            self._adjust_gauge()
            self._redraw()      # refresh all
        else:                   # OFF limits refresh only readout
            self.readout(self._value, 'red')  # on RED BackGround
    
    def _adjust_gauge(self):
        '''
        Auto-adjust the upper limit of the gauge.
        When the needle approaches 90% of the upper limit or 
        10% of lower limit, upper or lower limit are shifted 
        by a decade respectively. 
        '''
        scale = 10 # change this scale the gauge by a different factor
        if self._value < self._lower_lim:
            self._max_value =  self._max_value / scale
        elif self._value > self._upper_lim:
            self._max_value = self._max_value * scale
        else:
            pass
        self._average_value = (self._max_value + self._min_value) / 2
        self._upper_lim = self._max_value * (1-self._reset_when)
        self._lower_lim = self._max_value * self._reset_when
