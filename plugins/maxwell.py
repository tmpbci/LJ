#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''

Maxwell
v0.1.0

This client uses the relative drawing functions (rpolyline) -> your coordinates must be centered around 0,0. 

- Mixer :
    LRmixer : right curve percent
    LRtype  : "add", "minus", "multiply"

- points numbers

- Curve objects : required parameters :
    name, curvetype, freqlimit, freq, inversion

- Scaler :
    Everything is resize by a constant

- Translator :
    translations X Y Z by a constant

- Rotator :
    rotations X Y Z by a constant

- Duplicator : duplicators, duplicatorsAngle
    Duplicators are extra rpolyline with Angle added as global rotation parameter along *all* axis, this need to be checked conceptually


TODO :

- in Curve Objects :
    amptype, amp, phasemodtype, phasemodspeed, phasemodspeed, phaseoffsettype, phaseoffset

- Other functions for lfos, translator, rotator, scaler, duplicator,...
- CC inputs for all parameters



LICENCE : CC

by Sam Neurohack

'''
import sys
import os
print()
ljpath = r'%s' % os.getcwd().replace('\\','/')

# import from shell

sys.path.append(ljpath +'/../libs/')

#import from LJ
sys.path.append(ljpath +'/libs/')
print ('Maxwell plugin startup')

import lj23 as lj
sys.path.append('../libs')
from OSC3 import OSCServer, OSCClient, OSCMessage
import redis
import socketserver
import math
import time
import argparse
import numpy as np
import weakref
from math import pi as PI
import scipy.signal as signal
import midi3


OSCinPort = 8012
#oscrun = True
# myIP = "127.0.0.1"
PL = 0

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Text Cycling for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-l","--laser",help="Laser number to be displayed (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)

args = argsparser.parse_args()


if args.client:
    ljclient = args.client
else:
    ljclient = 0

if args.laser:
    plnumber = args.laser
else:
    plnumber = 0

# Redis Computer IP
if args.redisIP  != None:
    redisIP  = args.redisIP
else:
    redisIP = '127.0.0.1'

print("redisIP",redisIP)

# myIP
if args.myIP  != None:
    myIP  = args.myIP
else:
    myIP = '127.0.0.1'

print("myIP",myIP)

if args.verbose:
    debug = args.verbose
else:
    debug = 0


lj.Config(redisIP,ljclient,"maxw")

white = lj.rgb2int(255,255,255)
red = lj.rgb2int(255,0,0)
blue = lj.rgb2int(0,0,255)
green = lj.rgb2int(0,255,0)

points = 512
# maxpoints = 500
samples = points
samparray = [0] * samples

# Channel 1 midi CC
cc1 = [0]*127
# Channel 2 midi CC
cc2 = [0]*127

# Mixer
LRmixer = 0
LRtype = 'minus'          # "minus", 'multiply'

# Duplicators
duplicators = 1
duplicatorsAngle = 30

Oscillators = []
LFOs = []
Rotators = []
Translators = []


width = 800
height = 600
centerX = width / 2
centerY = height / 2

# 3D to 2D projection parameters
fov = 256
viewer_distance = 2.2


# Anaglyph computation parameters for right and left eyes.
eye_spacing = 100
nadir = 0.5
observer_altitude = 30000
#observer_altitude = 10000
# elevation = z coordinate
# 0.0, -2000 pop out
map_plane_altitude = 0.0

# Relative Object (name, active, intensity, xy, color, red, green, blue, PL , closed, xpos , ypos , resize , rotx , roty , rotz)
#Leftshape = lj.RelativeObject('Leftshape', True, 255, [], red, 255, 0, 0, PL , True, 100 , 100 , 1 , 0 , 0 , 0)


#                           name, intensity, active, xy, color, red, green, blue, PL , closed):
Leftshape = lj.FixedObject('Leftshape', True, 255, [], red, 255, 0, 0, PL , False)
#Rightshape = lj.FixedObject('Rightshape', True, 255, [], green, 0, 255, 0, PL , False)

# 'Destination' for each PL 
#                  name, number, active, PL , scene, laser
# PL 0
Dest0 = lj.DestObject('0', 0, True, 0 , 0, 0)
#Dest1 = lj.DestObject('1', 1, True, 0 , 1, 1)

'''
viewgen3Lasers = [True,False,False,False]
# Add here, one by one, as much destination as you want for each PL. 
# LJ and OSC can remotely add/delete destinations here.

lj.Dests = {
    "0":       {"PL": 0, "scene": 0, "laser": 0},
    "1":       {"PL": 0, "scene": 1, "laser": 1}
    }

'''


#
# OSC
#

oscserver = OSCServer( (myIP, OSCinPort) )
oscserver.timeout = 0

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# OSC callbacks

# /viewgen/ljclient
def OSCljclient(path, tags, args, source):

    print("Got /viewgen/ljclient with values", args[0])
    lj.WebStatus("viewgen to virtual "+ str(args[0]))
    ljclient = args[0]
    lj.LjClient(ljclient)


# /noteon note velocity
def OSCnoteon(path, tags, args, source):

    note = args[0]
    velocity = args[1]
    # Do something with it

# /noteoff note
def OSCnoteoff(path, tags, args, source):

    note = args[0]
    # Do something with it

# /cc number value
def OSCcc(path, tags, args, source):

    cc1[args[0]]= args[1]
    #cc = args[0]
    #value = args[1]

#
# CC functions
#

# /cc cc number value
def cc(ccnumber, value):

    if ccnumber > 127:
        cc2[ccnumber - 127]= value
    else:
        midichannel = basemidichannel
        cc1[ccnumber]= value

    #print("Sending Midi channel", midichannel, "cc", ccnumber, "value", value)
    #midi3.MidiMsg([CONTROLLER_CHANGE+midichannel-1,ccnumber,value], learner)


def FindCC(FunctionName):

    for Maxfunction in range(len(maxwell['ccs'])):
        if FunctionName == maxwell['ccs'][Maxfunction]['Function']:
            #print(FunctionName, "is CC", Maxfunction)
            return Maxfunction


def LoadCC():
    global maxwell

    print("Loading Maxwell CCs Functions...")
    f=open("maxwell.json","r")
    s = f.read()
    maxwell = json.loads(s)
    print(len(maxwell['ccs']),"Functions")
    print("Loaded.")


def SendCC(path,init):

    funcpath = path.split("/")
    func = funcpath[len(funcpath)-1]
    if func in specificvalues:
        value = specificvalues[func][init]
    else:
        value  = int(init)

    #print("sending CC", FindCC(path), "with value", value)
    cc(FindCC(path),value)
    time.sleep(0.005)


#
# computing functions
# 

def ssawtooth(samples, freq, phase):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.sawtooth(2 * np.pi * freq * t[ww])
    return samparray

def ssquare(samples, freq, phase):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.square(2 * np.pi * freq * t[ww])
    return samparray

def ssine(samples, freq, phase):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = np.sin(2 * np.pi * freq  * t[ww])
    return samparray

'''
def sline(samples, 1):

    samparray = [0] * samples
    for ww in range(samples):
        samparray[ww] = ww
    return samparray
'''

def slinear(samples, min, max):

    samparray = [0] * samples
    linearinc = (max-min)/samples
    for ww in range(samples):
        if ww == 0:
            samparray[ww] = min
        else:
            samparray[ww] = samparray[ww-1] + linearinc
    #print('linear min max', min, max)
    #print ('linear',samparray)
    return samparray

def sconstant(samples, values):

    samparray = [0] * samples
    for ww in range(samples):
        samparray[ww] = values
    return samparray

def remap(s,min1,max1, min2, max2):
    a1, a2 = min1, max1  
    b1, b2 = min2, max2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def cc2range(s,min,max):
    a1, a2 = 0,127  
    b1, b2 = min, max
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def range2cc(s,min,max):
    a1, a2 = min, max
    b1, b2 = 0,127
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def LeftShift(elevation):

            diff = elevation - map_plane_altitude
            return nadir * eye_spacing *  diff / (observer_altitude - elevation)

def RightShift(elevation):

            diff = map_plane_altitude - elevation
            return (1 - nadir) * eye_spacing * diff / (observer_altitude - elevation)

def Proj(x,y,z,angleX,angleY,angleZ):

        rad = angleX * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        y2 = y
        y = y2 * cosa - z * sina
        z = y2 * sina + z * cosa
        
        rad = angleY * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        z2 = z
        z = z2 * cosa - x * sina
        x = z2 * sina + x * cosa

        rad = angleZ * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        x2 = x
        x = x2 * cosa - y * sina
        y = x2 * sina + y * cosa

        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = fov / (viewer_distance + z)
        x = x * factor + centerX
        y = - y * factor + centerY
        return (x,y)


#
# Main Oscillators
#

specificvalues = {
    "sine":  0,
    "saw":  33,
    "square":  95,
    "linear":  127,
    "constant" : 128,
    "1":  0,
    "4":  26,
    "16":  52,
    "32":  80,
    "127":  127,
    "solid":  0,
    "lfo":  127,
    "off":  0,
    "on":  127,
    "add":  0,
    "minus":  50,
    "multiply":  127,
    "lfo1":  33,
    "lfo2":  95,
    "lfo3":  127,
    "manual": 0,
    }

'''
"colormodtype": {
    "sin":  0,
    "linear":  127
    }
'''
# return v1,v2,v3 or v4 according to "value" 0-127
def vals4(value,v1,v2,v3,v4):
    if value < 32:
        return v1
    if value > 31 and value < 64:
        return v2
    if value > 61 and value < 96:
        return v3
    if value > 95:
        return v4

# return v1,v2,v3,v4 or v5 according to "value" 0-127
def vals5(value,v1,v2,v3,v4,v5):
    if value < 26:
        return v1
    if value > 25 and value < 52:
        return v2
    if value > 51 and value < 80:
        return v3
    if value > 79 and value < 104:
        return v4
    if value > 104:
        return v5


class OsciObject:

    _instances = set()
    counter = 0
    kind = 'fixed'

    def __init__(self, name, curvetype, amp, inversion, baseCC):
      
        self.name = name
        self.baseCC = baseCC
        
        # Amplitude 64 values positive and 64 values negative -256 to +256
        self.amp = amp
        # curvetypes : sine, saw, square, linear, constant ?
        self.curvetype = curvetype
        self.freqlimit = 4
        # Curvetype frequency : 128 possible values between 1 - freqlimit
        self.freq = 2
        # Amplitude Curvetype : constant, lfo1, lfo2, lfo3
        self.amptype = 'constant'

        # Phase modification type : linear or sine.
        self.phasemodtype = 'linear'
        # Phase modification 64 speed forward and 64 speed backward.
        # Speed is increment browsing 
        self.phasemodspeed = 1
        #self.phasemodspeed = 0

        self.phaseoffsettype = 'manual'
        self.phaseoffset = 200

        self.ampoffset = cc2range(cc1[self.baseCC + 9],0,32)
        self.ampoffsettype = cc1[self.baseCC + 10]

        self.inversion = inversion

        self.phasemodcurve = [0]*points  # ssine(points, self.freq, self.phasemodspeed)
        self.phaseoffsetcurve = ssine(points, self.freq, self.phasemodspeed)
        self.values = ssine(points, self.freq, self.phasemodspeed)
        self.counter = 0

        self.samples = samples

        self._instances.add(weakref.ref(self))
        OsciObject.counter += 1

        # print(self.name, "kind", self.kind, "port", self.port)

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def __del__(self):
        OsciObject.counter -= 1


    def CC2VAR(self):

        if cc1[self.baseCC] == 128:
            self.curvetype = "constant"
        else:
            self.curvetype = vals4(cc1[self.baseCC], "sine", "saw","square","linear")

        self.freqlimit = vals5(cc1[self.baseCC + 2],"1","4","16","32","127")
        self.freq = cc2range(cc1[self.baseCC + 1], 0, self.freqlimit)
        self.amptype = vals4(cc1[self.baseCC + 4], "constant", "lfo1","lfo2","lfo3") 
        self.amp = cc2range(cc1[self.baseCC + 3] , -256, 256)

        if cc1[self.baseCC]+ 6 < 64:
            self.phasemodtype = "linear"
        else:
            self.phasemodtype ="sine"

        # phasemodspeed : 0 to 32 ?, because why not 32 ? to test.
        self.phasemodspeed = cc2range(cc1[self.baseCC + 5], 0, 32)
        self.phaseoffsettype = vals4(cc1[self.baseCC + 8], "manual", "lfo1","lfo2","lfo3")
        # phaseoffset : between 0 to 10 ?
        self.phaseoffset = cc2range(cc1[self.baseCC + 7], 0, 10)

        self.ampoffsettype = vals4(cc1[self.baseCC + 10], "manual", "lfo1","lfo2","lfo3") 
        # ampoffset : between 0 to 10 ?
        self.ampoffset = cc2range(cc1[self.baseCC + 9], 0, 10)

        self.inversion = cc1[self.baseCC + 11]

    def VAR2CC(self):

        '''
        /osc/left/X/curvetype is Artnet 0  MIDI Channel 1 CC 0          "sine"/0 - "saw"/33 - "square"/95 - "linear"/127 - "constant"/128
        /osc/left/X/freq is Artnet 1  MIDI Channel 1 CC 1               0 - freqlimit
        /osc/left/X/freqlimit is Artnet 2  MIDI Channel 1 CC 2          "1"/0 - "4"/26 - "16"/52 - "32"/80 - "127"/127
        /osc/left/X/amp is Artnet 3  MIDI Channel 1 CC 3                0/-256 - 127/256
        /osc/left/X/amptype is Artnet 4  MIDI Channel 1 CC 4            "constant"/0 - "lfo1"/33 - "lfo2"/95 - "lfo3"/127
        /osc/left/X/phasemodspeed is Artnet 5  MIDI Channel 1 CC 5      0 - 32 ?
        /osc/left/X/phasemodtype is Artnet 6  MIDI Channel 1 CC 6 :     "linear"/ - "sin"/
        /osc/left/X/phaseoffset is Artnet 7  MIDI Channel 1 CC 7        0 - 10 ?
        /osc/left/X/phaseoffsettype is Artnet 8  MIDI Channel 1 CC 8    "manual"/0 - "lfo1"/33 - "lfo2"/95 - "lfo3"/127
        /osc/left/X/ampoffset is Artnet 9  MIDI Channel 1 CC 9          0 - 10 ?
        /osc/left/X/ampoffsettype is Artnet 10  MIDI Channel 1 CC 10    "manual"/0 - "lfo1"/33 - "lfo2"/95 - "lfo3"/127
        /osc/left/X/inversion is Artnet 11  MIDI Channel 1 CC 11 :      "off"/0 - "on"/127
        '''
  
        cc1[self.baseCC + 3] = range2cc(self.amp, -256, 256) 
        cc1[self.baseCC] = specificvalues[self.curvetype]
        cc1[self.baseCC + 2] = specificvalues[str(self.freqlimit)]
        cc1[self.baseCC + 1] = range2cc(self.freq, 0, self.freqlimit) 
        if self.amptype == 'constant':
            cc1[self.baseCC + 4] = 0
        else:
            cc1[self.baseCC + 4] = specificvalues[self.amptype]

        # Phase modification type : linear or sine.
        if self.phasemodtype == 'linear':
            cc1[self.baseCC + 6] = 0
        else:
            cc1[self.baseCC + 6] = 90
        cc1[self.baseCC + 5] = range2cc(self.phasemodspeed, 0, 32)

        # Phase offset
        cc1[self.baseCC + 8] = specificvalues[self.phaseoffsettype]
        cc1[self.baseCC + 7] = range2cc(self.phaseoffset, 0, 10)

        # Amp offset
        cc1[self.baseCC + 9] = range2cc(self.ampoffset, 0, 10)
        cc1[self.baseCC + 10] = specificvalues[self.ampoffsettype]

        if self.inversion == True:
            cc1[self.baseCC + 11] = 127
        else:
            cc1[self.baseCC + 11] = 0


    def Curve(self):

        self.values = [0] * points
        self.ampcurve = [0] * points
        self.phasemodcurve = [0] * points
        self.phaseoffsetcurve = [0] * points

        self.counter += 1
        #print ('counter', self.counter)
        if self.counter == points:
            self.counter = 0
        # Phase offset curve
        #self.phasemodcurve = slinear(points, -PI, PI)  # ssine(points, self.freq, self.phasemodspeed)
        if self.phaseoffsettype == 'manual':
            self.phaseoffsetcurve = sconstant(points, self.phaseoffset)

        if self.phaseoffsettype == 'lfo1':
            self.phaseoffsetcurve = lfo1.Curve()

        if self.phaseoffsettype == 'lfo2':
            self.phaseoffsetcurve = lfo2.Curve()

        if self.phaseoffsettype == 'lfo3':
            self.phaseoffsetcurve = lfo3.Curve()

        
        # Phase mod curve : phasemodspeed is 'speed' of change
        if self.phasemodtype == 'linear':
            self.phasemodcurve = slinear(points, -PI*self.phasemodspeed, PI*self.phasemodspeed)

        if self.phasemodtype == 'lfo1':
            self.phasemodcurve = lfo1.Curve()

        if self.phasemodtype == 'lfo2':
            self.phasemodcurve = lfo2.Curve()

        if self.phasemodtype == 'lfo3':
            self.phasemodcurve = lfo3.Curve()

        self.phasemodspeed = self.phasemodcurve[self.counter]
        #print('counter', self.counter, 'phasemod',self.phasemodspeed)

        #  Base values curve, trigo functions between -1 and + 1
        if self.curvetype == 'sine':
            self.ampcurve = ssine(points, self.freq, self.phasemodspeed)

        if self.curvetype == 'saw':
            self.ampcurve = ssawtooth(points, self.freq, self.phasemodspeed)

        if self.curvetype == 'square':
            self.ampcurve = ssquare(points, self.freq, self.phasemodspeed)

        if self.curvetype == 'linear':
            self.ampcurve = slinear(points, -1, 1)

        if self.curvetype == 'constant':
            self.ampcurve = sconstant(points, self.freq)


        for point in range(points):

            # curve points = base curve * amp + curve modifier
            if self.amptype == 'constant':
                self.values[point] = self.ampcurve[point] * self.amp

            if self.amptype == 'lfo1':
                self.values[point] = (self.ampcurve[point] * self.amp) + (lfo1.values[point] * self.amp) 

            if self.amptype == 'lfo2':
                self.values[point] = (self.ampcurve[point] * self.amp) + (lfo2.values[point] * self.amp) 

            if self.amptype == 'lfo3':
                self.values[point] = (self.ampcurve[point] * self.amp) + (lfo3.values[point] * self.amp)

        if self.inversion == True:
            self.values = self.values[::-1]

#
# LFOs
#

class LFObject:

    _instances = set()
    counter = 0
    kind = 'fixed'

    def __init__(self, name):

        self.name = name
        self.freqlimit = 4
        self.freq = 1
        self.curvetype = 'sine'
        # -1  1
        self.phasemodspeed = 0
        self.inversion = False
        self.values = ssine(points, self.freq, self.phasemodspeed)

        self._instances.add(weakref.ref(self))
        LFObject.counter += 1

        #print(self.name, "type", self.curvetype, "freq", self.freq)

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def Curve(self):

        #print(self.name, "type", self.curvetype, "freq", self.freq)
        self.values = [0]*points
        if self.curvetype == 'sine':
            self.values = ssine(points, self.freq, self.phasemodspeed)

        if self.curvetype == 'saw':
            self.values = ssawtooth(points, self.freq, self.phasemodspeed)

        if self.curvetype == 'square':
            self.values = ssquare(points, self.freq, self.phasemodspeed)

        if self.curvetype == 'linear':
            self.values = slinear(points, self.freq)

        if self.curvetype == 'constant':
            self.values = sconstant(points, self.freq)

        if self.inversion == True:
            self.values = self.values[::-1]

    def __del__(self):
        LFObject.counter -= 1

#
# Rotators
#

class RotatorObject:  

    '''
    # anim format (name, xpos, ypos, resize, currentframe, totalframe, count, speed)
    #               0     1     2      3           4           5         6      7
    # total frames is fetched from directory by lengthPOSE()
    #anims[0] = ['boredhh' , xy_center[0] - 100, xy_center[1] + 30, 550, 0, 0, 0, animspeed]
    anim[4] = anim[4]+anim[7]
    if anim[4] >= anim[5]:
        anim[4] = 0
    '''

    _instances = set()
    counter = 0
    kind = 'fixed'

    def __init__(self, name):
        
        self.name = name
        self.curvetype = 'constant'
        self.speed = 0
        self.lfo = False
        self.direction = 0

        self._instances.add(weakref.ref(self))
        RotatorObject.counter += 1


    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def __del__(self):
        RotatorObject.counter -= 1

    def Curve(self):

        self.values = [0]*points

        if self.curvetype == 'sine':
            self.values = ssine(points, self.direction, self.phasemodspeed)

        if self.curvetype == 'saw':
            self.values = ssawtooth(points, self.direction, self.phasemodspeed)

        if self.curvetype == 'square':
            self.values = ssquare(points, self.direction, self.phasemodspeed)

        if self.curvetype == 'linear':
            self.values = slinear(points, self.direction)

        if self.curvetype == 'constant':
            self.values = sconstant(points, 0)

#
# Translators
#

class TranslatorObject:

    _instances = set()
    counter = 0
    kind = 'fixed'

    def __init__(self, name, amt, speed):

        self.name = name
        self.curvetype = 'constant'
        self.speed = speed
        self.lfo = False
        self.amt = amt
        #self.values =  ssine(points, self.amt, self.speed)
        self.values = sconstant(points, self.amt)
        
        self._instances.add(weakref.ref(self))
        TranslatorObject.counter += 1

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    def __del__(self):
        TranslatorObject.counter -= 1

    def Curve(self):

        self.values = [0]*points

        if self.curvetype == 'sine':
            self.values = ssine(points, self.amt, self.speed)

        if self.curvetype == 'saw':
            self.values = ssawtooth(points, self.amt, self.speed)

        if self.curvetype == 'square':
            self.values = ssquare(points, self.amt, self.speed)

        if self.curvetype == 'linear':
            self.values = slinear(points, self.amt)

        if self.curvetype == 'constant':
            self.values = sconstant(points, self.amt)

#
# Scaler
#

Scalercurvetype = 'constant'
Scalercurve = [0.05] * points
Scalerspeed = 0
Scalerbutton = False
Scalerwidth = 0
Scaleramt = 0


def ScalerCurve():

    Scalercurve = [0]*points

    if Scalercurvetype == 'sine':
        Scalercurve = ssine(points, Scaleramt, Scalerspeed)

    if Scalercurvetype == 'saw':
        Scalercurve = ssawtooth(points, Scaleramt, Scalerspeed)

    if Scalercurvetype == 'square':
        Scalercurve = ssquare(points, Scaleramt, Scalerspeed)

    if Scalercurvetype == 'linear':
        Scalercurve = slinear(points, Scaleramt)

    if Scalercurvetype == 'constant':
        Scalercurve = sconstant(points, 0.05)

#
# Main
#

def Run():

    Left = []
    Right = []
    counter =0
    lj.WebStatus("Maxwellator")
    lj.SendLJ("/maxw/start 1")

    # OSC
    # OSC Server callbacks
    print("Starting OSC server at",myIP," port",OSCinPort,"...")
    oscserver.addMsgHandler( "/maxw/ljclient", OSCljclient )

    # You will receive midi callbacks in OSC messages form if this plugin is in midi2OSC list in midi3.py and midi3.py is imported somewhere 
    oscserver.addMsgHandler( "/noteon", OSCnoteon)
    oscserver.addMsgHandler( "/noteoff", OSCnoteoff)
    oscserver.addMsgHandler( "/cc", OSCnoteon)
    # Add OSC generic plugins commands : 'default", /ping, /quit, /pluginame/obj, /pluginame/var, /pluginame/adddest, /pluginame/deldest
    lj.addOSCdefaults(oscserver)


    # Drawing parameters
    # LFOs
    lfo1 = LFObject("lfo1")
    lfo2 = LFObject("lfo2")
    lfo3 = LFObject("lfo3")

    # Rotators
    rotX = RotatorObject("rotX")
    rotY = RotatorObject("rotY")
    rotZ = RotatorObject("rotZ")

    # Translators : name amount speed
    transX = TranslatorObject("transX",0,0)
    transY = TranslatorObject("transY",0,0)
    transZ = TranslatorObject("transZ",0,0)

    Scaler =  ScalerCurve() 

    # Left parameters : name, type, amp, inversion, base midi CC
    leftX = OsciObject("leftX", "sine", 30, False, 0)
    leftY = OsciObject("leftY", "sine", 30, True, 12)
    leftZ = OsciObject("leftZ", "constant", 0, False, 24)

    # Right parameters : name, type, amp, inversion, base midi CC
    rightX = OsciObject("rightX", "saw", 30, False, 36)
    rightY = OsciObject("rightY", 'saw', 30, True, 48)
    rightZ = OsciObject("rightZ", 'constant', 0, False, 60)

    try:

        while lj.oscrun:

            lj.OSCframe()

            Left = []
            Right = []

            lfo1.Curve()
            lfo2.Curve()
            lfo3.Curve()
            
            transX.Curve()
            transY.Curve()
            transZ.Curve()

            rotX.Curve()
            rotY.Curve()
            rotZ.Curve()

            leftX.Curve()
            leftY.Curve()
            leftZ.Curve()

            rightX.Curve()
            rightY.Curve()
            rightZ.Curve()

            for point in range(points):

                if LRtype == 'add':

                    CurveX = (leftX.values[point]*(100-LRmixer)/100) + (rightX.values[point]*LRmixer/100) + transX.values[point]
                    CurveY = (leftY.values[point]*(100-LRmixer)/100) + (rightY.values[point]*LRmixer/100) + transY.values[point]
                    CurveZ = (leftZ.values[point]*(100-LRmixer)/100) + (rightZ.values[point]*LRmixer/100) + transZ.values[point]

                if LRtype == 'minus':

                    CurveX = (leftX.values[point]*(100-LRmixer)/100) - (rightX.values[point]*LRmixer/100) + transX.values[point]
                    CurveY = (leftY.values[point]*(100-LRmixer)/100) - (rightY.values[point]*LRmixer/100) + transY.values[point]
                    CurveZ = (leftZ.values[point]*(100-LRmixer)/100) - (rightZ.values[point]*LRmixer/100) + transZ.values[point]

                if LRtype == 'multiply':

                    CurveX = (leftX.values[point]*(100-LRmixer)/100) * (rightX.values[point]*LRmixer/100) + transX.values[point]
                    CurveY = (leftY.values[point]*(100-LRmixer)/100) * (rightY.values[point]*LRmixer/100) + transY.values[point]
                    CurveZ = (leftZ.values[point]*(100-LRmixer)/100) * (rightZ.values[point]*LRmixer/100) + transZ.values[point]

    
                Left.append(Proj(CurveX+LeftShift(CurveZ*25), CurveY, CurveZ, 0, 0, 0))
                #Right.append(Proj(CurveX+RightShift(CurveZ*25), CurveY, CurveZ, 0, 0, 0))    
    
            for clone in range(duplicators):
     
                # Drawing step, 2 possibilities 
                # Red and Green drawn by laser 0
                lj.rPolyLineOneColor(Left, c = Leftshape.color , PL = Leftshape.PL, closed = Leftshape.closed, xpos = 350, ypos = 350, resize = Scalercurve[0], rotx = rotX.values[0] + (clone * duplicatorsAngle), roty = rotY.values[0] + (clone * duplicatorsAngle), rotz = rotZ.values[0] + (clone * duplicatorsAngle))
                #lj.PolyLineOneColor(Right, c = Rightshape.color , PL = Rightshape.PL, closed = Rightshape.closed)

                #lj.DrawPL(PL)
            lj.DrawDests()

            
            time.sleep(0.01)
    
            counter += 1
            if counter > 360:
                counter = 0

    except KeyboardInterrupt:
        pass

    # Gently stop on CTRL C

    finally:

        lj.ClosePlugin()


Run()
