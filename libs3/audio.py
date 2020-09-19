
#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Audio Spectrum analyser
v0.7.0

- summed given fft in n bands, but re normalized between 0 - 70? 
- Peaks L and R
- amplitude for given target frequency and PEAK frequency
- "music note" to given frequency
- Real FFT, Imaginary FFT, Real + imaginary FFT
- threshold detection

todo :


by Sam Neurohack 
from /team/laser

for python 2 & 3

Stereo : CHANNELS = 2
mono : CHANNELS = 1

"""


import numpy as np
import pyaudio
from math import log, pow

#import matplotlib.pyplot as plt

#from scipy.interpolate import Akima1DInterpolator
#import matplotlib.pyplot as plt

DEVICE = 3
CHANNELS = 2
START = 0
RATE = 44100 # time resolution of the recording device (Hz)
CHUNK = 4096 # number of data points to read at a time. Almost 10 update/second
TARGET = 2100 # show only this one frequency


A4 = 440
C0 = A4*pow(2, -4.75)
name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
data = []

p = pyaudio.PyAudio() # start the PyAudio class
stream = p.open(format = pyaudio.paInt16, channels = CHANNELS, input_device_index = DEVICE, rate=RATE, input=True,
              frames_per_buffer=CHUNK) #uses default input device


#
# Audio devices & audiogen functions
#

def list_devices():
    # List all audio input devices
    p = pyaudio.PyAudio()
    i = 0
    n = p.get_device_count()
    print((n,"devices found"))
    while i < n:
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print((str(i)+'. '+dev['name']))
        i += 1


def valid_input_devices(self):
        """
        See which devices can be opened for microphone input.
        call this when no PyAudio object is loaded.
        """
        mics=[]
        for device in range(self.p.get_device_count()):
            if self.valid_test(device):
                mics.append(device)
        if len(mics)==0:
            print("no microphone devices found!")
        else:
            print(("found %d microphone devices: %s"%(len(mics),mics)))
        return mics



def loop():
    try:

        #plt.ion()
        
        #plt.axis([x[0], x[-1], -0.1, max_f])
        fftbands = [0,1,2,3,4,5,6,7,8,9]
        plt.xlabel('frequencies')
        plt.ylabel('amplitude')
        data = audioinput()
        drawfreq, fft = allfft(data)
        #lines = plt.plot(drawfreq, fft)

        #plt.axis([drawfreq[0], drawfreq[-1], 0, np.max(fft)])
        #plt.plot(drawfreq, fft)
        #plt.show()
        #line, = plt.plot(fftbands, levels(fft,10))
        line, = plt.plot(drawfreq, fft)
        #while True :
        for i in range(50):
        
            data = audioinput()
            
            # smooth the FFT by windowing data
            #data = data * np.hanning(len(data)) 
            
            # conversion to -1 to +1
            # normed_samples = (data / float(np.iinfo(np.int16).max))

            # Left is channel 0
            dataL = data[0::2]
            # Right is channel 1
            dataR = data[1::2]

            # Peaks L and R
            peakL = np.abs(np.max(dataL)-np.min(dataL))/CHUNK
            peakR = np.abs(np.max(dataR)-np.min(dataR))/CHUNK
            # print(peakL, peakR)

            drawfreq, fft = allfft(data)
            #fft, fftr, ffti, fftb, drawfreq = allfft(data)
            
            #line.set_ydata(levels(fft,10))
            line.set_ydata(fft)
            plt.pause(0.01)
            #print(drawfreq)
            #print(fft)
            #print (levels(fft,10))
 
            #line.set_ydata(fft)
            #plt.pause(0.01) # pause avec duree en secondes

            # lines = plt.plot(x, y)
            #lines[0].set_ydata(fft)
            #plt.legend(['s=%4.2f' % s])
            #plt.draw()
            #plt.show()

        

            '''
            targetpower,freqPeak = basicfft(audioinput(stream))
            print("amplitude", targetpower, "@", TARGET, "Hz")
            if freqPeak > 0.0:
                print("peak frequency: %d Hz"%freqPeak, pitch(freqPeak))
            '''
        plt.show()

    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()

    print("End...")

# Close properly
def close():
        stream.stop_stream()
        stream.close()
        p.terminate()


# Return "music note" to given frequency
def pitch(freq):
    h = round(12*(log(freq/C0)/log(2)))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)


# Return summed given fft in n bands, but re normalized 0 - 70 
def levels(fourier, bands):

    size = int(len(fourier))
    levels = [0.0] * bands

    # Add up for n bands
    # remove normalizer if you want raw added data in all bands
    normalizer = size/bands
    #print (size,bands,size/bands)
    levels = [sum(fourier[I:int(I+size/bands)])/normalizer for I in range(0, size, int(size/bands))][:bands]
    
    for band in range(bands):
        if levels[band] == np.NINF:
            levels[band] =0
    

    return levels


# read CHUNK size in audio buffer
def audioinput():

    # When reading from our 16-bit stereo stream, we receive 4 characters (0-255) per
    # sample. To get them in a more convenient form, numpy provides
    # fromstring() which will for each 16 bits convert it into a nicer form and
    # turn the string into an array.
    return np.fromstring(stream.read(CHUNK),dtype=np.int16)

# power for given TARGET frequency and PEAK frequency
# do fft first. No conversion in 'powers'
def basicfft(data):

    #data = data * np.hanning(len(data)) # smooth the FFT by windowing data
    fft = abs(np.fft.fft(data).real)
    #fft = 10*np.log10(fft)
    fft = fft[:int(len(fft)/2)]             # first half of fft

    freq = np.fft.fftfreq(CHUNK,1.0/RATE)
    freq = freq[:int(len(freq)/2)]          # first half of FFTfreq 

    assert freq[-1]>TARGET, "ERROR: increase chunk size"

    # return power for given TARGET frequency and peak frequency
    return fft[np.where(freq > TARGET)[0][0]],  freq[np.where(fft == np.max(fft))[0][0]]+1
    

# todo : Try if data = 1024 ?
# in "power' (0-70?) get Real FFT, Imaginary FFT, Real + imaginary FFT
def allfft(data):

    #print ("allfft", len(data))
    fft = np.fft.fft(data)
    #print("fft",len(fft))
    fftr = 10*np.log10(abs(fft.real))[:int(len(data)/2)]
    ffti = 10*np.log10(abs(fft.imag))[:int(len(data)/2)]
    fftb = 10*np.log10(np.sqrt(fft.imag**2+fft.real**2))[:int(len(data)/2)]
    #print("fftb",len(fftb))
    drawfreq = np.fft.fftfreq(np.arange(len(data)).shape[-1])[:int(len(data)/2)]
    drawfreq = drawfreq*RATE/1000 #make the frequency scale
    #return fft, fftr, ffti, fftb, drawfreq
    return drawfreq, fftb

    # Draw Original datas 
    # X : np.arange(len(data))/float(rate)*1000
    # Y : data
    
    # Draw real FFT 
    # X : drawfreq
    # Y : fftr
    
    # Draw imaginary 
    # X : drawfreq
    # Y : ffti

    # Draw Real + imaginary  
    # X : drawfreq
    # Y : fftb


# True if any value in the data is greater than threshold and after a certain delay 
def ding(right,threshold):
    if max(right) > threshold and time.time() - last_run > min_delay:
        return True
    else:
        return False
    last_run = time.time()


if __name__ == "__main__":
    
    
    loop()
'''
x = np.linspace(0, 3, 100)
k = 2*np.pi
w = 2*np.pi
dt = 0.01

t = 0
for i in range(50):
    y = np.cos(k*x - w*t)
    if i == 0:
        line, = plt.plot(x, y)
    else:
        line.set_ydata(y)
    plt.pause(0.01) # pause avec duree en secondes
    t = t + dt

plt.show()
'''

