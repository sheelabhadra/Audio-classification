# The code is written in Python3
# 
# install the pyaudio and pyqtgraph libraries-
# In the command window, type and run:
# 
# for pyqtgraph:
# sudo apt-get install python3-pyqtgraph
# 
# for pyaudio:
# sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
# sudo apt-get install ffmpeg libav-tools
# sudo apt-get install python3-pyaudio


import pyaudio
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 14100
CHUNK = 1024
MAX_PLOT_SIZE = CHUNK * 50

# setup audio recording
audio = pyaudio.PyAudio()

# Read the audio input
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

win = pg.GraphicsWindow()
win.setWindowTitle("Microphone Audio Data")

# create a plot for the time domain data
data_plot = win.addPlot(title="Audio Signal Vs Time")
data_plot.setXRange(0 ,MAX_PLOT_SIZE)
data_plot.setLabel(axis="bottom", text="Time(s)")
data_plot.setLabel(axis="left", text="Signal amplitude")
data_plot.showGrid(True, True)
data_plot.addLegend()
time_curve = data_plot.plot(pen=(24,215,248), name = "Time Domain Audio")

# create a plot for the frequency domain data
win.nextRow()
fft_plot = win.addPlot(title="Power Vs Frequency Domain") 
fft_plot.setLabel(axis="bottom", text="Frequency(Hz)")
fft_plot.setLabel(axis="left", text="Log Power")
fft_plot.addLegend()
fft_curve = fft_plot.plot(pen='y', name = "Power Spectrum")

fft_plot.showGrid(True, True)
total_data = []

# power-frequency graph x-axis
x_axis = RATE/CHUNK*np.linspace(0, CHUNK/2, CHUNK/2+1)

# for counting the time step
t = 1

# You can capture 5s clips of the data using the get_data() function. The data is updated after every 5 seconds.
# The format of the data is int16. You can directly apply FFT etc. on this data. You may go through the implementation of FFT below in the update() function to get an idea regarding how to use the data.
 
def get_data(total_data):
    print(max(total_data))

def update():
    global stream, total_data, max_hold, t
    
    # read data
    raw_data = stream.read(CHUNK)
    
    # convert raw bytes into integers
    data_sample = np.fromstring(raw_data, dtype=np.int16)
    total_data = np.concatenate([total_data, data_sample ])
    
    # remove old data
    if len(total_data) > MAX_PLOT_SIZE:
        total_data = total_data[CHUNK:]
    time_curve.setData(total_data)
    
    # calculate the FFT
    fft_data = data_sample * np.hanning(len(data_sample))
    power_spectrum = 20 * np.log10(np.abs(np.fft.rfft(fft_data))/len(fft_data))
    fft_curve.setData(x=x_axis, y=power_spectrum)
    
    if t == 50:
        get_data(total_data)
        t = 1
    t += 1
    
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

## Start Qt Event
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
