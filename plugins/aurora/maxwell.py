#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
maxwell interactive 

Quoi pour debut fin ?


LICENCE : CC
Sam Neurohack

 LINK

  - bpm 

  - beatnumber -> Event
 

 MIDI  

 - cc : channel = layer / ccnumber = steps / ccvalue = stepmax -> /maxwell/cc channel ccnumber ccvalue
 
 - notes

 if midi.sync :

 - midix.bpm
 
 - start -> /maxwell/start
 
 - stop  -> /maxwell/stop
 
 - clock -> /maxwell/clock


 OSC 

 - /maxwell/rawcc layer encoder value (to change given encoder parameter ie 0 = steps)

 - /maxwell/cc layer steps stepmax

 - /maxwell/fx/layernumber fxname ('ScanH', 'ScanV', 'Circle', 'Wave')

 - /maxwell/x/layernumber coord (0-1)
 - /maxwell/xcoord layernumber coord

 - /maxwell/y/layernumber coord (0-1)
 - /maxwell/ycoord layernumber coord

                        Scale 98
 - /maxwell/scale layer value

 - /maxwell/linesize layer value

 - /maxwell/color/layername colorname

                         X 100 Y 104 Z 108
 - /maxwell/rotspeed layernumber axe speed

                        X 114 Y 118 Z 122
 - /maxwell/transamt layernumber axe maxposition 

                        X 102 Y 106 Z 110
 - /maxwell/rotdirec layernumber axe rotdirec


 - /maxwell/bpm

 - /maxwell/clock

 - /maxwell/start

 - /maxwell/stop

 - /maxwell/noteon layer note velocity

 - /maxwell/noteoff layer note

 - /maxwell/part partname

 - /maxwell/intensity layernumber intensity

 - /maxwell/radius    layernumber value

 - /maxwell/type  layer side axe value
 - /maxwell/freq  layer side axe freq
 - /maxwell/amp  layer side axe amp
 - /maxwell/inv  layer side axe inv

 to code 

 /maxwell/scandots       layernumber value
 /maxwell/cu/freq        layernumber axe frequency
 /maxwell/cu/phaseoffset layernumber axe phaseoffset
 curvetype


mode ALIGN

mode LIVE

mode SONG


 trigger / layer / size / speed 
 trigger / layer / stepmax / steps
 
 Layer : Xsteps, Ysteps, Sizesteps, rotXsteps,...

'''


import math

import numpy as np
import pdb
from datetime import datetime
from random import randrange
import redis
import sys
import ast
import os
import time,traceback
import midix, anim

ljpath = r'%s' % os.getcwd().replace('\\','/')

# import from shell
sys.path.append(ljpath +'/../../libs/')
sys.path.append(ljpath +'/../libs/')

#import from LJ
sys.path.append(ljpath +'/libs/')

sys.path.append('../libs')
sys.path.append(ljpath +'/../../libs')

import gstt

is_py2 = sys.version[0] == '2'
if is_py2:
    from OSC import OSCServer, OSCClient, OSCMessage
else:
    from OSC3 import OSCServer, OSCClient, OSCMessage

import lj23layers as lj
import argparse

print ("")
print ("maxwell v0.1b")

OSCinPort = 8090

ljscene = 0

# Useful variables init.
white = lj.rgb2int(255,255,255)
red = lj.rgb2int(255,0,0)
blue = lj.rgb2int(0,0,255)
green = lj.rgb2int(0,255,0)
cyan = lj.rgb2int(255,0,255)
yellow = lj.rgb2int(255,255,0)

screen_size = [700,700]
xy_center = [screen_size[0]/2,screen_size[1]/2]

width = 800
height = 600
centerX = width / 2
centerY = height / 2

# 3D to 2D projection parameters
fov = 256
viewer_distance = 2.2

inv = math.pi/2

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="maxwell for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-s","--scene",help="LJ scene number (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)
argsparser.add_argument("-L","--Lasers",help="Number of lasers connected (1 by default).",type=int)
argsparser.add_argument('-song',help="Run according to external (LIVE is default)", dest='song', action='store_true')
argsparser.set_defaults(song=False)
argsparser.add_argument('-nolink',help="Disable Ableton Link (enabled by default)", dest='link', action='store_false')
argsparser.set_defaults(link=True)
args = argsparser.parse_args()


if args.verbose:
    debug = args.verbose
else:
    debug = 0

if args.scene:
    ljscene = args.scene
else:
    ljscene = 0

# Redis Computer IP
if args.redisIP  != None:
    redisIP  = args.redisIP
else:
    redisIP = '127.0.0.1'

# myIP
if args.myIP  != None:
    gstt.myIP  = args.myIP
else:
    gstt.myIP = '127.0.0.1'

# Lasers = number of laser connected
if args.Lasers  != None:
    gstt.lasernumber = args.Lasers
else:
    gstt.lasernumber = 1

# with Ableton Link
if args.link  == True:
    import alink

    alink.Start()
    linked = True
else:
    print("Link DISABLED")
    linked = False

# Mode song 
if args.song  == True:
    print("Mode SONG")
    mode = "song"
else:
    print("Mode LIVE")
    mode = "live"


lj.Config(redisIP, ljscene, "maxwell")


ccs =[[0] * 140] *4


# Animation parameters for each layer
Layer = [{'scandots': 10, 'mixer': 0, 'color': red, 'scale': 1,'intensity': 255}] * 3

LayerX = [{'coord': 250, 'rotspeed': 0, 'transpeed': 0, 'transamt': 250, "rotdirec": 0}] *3
LayerY = [{'coord': 250, 'rotspeed': 0, 'transpeed': 0, 'transamt': 250, "rotdirec": 0}] *3
LayerZ = [{'coord': 0,   'rotspeed': 0, 'transpeed': 0, 'transamt': 0,   "rotdirec": 0}] *3

# Maxwell Style
# sin:0/saw:33/squ:95/lin:127
CurveLX= [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3
CurveLY= [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': np.pi/2}] * 3
CurveLZ= [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3

CurveRX= [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3
CurveRY= [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3
CurveRZ= [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3


# Destination :           name, number, active, layer , scene, laser)
Dest000 = lj.DestObject('FX0', 0, True, 0 , 0, 0)
#Dest101 = lj.DestObject('FX1', 1, True, 1 , 0, 1)
#Dest202 = lj.DestObject('FX2', 2, True, 2 , 0, 2)

# RelativeObject              name, active, intensity, xy, color, red, green, blue, layer , closed, xpos , ypos , scale , rotx , roty , rotz
FX0Form = lj.RelativeObject('FX0', True, 255, [], Layer[0]['color'], 255, 0, 0, 0 , False, 250 , 250, 1 , 0 , 0 , 0)
FX1Form = lj.RelativeObject('FX1', True, 255, [], Layer[1]['color'], 255, 0, 0, 1 , False, 250 , 250, 1 , 0 , 0 , 0)
FX2Form = lj.RelativeObject('FX2', True, 255, [], Layer[2]['color'], 255, 0, 0, 2 , False, 250 , 250, 1 , 0 , 0 , 0)


#
# OSC
#

oscserver = OSCServer( (gstt.myIP, OSCinPort) )
oscserver.timeout = 0
#oscrun = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True


# funny python's way to add a method to an instance of a class
import types
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# /maxwell/ljscene
def OSCljscene(path, tags, args, source):

    print("maxwell OSC : got /maxwell/ljscene with value", args[0])
    lj.WebStatus("maxwell to virtual "+ str(args[0]))
    ljscene = args[0]
    lj.ljscene(ljscene)

# default handler
def OSChandler(path, tags, args, source):

    oscaddress = ''.join(path.split("/"))
    print("maxwell default OSC Handler from Client :" + str(source[0]),)
    print("OSC address", path)
    print('Incoming OSC with path', path[8:])
    if len(args) > 0:
        print("with args", args)

    # /maxwell/fx/layer FXname
    if path.find('/maxwell/fx') == 0:
        layer = int(path[11:12])
        fx = args[0]
        FXs[layer] = "anim."+fx
        print("maxwell OSC Got new OSC FX generator for layer", layer,":", FXs[layer])

    # /maxwell/color/layer colorname
    if path.find('/maxwell/color') == 0:

        if args[1] =='1':
            layer = int(path[14:15])
            color = args[0]
            print("color was",Layer[layer]["color"] )
            Layer[layer]["color"] = eval(color)
            print("maxwell OSC :", color ,"for layer", layer)

    # /maxwell/x/layer coord
    if path.find('/maxwell/x') == 0:
        layer = int(path[10:11])
        value = float(args[0])
        print("xdefault layer", layer, "value", value)
        LayerX[layer]['coord'] = value * LayerX[layer]['transamt']
        print("maxwell default OSC Got new X coord for layer", layer,":", LayerX[layer]['coord'])

    # /maxwell/y/layer coord
    if path.find('/maxwell/y') == 0:
        layer = int(path[10:11])
        value = float(args[0])
        print("ydefault layer", layer, "value", value)
        LayerY[layer]['coord'] = value * LayerY[layer]['transamt']
        print("maxwell default OSC Got new Y coord for layer", layer,":", LayerY[layer]['coord'])



# /maxwell/color/layernumber color
def OSCcolor(path, tags, args, source):

    print("maxwell OSC : color got", path, args)
    
    if args[1] == '1':
        layer = int(path[14:15])
        color = args[0]

        Layer[layer]["color"] = eval(color)
        print("maxwell OSC :", color ,"for layer", layer)



# /maxwell/intensity layernumber intensity
def OSCintensity(path, tags, args, source):
    
    print("maxwell OSC : intensity got",path, args)
    layer = int(args[0])
    i = int(args[1])

    intensity[layer] = i


# /maxwell/rotspeed layernumber axe speed
def OSCrotspeed(path, tags, args, source):

    print("maxwell OSC : rotspeed got", path, args)
    layer = int(args[0])
    axe = args[1]
    speed = int(args[2])

    if axe =="X":
        LayerX[layer]['rotspeed'] =  ccs[layer][100] = speed
    if axe =="Y":
        LayerY[layer]['rotspeed'] =  ccs[layer][104] = speed
    if axe =="Z":
        LayerZ[layer]['rotspeed'] =  ccs[layer][108] = speed


# /maxwell/transamt layernumber axe maxposition
def OSCtransamt(path, tags, args, source):
    
    print("maxwell OSC : transamt got", path, args)
    layer = int(args[0])
    axe = args[1]
    maxpos = int(args[2])

    if axe =="X":
        LayerX[layer]['transamt'] = ccs[layer][114] = maxpos
    if axe =="Y":
        LayerY[layer]['transamt'] = ccs[layer][118] = maxpos
    if axe =="Z":
        LayerZ[layer]['transamt'] = ccs[layer][122] = maxpos


# /maxwell/transpeed layernumber axe transpeed
def OSCtranspeed(path, tags, args, source):

    print("maxwell OSC : transspeed got", path, args)
    layer = int(args[0])
    axe = args[1]
    speed = int(args[2])

    if axe =="X":
        LayerX[layer]['transpeed'] = ccs[layer][112] = speed
    if axe =="Y":
        LayerY[layer]['transpeed'] = ccs[layer][116] =  speed
    if axe =="Z":
        LayerZ[layer]['transpeed'] = ccs[layer][120] =  speed


# /maxwell/part partname
def OSCpart(path, tags, args, source):

    print("maxwell part got", path, args)
    gstt.maxwellpart = args[0]


# /maxwell/bpm set current bpm
def OSCbpm(path, tags, args, source):

    pass
    #gstt.currentbpm = int(args[0])
    #print("maxwell OSC New BPM :", int(args[0]))


#/maxwell/clock
def OSClock(path, tags, args, source):

    pass
    #print("maxwell OSC Got MIDI clock")


#/maxwell/mixer/value layernumber value
def OSCmixervalue(path, tags, args, source):

    print("maxwell OSC : got Mixer Value", path, args)
    layer = int(args[0])
    value = int(args[1])
    Layer[layer]['mixer'] = value
    ccs[layer][90] = value


# /maxwell/start
def OSCstart(path, tags, args, source):

    print("maxwell OSC Got MIDI start")
    for l in range(3):
        Layer[l]['run'] = True


# /maxwell/stop layer
def OSCstop(path, tags, args, source):

    print("maxwell OSC Got MIDI stop for layer", int(args[0]))
    Layer[int(args[0])]['run'] = False
    #for l in range(3):
    #    Layer[l]['run'] = not Layer[l]['run']


# 33 (B0) ScanH / 35 (B0) ScanV / 24 (C0) Wave / 26 (D0) Circle
#fxs = ["anim.ScanH", "anim.ScanV", "anim.Wave", "anim.Circle"]
# /maxwell/noteon note velocity
def OSCnoteon(path, tags, args, source):

    #print("maxwell OSC Got MIDI noteon")
    l = int(args[0])
    note = int(args[1])
    velocity = int(args[2])

    # A0
    if note == 33:
        FXs[l] = beatstepfxs[0]
     # B0
    if note == 35: 
        FXs[l] = beatstepfxs[1]
    # C0
    if note == 24:  
        FXs[l] = beatstepfxs[2]
    # D0
    if note == 26:
        FXs[l] = beatstepfxs[3]

    print ("maxwell OSC Got new MIDI FX generator for layer", l, ":", FXs[l])


# /maxwell/noteoff layer notenumber
def OSCnoteoff(path, tags, args, source):

    print("maxwell OSC Got MIDI noteoff")
    l = int(args[0])
    note = int(args[1])


# /maxwell/cc channel CC value
# /maxwell/cc layer steps stepmax
def OSCcc(path, tags, args, source):
    #global step, steps, stepmax, stepvals

    print("maxwell OSC Got CC")
    channel = int(args[0])
    ccnumber = int(args[1])
    ccvalue = int(args[2])

    Layer[channel]['step']    = 0
    Layer[channel]['steps']   = ccnumber * 5
    Layer[channel]['stepmax'] = ccvalue  * 5
    Layer[channel]['stepvals'] = anim.sbilinear(Layer[channel]['steps'], 0, Layer[channel]['stepmax'])


'''
0 type  LX
1 freq  LX
3 amp   LX
11 inv  LX

12 type LY
13 freq LY
15 amp  LY
23 inv  LY

24 type LZ
25 freq LZ
27 amp  LZ
35 inv  LZ

36 type RX
37 freq RX
39 amp  RX
47 inv  RX

48 type RY
49 freq RY
51 amp  RY
59 inv  RY

60 type RZ
61 freq RZ
63 amp  RZ
71 inv  RZ

100 rotspeedX[
104 rotspeedY 
108 rotspeedZ 

114 transamtX 
118 transamtY 
122 transamtZ 

112 transpeedX
116 transpeedY
120 transpeedZ

Encoders :
LX freq amp phasemod transamt   RX freq amp phasemod rotdire
LY freq amp phasemod transamt   RL freq amp phasemod rotdire

'''

# /maxwell/rawcc layer encoder value Maxwell maxwell style
encoders = ['steps', 'stepmax','lineSize','radius']
def OSCrawcc(path, tags, args, source):
    #global step, steps, stepmax, stepvals

    layer = int(args[0])
    number = int(args[1])
    value = int(args[2])

    midix.SendUI('/beatstep/'+ "m" +str(layer)+ str(number+1) + '/value', [format(value, "03d")])
    ccs[layer][number] = value

    print(encoders[number],": value", value, "steps", Layer[layer]['steps'],"stepmax", Layer[layer]['stepmax'], "lineSize", Layer[layer]['lineSize'])
    #print("maxwell OSC Got rawCC for layer", layer, "encoder", encoders[number], "value", value)
    #print(value, Layer[layer]['stepmax'])
    if value * 2 < Layer[layer]['stepmax']:

        Layer[layer][encoders[number]] = value * 5
        Layer[layer]['stepvals'] = anim.sbilinear(Layer[layer]['steps'], 0, Layer[layer]['stepmax'])

'''
# /maxwell/rawcc layer encoder value maxwell style
encoders = ['steps', 'stepmax','lineSize','radius']
def OSCrawcc(path, tags, args, source):
    #global step, steps, stepmax, stepvals

    layer = int(args[0])
    number = int(args[1])
    value = int(args[2])

    midix.SendUI('/beatstep/'+ "m" +str(layer)+ str(number+1) + '/value', [format(value, "03d")])
    ccs[layer][number] = value

    print(encoders[number],": value", value, "steps", Layer[layer]['steps'],"stepmax", Layer[layer]['stepmax'], "lineSize", Layer[layer]['lineSize'])
    #print("maxwell OSC Got rawCC for layer", layer, "encoder", encoders[number], "value", value)
    #print(value, Layer[layer]['stepmax'])
    if value * 2 < Layer[layer]['stepmax']:

        Layer[layer][encoders[number]] = value * 5
        Layer[layer]['stepvals'] = anim.sbilinear(Layer[layer]['steps'], 0, Layer[layer]['stepmax'])
'''

# /maxwell/rotdirec layer axe direc
def OSCrotdirec(path, tags, args, source):

    layer = int(args[0])
    axe = args[1]
    direc = int(args[2])

    if axe =="X":
        LayerX[layer]['rotdirec'] = ccs[layer][102] = direc
    if axe =="Y":
        LayerY[layer]['rotdirec'] = ccs[layer][106] = direc 
    if axe =="Z":
        LayerZ[layer]['rotdirec'] = ccs[layer][110] = direc

#                   
# /maxwell/xcoord layer value
def OSCXcoord(path, tags, args, source):

    Layer[layer]['run'] = False 
    LayerX[int(args[0])]['coord'] = int(args[1])

    #layer = int(path[10:11])
    #value = float(args[0])
    #LayerX[layer]['coord'] = value * LayerX[layer]['lineSize']

    print("maxwell OSC Got new Xcoord for layer", layer,":", LayerX[layer]['coord'])


# /maxwell/ycoord layer value
def OSCYcoord(path, tags, args, source):

    Layer[layer]['run'] = False 
    LayerX[int(args[0])]['coord'] = int(args[1])

    print("maxwell OSC Got new Ycoord for layer", layer,":", LayerY[layer]['coord'])

# [0-1] ?
# /maxwell/scale layer value
def OSCcale(path, tags, args, source):

    layer = int(args[0])
    value = int(args[1])

    Layer[int(args[0])]['scale'] = float(args[1])*200
    ccs[layer][98] = value * 200


# /maxwell/scandots       layernumber value
def OSCandots(path, tags, args, source):

    Layer[int(args[0])]['scandots'] = int(args[1])

    # ccs[layer][98] = value       2/11


# /maxwell/radius       layernumber radius
def OSCradius(path, tags, args, source):

    Layer[int(args[0])]['radius'] = int(args[1])



#                         L/R  X/Y/Z  sin:0/saw:33/squ:95/lin:127
# /maxwell/curvetype layer side axe type
def OSCurvetype(path, tags, args, source):
    
    layer = int(args[0])
    side = args[1] 
    axe = args[2]
    value = args[3]

    if side == 'L':
        if axe =="X":
            CurveLX[layer]['type'] = ccs[layer][0] = value
        if axe =="Y":
            CurveLY[layer]['type'] = ccs[layer][12] = value
        if axe =="Z":
            CurveLZ[layer]['type'] = ccs[layer][24] = value

    else:
        if axe =="X":
            CurveRX[layer]['type'] = ccs[layer][36] = value
        if axe =="Y":
            CurveRY[layer]['type'] = ccs[layer][48] = value 
        if axe =="Z":
            CurveRZ[layer]['type'] = ccs[layer][60] = value


# /maxwell/freq  layer side axe type
def OSCfreq(path, tags, args, source):
    
    layer = int(args[0])
    side = args[1] 
    axe = args[2]
    value = args[3]

    if side == 'L':
        if axe =="X":
            CurveLX[layer]['freq'] = ccs[layer][1] = value
        if axe =="Y":
            CurveLY[layer]['freq'] = ccs[layer][13] = value
        if axe =="Z":
            CurveLZ[layer]['freq'] = ccs[layer][25] = value

    else:
        if axe =="X":
            CurveRX[layer]['freq'] = ccs[layer][37] = value
        if axe =="Y":
            CurveRY[layer]['freq'] = ccs[layer][49] = value 
        if axe =="Z":
            CurveRZ[layer]['freq'] = ccs[layer][61] = value


# /maxwell/amp  layer side axe type
def OSCamp(path, tags, args, source):
    
    layer = int(args[0])
    side = args[1] 
    axe = args[2]
    amp = args[3]

    if side == 'L':
        if axe =="X":
            CurveLX[layer]['amp'] = ccs[layer][3] = amp
        if axe =="Y":
            CurveLY[layer]['amp'] = ccs[layer][15] = amp
        if axe =="Z":
            CurveLZ[layer]['amp'] = ccs[layer][27] = amp

    else:
        if axe =="X":
            CurveRX[layer]['amp'] = ccs[layer][39] = amp
        if axe =="Y":
            CurveRY[layer]['amp'] = ccs[layer][51] = amp
        if axe =="Z":
            CurveRZ[layer]['amp'] = ccs[layer][63] = amp



#                         L/R  X/Y/Z  0/1
# /maxwell/inv layer side axe 
def OSCurveinv(path, tags, args, source):
    
    layer = int(args[0])
    side = args[1] 
    axe = args[2]
    value = args[3]

    if side == 'L':
        if axe =="X":                                   
            CurveLX[layer]['inv'] = ccs[layer][11] = value * inv
        if axe =="Y":
            CurveLY[layer]['inv'] = ccs[layer][23] = value * inv
        if axe =="Z":
            CurveLZ[layer]['inv'] = ccs[layer][35] = value * inv

    else:
        if axe =="X":
            CurveRX[layer]['inv'] = ccs[layer][47] = value * inv
        if axe =="Y":
            CurveRY[layer]['inv'] = ccs[layer][59] = value * inv
        if axe =="Z":
            CurveRZ[layer]['inv'] = ccs[layer][71] = value * inv


'''

To code : what curve ?

#                                  CC : X 7 Y 21 Z 11
# /maxwell/cu/phaseoffset layernumber axe phaseoffset
def OSCphaseoffset((path, tags, args, source):

    layer = int(args[0])
    value = int(args[1])


    if axe =="X":
        LayerX[layer]['phaseoffset'] = ccs[layer][102] = direc

    if axe =="Y":
        Y[layer]['phaseoffset'] = ccs[layer][106] = direc 

    if axe =="Z":
        LayerZ[layer]['phaseoffset'] = ccs[layer][110] = direc



Layer = [{'scandots': 100, 'radius': 150, 'color': red, 
CurveL= [{'type': 64, 'freq': 1, 'phaseoffset': 0}] * 3
CurveR= [{'type': 64, 'freq': 1, 'phaseoffset': 0}] * 3

'''


# /maxwell/linesize layer value
def OSClinesize(path, tags, args, source):

    #Layer[layer]['run'] = False 
    Layer[int(args[0])]['lineSize'] = float(args[1])*200
    #Layer[int(args[0])]['lineSize'] = float(args[1])


'''
/osc/left/X/curvetype is Artnet 0  MIDI Channel 1 CC 0
/osc/left/Y/curvetype is Artnet 12  MIDI Channel 1 CC 12
/osc/left/Z/curvetype is Artnet 24  MIDI Channel 1 CC 24

/osc/right/X/curvetype is Artnet 36  MIDI Channel 1 CC 36
/osc/right/Y/curvetype is Artnet 48  MIDI Channel 1 CC 48
/osc/right/Z/curvetype is Artnet 60  MIDI Channel 1 CC 60
"sin": 0, "saw": 33, "squ": 95, "lin": 127
'''

#
# OSC Audio
# 

# /maxwell/audioR value
def OSCaudioR(path, tags, args, source):
    global audioR

    audioR = abs(float(args[0])* audiosize)
    #print("maxwell OSC Got audioR value", audioR )


# /maxwell/audioL value
def OSCaudioL(path, tags, args, source):
    global audioL

    audioL = abs(float(args[0]) * audiosize)
    #print("maxwell OSC Got audioR value", audioL )


# OSC FX selection

# /maxwell/fx/layer FXname
def OSCfx(path, tags, args, source):

    layer = int(path[11:12])
    fx = args[0]
    FXs[layer] = "anim."+fx
    print("maxwell OSC Got new WS FX generator for layer", layer,":", FXs[layer])

    '''
    layer = int(args[0])
    fx = args[1]
    FXs[layer] = "anim."+fx
    print("maxwell OSC Got new WS FX generator for layer", layer,":", FXs[layer])
    '''

#
# OSC Beatstep
#

beatstepfxs = ["anim.ScanH", "anim.ScanV", "anim.Wave", "anim.Circle"]
def beatstepUI():

    midix.SendUI('/beatstep', [1])
    midix.SendUI('/beatstep/on', [1])
    midix.SendUI('/status', ["maxwell"])
    if linked:
        midix.SendUI('/bpm', alink.bpm)

    for l in range(4):
        
        # First encoder line
        midix.SendUI('/beatstep/'+ "m1" + str(l+1) + '/line1', '')
        midix.SendUI('/beatstep/'+ "m1" + str(l+1) + '/line2', encoders[l])
        midix.SendUI('/beatstep/'+ "m1" + str(l+1) + '/value', [format(0, "03d")])
        midix.SendUI('/beatstep/'+ "m1" + str(4+l+1) + '/line1', '')
        midix.SendUI('/beatstep/'+ "m1" + str(4+l+1) + '/line2', encoders[l])
        midix.SendUI('/beatstep/'+ "m1" + str(4+l+1) + '/value', [format(0, "03d")])

        # First pad line
        fxname = beatstepfxs[l].split('.')
        print(fxname)
        midix.SendUI('/beatstep/'+ "m3" + str(l+1) + '/line1', fxname[0])
        midix.SendUI('/beatstep/'+ "m3" + str(l+1) + '/line2', fxname[1])
        midix.SendUI('/beatstep/'+ "m3" + str(4+l+1) + '/line1', fxname[0])
        midix.SendUI('/beatstep/'+ "m3" + str(4+l+1) + '/line2', fxname[1])



# 
# Color functions
#

def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))


def rgb2hex(rgb):
    return int('0x%02x%02x%02x' % tuple(rgb),0)

#
# Compute animations speed
#

def animSpeeds():

    print("Compute animations speed...")
    
    for l in range(3):
        Layer[l]['stepvals'] = anim.sbilinear(Layer[l]['steps'], 0, Layer[l]['stepmax'])
        #print(Layer[l]['stepvals'])



#
# ALl FXs points generation
#

def AllFX():
    global step, shapestep 

    for l in range(3):

        if AllFXDisplay[l]: #and 0 <= x0 < screen_size[0] - 2 and 0 <= y0 < screen_size[1] - 2:
 
            LAY = Layer[l]
            #print(LAY)

            dots = []
            dotsL = anim.Maxwell(LAY, CurveLX[l], CurveLY[l], CurveLZ[l], LayerX[l], LayerY[l], LayerZ[l])
            dotsR = anim.Maxwell(LAY, CurveRX[l], CurveRY[l], CurveRZ[l], LayerX[l], LayerY[l], LayerZ[l])

            for dot in range(LAY['scandots']):
                dotX = (dotsL[dot][0]*(100-LAY['mixer'])/100) + (dotsR[dot][0]*LAY['mixer']/100)                #+ transX.values[point]
                dotY = (dotsL[dot][1]*(100-LAY['mixer'])/100) + (dotsR[dot][1]*LAY['mixer']/100)   #+ transY.values[point]
                dotZ = (dotsL[dot][2]*(100-LAY['mixer'])/100) + (dotsR[dot][2]*LAY['mixer']/100)   #+ transZ.values[point]
                dots.append((dotX, dotY, dotZ))



            lj.rPolyLineOneColor(dots, c = LAY['color'], layer = l, closed = FX0Form.closed, xpos = LayerX[l]['transamt'] + LAY['stepvals'][LAY['step']] - (LAY['lineSize']/2), ypos = LayerY[l]['transamt'], resize = LAY['scale'] * audioR, rotx = LayerX[l]['rotdirec'], roty = LayerY[l]['rotdirec'], rotz = LayerZ[l]['rotdirec'])

            #lj.rPolyLineOneColor(dots, c = LAY['color'], layer = l, closed = FX0Form.closed, xpos = FX0Form.xpos + LAY['stepvals'][LAY['step']] - (LAY['lineSize']/2), ypos = FX0Form.ypos, resize = LAY['scale'] * audioR, rotx = X[l]['rotdirec'], roty = Y[l]['rotdirec'], rotz = Z[l]['rotdirec'])
            # OSC cc Audio reactive audioR -> size

            if LAY['run']:
                if LAY['step'] < LAY['steps']-1:
                    LAY['step'] +=1
                else:
                    LAY['step'] = 0
                # print("stepmax", LAY['stepmax'], 'step', LAY['step'])

            if shapestep < shapesteps-1:
                shapestep +=1
            else:
                shapestep =0


        '''
        # morphing
            gstt.patchnumber[layer] = number
            for ccnumber in range(len(maxwell['ccs'])):

                gstt.morphCCinc[ccnumber] = (getPatchValue(gstt.patchnumber[layer], ccnumber) - gstt.ccs[layer][ccnumber]) / gstt.morphsteps
                gstt.morphCC[ccnumber] = gstt.ccs[layer][ccnumber]
                print("CC", ccnumber, "was", gstt.ccs[layer][ccnumber],"will be", getPatchValue(gstt.patchnumber[layer], ccnumber), "so inced is", gstt.morphCCinc[ccnumber])

            gstt.morphing = 0
        '''

#X0 = anim.COORDobject("X0",0, 0, 0, 0)
#L0 = LAYERobject("0", "saw", 100, 150, red, True, 0, 500, 200, [], 300, 255)



# Update Pose webUI
def UpdatemaxwellUI():

    lj.WebStatus("Maxwell say sthng")


print('Loading Maxwell...')
lj.WebStatus("Loading Maxwell...")

print("Starting OSC server at", gstt.myIP, "port", OSCinPort, "...")
oscserver.addMsgHandler("/maxwell/ljscene", OSCljscene)

oscserver.addMsgHandler("/maxwell/noteon", OSCnoteon)
#oscserver.addMsgHandler("/maxwell/fx", OSCfx)

oscserver.addMsgHandler("/maxwell/noteoff", OSCnoteoff)
#oscserver.addMsgHandler("/maxwell/color", OSCcolor)

oscserver.addMsgHandler("/maxwell/bpm",  OSCbpm)
oscserver.addMsgHandler("/maxwell/clock", OSClock)
oscserver.addMsgHandler("/maxwell/start", OSCstart)
oscserver.addMsgHandler("/maxwell/stop", OSCstop)
oscserver.addMsgHandler("/maxwell/part", OSCpart)

oscserver.addMsgHandler("/maxwell/rawcc", OSCrawcc)
oscserver.addMsgHandler("/maxwell/cc", OSCcc)

oscserver.addMsgHandler("/maxwell/audioR", OSCaudioR)
oscserver.addMsgHandler("/maxwell/autioL", OSCaudioL)

oscserver.addMsgHandler("/maxwell/xcoord", OSCXcoord)
oscserver.addMsgHandler("/maxwell/ycoord", OSCYcoord)
oscserver.addMsgHandler("/maxwell/linesize", OSClinesize)
oscserver.addMsgHandler("/maxwell/scale", OSCcale)
oscserver.addMsgHandler("/maxwell/scandots", OSCandots)

oscserver.addMsgHandler("/maxwell/intensity", OSCintensity)
oscserver.addMsgHandler("/maxwell/rotspeed", OSCrotspeed)
oscserver.addMsgHandler("/maxwell/transamt", OSCtransamt)
oscserver.addMsgHandler("/maxwell/rotdirec", OSCrotdirec)

# Add OSC generic layerugins commands : 'default", /ping, /quit, /pluginame/obj, /pluginame/var, /pluginame/adddest, /pluginame/deldest
lj.addOSCdefaults(oscserver)
oscserver.addMsgHandler( "default", OSChandler )
#anim.prepareSTARFIELD()

beatstepUI()

#beatstep.UpdatePatch(beatstep.patchnumber)

print("Updating maxwell UI...")
UpdatemaxwellUI()

midix.check()

animSpeeds()

audioR = 1
audioL = 1
audiosize = 1.1

'''
steps = 500
step = 0
stepmax = 200
stepvals = anim.sbilinear(steps, 0, stepmax)
'''

shapesteps = 50
shapestep = 0
shapemax = 2
shapevals = anim.ssquare(shapesteps, 1, 0, shapemax)

def Run():
    
    try:
        while lj.oscrun:

            # If you want an idea 
            # t0 = time.time()
            lj.OSCframe()
            if linked:
                alink.BeatEvent()

            AllFX()

            time.sleep(0.002)

            #t1 = time.time()
            # looptime = t1 - t0
            # 25 frames/sec -> 1 frame is 0.04 sec long
            # if looptime is 0.01 sec
            # 0.04/0.01 = 4 loops with the same anim
            # so speedanim is 1 / 4 = 0.25
            # speedanim = 1 / (0.04 / looptime)

            lj.DrawDests()
            #print("Took %f" % (t1 - t0, ))

    #except KeyboardInterrupt:
    #    pass

    except Exception:
        traceback.print_exc()

    # Gently stop on CTRL C

    finally:

        lj.WebStatus("maxwell Exit")
        print("Stopping OSC...")
        lj.OSCstop()

    print ("maxwell Stopped.")

Run()

