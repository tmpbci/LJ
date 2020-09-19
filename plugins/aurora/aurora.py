#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''

Aurora interactive installation

Quoi pour debut fin ?
Dependre du tempo gstt.currentbpm 

LICENCE : CC
Sam Neurohack



CCs Aurora Style

#              0         1         2          3        4       5           6           7
encoders = ['steps', 'stepmax','lineSize','radius','Xcoord','Ycoord', 'Xrotdirec','Zrotdirec']

    layer = int(args[0])
    number = int(args[1])
    value = int(args[2])

    ccs[layer][number] = value


Xcoord = 114    # /translator/X/amt 
Ycoord = 118    # /translator/Y/amt 
Zcoord = 122    # /translator/Z/amt 
        
scandots = 138  # /points/number 
scale= 98       # /scaler/scale is Artnet 98
        
Xrotdirec = 102 # /rotator/X/direct
Yrotdirec = 106 # /rotator/Y/direct
Zrotdirec = 110 # /rotator/Z/direct
        
rotspeed = 100  # /rotator/X/speed 
        
color
run
    
step
steps
stepmax
stepvals
        
lineSize
radius
intensity = 92 # /intensity/freq

# /aurora/transpeed layernumber axe transpeed

# /aurora/transamt layernumber axe maxposition



 LINK

  - bpm 

  - beatnumber -> Event
 

 MIDI  

 - cc : channel = layer / ccnumber = steps / ccvalue = stepmax -> /aurora/cc channel ccnumber ccvalue
 
 - notes

 if midi.sync :

 - midix.bpm
 
 - start -> /aurora/start
 
 - stop  -> /aurora/stop
 
 - clock -> /aurora/clock


 OSC 

 - /aurora/scim layernumber
 
 - /aurora/amp  layer side axe amp

 - /aurora/cc layer steps stepmax

 - /aurora/color/layername colorname

 - /aurora/fx/layernumber fxname ("ScanH", "ScanV", "Wave", "Circle", "Dot00", "Zero", "Maxwell", "Starfield", "Trckr", "Word")

 - /aurora/intensity layernumber intensity

 - /aurora/linesize layer value

 - /aurora/noteoff layer note

                    33 (B0) ScanH / 35 (B0) ScanV / 24 (C0) Wave / 26 (D0) Circle
 - /aurora/noteon layer note velocity

 - /aurora/part partname

 - /aurora/radius layernumber value

 - /aurora/rawcc layer encoder value (to change given encoder parameter ie 0 = steps)

                        X 102 Y 106 Z 110
 - /aurora/rotdirec layernumber axe rotdirec
                          X 100 Y 104 Z 108
 - /aurora/rotspeed layernumber axe speed

                        Scale 98
 - /aurora/scale layer value

                        X 114 Y 118 Z 122
 - /aurora/transamt layernumber axe maxposition 

 - /aurora/transpeed layernumber axe transpeed

 - /aurora/trckr/frame layernumber framenumber points

 - /aurora/x/layernumber coord (0-1)
 - /aurora/xcoord layernumber coord

 - /aurora/y/layernumber coord (0-1)
 - /aurora/ycoord layernumber coord

 - /aurora/word/layernumber word

mode ALIGN

mode LIVE

mode SONG

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
import midix, anim, user
import log

ljpath = r'%s' % os.getcwd().replace('\\','/')

# import from shell
sys.path.append(ljpath +'/../../libs3/')
sys.path.append(ljpath +'/../libs3/')

#import from LJ
sys.path.append(ljpath +'/libs3/')

sys.path.append('../libs3')
sys.path.append(ljpath +'/../../libs3')

import gstt

is_py2 = sys.version[0] == '2'
if is_py2:
    from OSC import OSCServer, OSCClient, OSCMessage
else:
    from OSC3 import OSCServer, OSCClient, OSCMessage

import lj23layers as lj
import argparse

print()
log.infog("Aurora v0.1b")

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

print()
log.info('Startup...')
# print("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Aurora for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-m","--myIP",help="IP to bind (0.0.0.0 by default) ",type=str)
argsparser.add_argument("-s","--scene",help="LJ scene number (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)
argsparser.add_argument("-L","--Lasers",help="Number of lasers connected (1 by default).",type=int)
argsparser.add_argument('-song',help="Run according to external (LIVE is default)", dest='song', action='store_true')
argsparser.set_defaults(song=False)
argsparser.add_argument('-link',help="Enable Ableton Link (disabled by default)", dest='link', action='store_true')
argsparser.set_defaults(link=False)
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
    gstt.myIP = '0.0.0.0'

# Lasers = number of laser connected
if args.Lasers  != None:
    lasernumber = args.Lasers
else:
    lasernumber = 1

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


lj.Config(redisIP, ljscene, "aurora")


ccs =[[0] * 140] *4

# Layer FXs
FXs = ["ScanH", "ScanV", "Wave", "Circle", "Dot00", "Zero", "Maxwell", "Starfield", "Trckr", "Word"]
AllFXDisplay = [True, True, True, True]


# Animation parameters for each layer
Layer = [] *lasernumber
Stars = []    

for l in range(lasernumber):

    Layer.append({'number': 0, 'FX': "user.User4",
        'Xcoord': 45, 'Ycoord': 45, 'Zcoord': 0,
        'scandots': 64, 'scale': 45, 'color': red,  "run": False, 
        'intensity': 255, 'closed': False,
        'lineSize': 64, 'radius': 45, 'wavefreq': 3,
        'word': "hello",
        'step': 0, 'steps': 60, 'stepmax': 60, 'stepvals': [], 
        'Xtransamt': 0, 'Ytransamt': 0, 'Ztransamt': 0, 
        'Xtranspeed': 0, 'Ytranspeed': 0, 'Ztranspeed': 0,
        'Xrotdirec': 0, 'Yrotdirec': 0, 'Zrotdirec': 0, 
        'Xrotspeed': 0, 'Yrotspeed': 0, 'Zrotspeed': 0,
        'rotspeed': 0
        })

    Layer[l]['number']= l

multi = {"radius": 300 }


#
# Destination :           name, number, active, layer , scene, laser)
#

Dest000 = lj.DestObject('FX0', 0, True, 0 , 0, 0)

if lasernumber >1:
    Dest101 = lj.DestObject('FX1', 1, True, 1 , 0, 1)

if lasernumber >2:
    Dest202 = lj.DestObject('FX2', 2, True, 2 , 0, 2)

if lasernumber >3:
    Dest303 = lj.DestObject('FX3', 3, True, 3 , 0, 3)

'''
# RelativeObject              name, active, intensity, xy, color, red, green, blue, layer , closed, xpos , ypos , scale , rotx , roty , rotz
FX0Form = lj.RelativeObject('FX0', True, 255, [], Layer[0]['color'], 255, 0, 0, 0 , False, 250 , 250, 1 , 0 , 0 , 0)
FX1Form = lj.RelativeObject('FX1', True, 255, [], Layer[1]['color'], 255, 0, 0, 1 , False, 250 , 250, 1 , 0 , 0 , 0)
FX2Form = lj.RelativeObject('FX2', True, 255, [], Layer[2]['color'], 255, 0, 0, 2 , False, 250 , 250, 1 , 0 , 0 , 0)
FX3Form = lj.RelativeObject('FX3', True, 255, [], Layer[3]['color'], 255, 0, 0, 3 , False, 250 , 250, 1 , 0 , 0 , 0)
'''

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


# /aurora/ljscene
def OSCljscene(path, tags, args, source):

    log.info("Aurora OSC : got /aurora/ljscene with value" + str(args[0]))
    lj.WebStatus("aurora to virtual "+ str(args[0]))
    ljscene = args[0]
    lj.ljscene(ljscene)

# default handler
def OSChandler(path, tags, args, source):
    global TrckrPts

    oscaddress = ''.join(path.split("/"))
    #print()
    print("Aurora default OSC Handler : " + str(path) + " from Client : " + str(source[0]))

    if len(args) > 0:
        pass

    #Convert from TouchOSC full text OSC style (no args) 
    if path.find(" ") != -1:

        prevargs = []
        if len(args) > 0:
            prevargs = args
            print(prevargs)
        newargs = path.split(" ")
        args=[]
        #print(newargs, len(newargs))
        for arg in range(len(newargs)-1):
            args.append(newargs[arg+1])

        args.append(prevargs[0])
        
        print("correction", path, args)
        #log.info("with args " + str(args))

    # /aurora/fx/layernumber FXname
    if path.find('/aurora/fx') == 0:

        #print("path", path, 'args', args)
        #print("layer", path[11:12])
        layer = int(path[11:12])

        if layer <= lasernumber-1:
            fx = args[0]
            if fx in FXs:
    
                Layer[layer]['FX']  = "anim."+fx
                print("Aurora default OSC got FX generator for layer", layer,":", Layer[layer]['FX'] )
                lj.SendLJ("/line1",[fx])
                midix.SendUI('/status', [fx])
            else:
                print("unknwon FX.")
        else:
            print("NOT POSSIBLE : only", lasernumber,"laser requested at startup")
            lj.SendLJ("/line1",str(lasernumber)+ " Laser")
            
    # /aurora/color/layernumber colorname
    if path.find('/aurora/color') == 0:

        #if args[1] =='1':
        layer = int(path[14:15])
        if layer <= lasernumber-1:
            color = args[0]
            Layer[layer]['color'] = eval(color)
            print("Aurora default OSc for Layer", layer,Layer[layer]['FX'], "Got color change to", color)
        else:
            print("NOT POSSIBLE : only", lasernumber,"laser requested at startup")
            lj.SendLJ("/line1",str(lasernumber)+ " Laser")

    #                      [0,1] or [0,127]
    # /aurora/x/layernumber coord
    if path.find('/aurora/x') == 0:

        layer = int(path[10:11])
        value = float(args[0])
        if value >1:
            value = value /127
        #print("xdefault layer", layer, "value", value)
        Layer[layer]['Xcoord'] = value * screen_size[0]
        print("Aurora default OSC got X coord for layer", layer,":", Layer[layer]['Xcoord'])
        midix.SendUI('/status', ["X : "+str(value * screen_size[0])])
    #                      [0,1] or [0,127]
    # /aurora/y/layernumber coord
    if path.find('/aurora/y') == 0:

        layer = int(path[10:11])
        value = float(args[0])
        if value >1:
            value = value /127
        #print("ydefault layer", layer, "value", value)
        Layer[layer]['Ycoord'] = value * screen_size[1]
        print("Aurora default OSC got Y coord for layer", layer,":", Layer[layer]['Ycoord'])
        midix.SendUI('/status', ["Y : "+str(value * screen_size[0])])
    
    # /aurora/trckr/frame layernumber framenumber points
    if path.find('aurora/trckr/frame') == 0:

       if debug != 0: 
         print("Aurora default OSC got trckr frame", args[1], "for layer", args[0], "with path", path)
         print(len(args),"args", args)

       counter =0

       '''
       TrckrPts = []
       for dot in range(2,len(args)-1,2):

         TrckrPts.append([float(args[dot]), float(args[dot+1])])
       '''

       TrckrPts[args[0]] = []
       for dot in range(2,len(args)-1,2):

         TrckrPts[args[0]].append([float(args[dot]), float(args[dot+1])])


    # /aurora/word/layer word
    if path.find('/aurora/word') == 0:

        layer = int(path[13:14])
        value = args[0]
        Layer[layer]['word'] = value
        print("Aurora default OSC got word", args[0], "for layer", layer)
        midix.SendUI('/status', ["Word : "+str(value * screen_size[0])])

    # /aurora/word/layer word
    if path.find('/aurora/rawcc') == 0:

        layer = int(args[0])
        number = int(args[1])
        value = int(args[2])
        midix.SendUI('/beatstep/'+ "m" +str(layer+1)+ str(number+1) + '/value', [format(value, "03d")])
        #ccs[layer][number] = value
    
        print(encoders[number],": value", value, "steps", Layer[layer]['steps'],"stepmax", Layer[layer]['stepmax'], "lineSize", Layer[layer]['lineSize'])
        print("Aurora Default OSC Got rawCC for layer", layer, "encoder", encoders[number], "value", value)
        #print(value, Layer[layer]['stepmax'])
        if value * 2 < Layer[layer]['stepmax']:
    
            Layer[layer][encoders[number]] = value * 5
            Layer[layer]['stepvals'] = anim.sbilinear(Layer[layer]['steps'], 0, Layer[layer]['stepmax'])

    # /aurora/scim
    if path.find('/aurora/scim') == 0:

        print("OScim sending to LJ2 /scim",int(args[0])+24)
        lj.SendLJ("/scim", [int(args[0])+24])

'''
# /aurora/color/layernumber color
def OSCcolor(path, tags, args, source):

    print("Aurora OSC : color got", path, args)
    
    if args[1] == '1':
        layer = int(path[14:15])
        color = args[0]

        Layer[layer]["color"] = eval(color)
        print("Aurora OSC :", color ,"for layer", layer)
'''

# /aurora/scim layernumber
def OSCim(path, tags, args, source):

    newarg = path.split(" ")
    newlaser = args[0]+24
    print("OSim sending to LJ2 /scim",str(newlaser))
    lj.SendLJ("/scim", [newlaser])
    print("sending knobs value for new layer")
    UpdateKnobs(newlaser)
    midix.SendUI('/status', ["Sim : "+newlaser])


def Resampler(laser,lsteps):

    #                   shortstep          longsteps    
    # lsteps is  like : [ 1.0, 8,     0.25, 3, 0.75, 3, 1.0, 10]
    print("Resampler change for laser ", laser)
    lj.SendLJ("/resampler/"+str(laser), [lsteps])


# /aurora/start
def OSCstart(path, tags, args, source):

    print("Aurora OSC Got MIDI start")
    for l in range(3):
        Layer[l]['run'] = True
    midix.SendUI('/status', ["Start"])


# /aurora/stop layer
def OSCstop(path, tags, args, source):

    print("Aurora OSC Got MIDI stop for layer", int(args[0]))
    Layer[int(args[0])]['run'] = False
    #for l in range(3):
    #    Layer[l]['run'] = not Layer[l]['run']
    midix.SendUI('/status', ["Stop"])


# 33 (B0) ScanH / 35 (B0) ScanV / 24 (C0) Wave / 26 (D0) Circle
# fxs = ["anim.ScanH", "anim.ScanV", "anim.Wave", "anim.Circle"]
# /aurora/noteon layer note velocity
def OSCnoteon(path, tags, args, source):

    print("Aurora OSC Got MIDI noteon")
    l = int(args[0])
    note = int(args[1])
    velocity = int(args[2])

    # first led raw : FX change

    # A0 / Scan H
    if note == 33:
        Layer[l]['FX'] = beatstepfxs[0]
    # B0
    if note == 35: 
        Layer[l]['FX'] = beatstepfxs[1]
    # C0
    if note == 24:  
        Layer[l]['FX'] = beatstepfxs[2]
    # D0
    if note == 26:
        Layer[l]['FX'] = beatstepfxs[3]

    # E0
    if note == 28:
        Layer[l]['FX'] = beatstepfxs[4]
    # F0
    if note == 29: 
        Layer[l]['FX'] = beatstepfxs[5]
    # G0
    if note == 31:  
        Layer[l]['FX'] = beatstepfxs[6]
    # G#0
    if note == 21:
        Layer[l]['FX'] = beatstepfxs[7]

    if 21 < note < 35:
        midix.SendUI('/status', [Layer[l]['FX']])
    # Second led raw : Color change

    # A1
    if note == 45:
        Layer[l]['color'] = eval(beatstepcols[0])
    # B1
    if note == 47: 
        Layer[l]['color'] = eval(beatstepcols[1])
    # C1
    if note == 36:  
        Layer[l]['color'] = eval(beatstepcols[2])
    # D1
    if note == 38:
        Layer[l]['color'] = eval(beatstepcols[3])

    # E1
    if note == 40:
        Layer[l]['color'] = eval(beatstepcols[4])
    # F1
    if note == 41: 
        Layer[l]['color'] = eval(beatstepcols[5])
    # G1
    if note == 43:  
        Layer[l]['color'] = eval(beatstepcols[6])
    # G#1
    if note == 44:
        Layer[l]['color'] = eval(beatstepcols[7])

    if 36 < note < 47:
        midix.SendUI('/status', [Layer[l]['color']])


    print ("Aurora OSC Got new MIDI FX/color for layer", l, ":", Layer[l]['FX'],"/",(Layer[l]['color']) )


# /aurora/noteoff layer notenumber
def OSCnoteoff(path, tags, args, source):

    print("Aurora OSC Got MIDI noteoff")
    l = int(args[0])
    note = int(args[1])


# /aurora/fx layer FXname
def OSCfx(path, tags, args, source):

    layer = int(args[0])
    fx = args[1]
    print(layer, fx)
    if fx in FXs:
        Layer[layer]['FX'] = "anim."+fx
        print("Aurora OSC Got new WS FX generator for layer", layer, ":", Layer[layer]['FX'])
    else:
        print("unknwon FX.")

#                   
# /aurora/xcoord layer value
def OSCXcoord(path, tags, args, source):

    #Layer[layer]['run'] = False 
    layer = int(args[0])
    value = float(args[1])
    if value >0:
       value = value /127
    #print("xdefault layer", layer, "value", value)
    Layer[layer]['Xcoord'] = value * screen_size[0]
    print("Aurora OSC got X coord for layer", layer,":", Layer[layer]['Xcoord'])



# /aurora/ycoord layer value
def OSCYcoord(path, tags, args, source):

    layer = int(args[0])
    value = float(args[1])
    if value >0:
       value = value /127
    #print("xdefault layer", layer, "value", value)
    Layer[layer]['Ycoord'] = value * screen_size[0]
    print("Aurora OSC got Y coord for layer", layer,":", Layer[layer]['Ycoord'])

# [0-1] ?
# /aurora/scale layer value
def OSCale(path, tags, args, source):

    layer = int(args[0])
    value = float(args[1])
    #if value >1:
    #    value = value /127
    print("New scale", value, "for layer", layer)
    Layer[int(args[0])]['scale'] = value*3
    ccs[layer][98] = value * 127


# /aurora/scandots layernumber value
def OSCandots(path, tags, args, source):

    if int(args[1]) > 2:
      Layer[int(args[0])]['scandots'] = int(args[1])
    else:
      lj.WebStatus("2 dots minimum")

    # ccs[layer][98] = value       2/11


# /aurora/radius layernumber radius [0-1] 
def OSCradius(path, tags, args, source):

    layer = int(args[0])
    value = float(args[1])
    if value >1:
        value = value /127
    print("aurora OSC got radius", value, (value * multi["radius"]), "layer", layer)
    Layer[layer]['radius'] = value * multi["radius"]
    midix.SendUI('/status', ["Radius : ", value * multi["radius"]])


# /aurora/amp  layer side axe type
def OSCamp(path, tags, args, source):
    pass

# /aurora/linesize layer value
def OSClinesize(path, tags, args, source):

    #Layer[layer]['run'] = False 

    layer = int(args[0])
    value = float(args[1])
    if value >1:
        value = value /127
    Layer[layer]['lineSize'] = value*400
    midix.SendUI('/status', ["linesize : ", value*400])


# /aurora/steps layer value
def OSCsteps(path, tags, args, source):

    layer = int(args[0])
    value = float(args[1])
    print("aurora OSC got steps", value, (value * 5), "layer", layer)
    
    if value * 2 < Layer[layer]['stepmax']:

        Layer[layer]['step']   = 0
        Layer[layer]['steps'] = round(value * 5)
        Layer[layer]['stepvals'] = anim.sbilinear(Layer[layer]['steps'], 0, Layer[layer]['stepmax'])


# /aurora/stepmax layer value
def OSCstepmax(path, tags, args, source):

    layer = int(args[0])
    value = float(args[1])
    print("aurora OSC got stepmax", value, (value * 5), "layer", layer)

    if value * 2 < Layer[layer]['stepmax']:

        Layer[layer]['step']   = 0
        Layer[layer]['stepmax'] = value * 5
        Layer[layer]['stepvals'] = anim.sbilinear(Layer[layer]['steps'], 0, Layer[layer]['stepmax'])


# /aurora/rotdirec layer axe direc
def OSCrotdirec(path, tags, args, source):

    layer = int(args[0])
    axe = args[1]
    direc = int(args[2])

    #print(layer, axe, direc)
    if axe =="X":
        Layer[layer]['Xrotdirec'] = ccs[layer][102] = direc
    if axe =="Y":
        Layer[layer]['Yrotdirec'] = ccs[layer][106] = direc 
    if axe =="Z":
        Layer[layer]['Zrotdirec'] = ccs[layer][110] = direc


# /aurora/rotspeed layernumber axe speed
def OSCrotspeed(path, tags, args, source):

    print("Aurora OSC : rotspeed got", path, args)
    layer = int(args[0])
    axe = args[1]
    speed = int(args[2])

    if axe =="X":
        Layer[layer]['Xrotspeed'] =  ccs[layer][100] = speed
    if axe =="Y":
        Layer[layer]['Yrotspeed'] =  ccs[layer][104] = speed
    if axe =="Z":
        Layer[layer]['Zrotspeed'] =  ccs[layer][108] = speed


# /aurora/transamt layernumber axe maxposition
def OSCtransamt(path, tags, args, source):
    
    print("Aurora OSC : transamt got", path, args)
    layer = int(args[0])
    axe = args[1]
    maxpos = int(args[2])

    if axe =="X":
        Layer[layer]['Xtransamt'] = ccs[layer][114] = maxpos
    if axe =="Y":
        Layer[layer]['Ytransamt'] = ccs[layer][118] = maxpos
    if axe =="Z":
        Layer[layer]['Ztransamt'] = ccs[layer][122] = maxpos



# /aurora/transpeed layernumber axe transpeed
def OSCtranspeed(path, tags, args, source):

    print("Aurora OSC : transspeed got", path, args)
    layer = int(args[0])
    axe = args[1]
    speed = int(args[2])

    if axe =="X":
        Layer[layer]['Xtranspeed'] = ccs[layer][112] = speed
    if axe =="Y":
        Layer[layer]['Ytranspeed'] = ccs[layer][116] =  speed
    if axe =="Z":
        Layer[layer]['Ztranspeed'] = ccs[layer][120] =  speed


# /aurora/part partname
def OSCpart(path, tags, args, source):

    print("aurora part got", path, args)
    gstt.aurorapart = args[0]


# /aurora/bpm set current bpm
def OSCbpm(path, tags, args, source):

    pass
    #gstt.currentbpm = int(args[0])
    #print("Aurora OSC New BPM :", int(args[0]))


#/aurora/clock
def OSClock(path, tags, args, source):

    pass
    #print("Aurora OSC Got MIDI clock")

# /aurora/trckr/frame
def OSCtrckr(path, tags, args, source):
    global TrckrPts


    #print("trckr got frame", args[0])
    if debug != 0: 
      print("trckr got frame", args[1], "for layer", layer)
      print(len(args),"args", args)
    counter =0
    TrckrPts[args[0]] = []

    for dot in range(2,len(args)-2,2):

      TrckrPts[args[0]].append([float(args[dot]), float(args[dot+1])])


# /aurora/rawcc layer encoder value (Aurora style)
encoders = ['Xcoord','Ycoord', 'resize', 'scandots', 'Xrotdirec', 'Yrotdirec', 'Zrotdirec', 'radius','steps', 'stepmax','lineSize','radius','radius','radius','radius','radius']
def OSCrawcc(path, tags, args, source):

    if path.find(" ") != -1:
        newargs = path.split(" ")
        args=[]
        #print(newargs, len(newargs))
        for arg in range(len(newargs)-1):
            args.append(newargs[arg+1])
        print(path, args)

    layer = int(args[0])
    number = int(args[1])
    value = int(args[2])

    #print("OSC rawcc")
    midix.SendUI('/beatstep/'+ "m" +str(layer+1)+ str(number+1) + '/value', [format(value, "03d")])
    #print('/beatstep/'+ "m" +str(layer+1)+ str(number+1) + '/value', [format(value, "03d")])
    #ccs[layer][number] = value

    print(encoders[number],": value", value, "steps", Layer[layer]['steps'],"stepmax", Layer[layer]['stepmax'], "lineSize", Layer[layer]['lineSize'])
    #print("Aurora OSC Got rawCC for layer", layer, "encoder", encoders[number], "value", value)
    #print(value, Layer[layer]['stepmax'])
    if value * 2 < Layer[layer]['stepmax']:

        Layer[layer][encoders[number]] = value * 5
        Layer[layer]['stepvals'] = anim.sbilinear(Layer[layer]['steps'], 0, Layer[layer]['stepmax'])


# /aurora/cc channel CC value
# /aurora/cc layer steps stepmax
def OSCcc(path, tags, args, source):

    print("Aurora OSC Got CC")
    channel = int(args[0])
    ccnumber = int(args[1])
    ccvalue = int(args[2])

    Layer[channel]['step']    = 0
    Layer[channel]['steps']   = ccnumber * 5
    Layer[channel]['stepmax'] = ccvalue  * 5
    Layer[channel]['stepvals'] = anim.sbilinear(Layer[channel]['steps'], 0, Layer[channel]['stepmax'])


# /aurora/intensity layernumber intensity
def OSCintensity(path, tags, args, source):
    
    print("Aurora OSC : intensity got", path, args)
    layer = int(args[0])
    Layer[layer]['intensity'] = int(args[1])
    lj.SendIntensity(layer, int(args[1]))


# /aurora/kpps layernumber kpps
def OSCkpps(path, tags, args, source):
    
    print("Aurora OSC : kpps got", path, args)
    layer = int(args[0])
    lj.Sendkpps(layer, int(args[1]))
    


#
# OSC Audio
# 

# /aurora/audioR value
def OSCaudioR(path, tags, args, source):
    global audioR

    audioR = abs(float(args[0])* audiosize)
    #print("Aurora OSC Got audioR value", audioR )


# /aurora/audioL value
def OSCaudioL(path, tags, args, source):
    global audioL

    audioL = abs(float(args[0]) * audiosize)
    #print("Aurora OSC Got audioR value", audioL )




#
# OSC Beatstep
#

beatstepfxs = ["anim.ScanH", "anim.ScanV", "anim.Wave", "anim.Circle", "anim.Starfield", "anim.Word", "anim.Trckr", "anim.ScanH"]
beatstepcols = ["red", "yellow", "green", "blue", "cyan", "white", "white", "white"]
def beatstepUI():

    midix.SendUI('/beatstep', [1])
    midix.SendUI('/beatstep/on', [1])
    midix.SendUI('/status', ["Aurora"])
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

# input hexcode = '0xff00ff'
def hex2rgb(hexcode):

    hexcode = hexcode[2:]
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    #return tuple(map(ord,hexcode[1:].decode('hex')))

# input rgb=(255,0,255) output '0xff00ff'
def rgb2hex(rgb):
    return '0x%02x%02x%02x' % tuple(rgb)

#def rgb2hex(r, g, b):
#    return hex((r << 16) + (g << 8) + b)


def rgb2int(rgb):
    return int('0x%02x%02x%02x' % tuple(rgb),0)

#def rgb2int(r,g,b):
#    return int('0x%02x%02x%02x' % (r,g,b),0)

def int2rgb(intcode):
    #hexcode = '0x{0:06X}'.format(intcode)
    hexcode = '{0:06X}'.format(intcode)
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

#
# Compute animations speed
#

def animSpeeds():

    print("Compute animations speed for", lasernumber, "lasers...")
    
    for l in range(lasernumber):
        Layer[l]['stepvals'] = anim.sbilinear(Layer[l]['steps'], 0, Layer[l]['stepmax'])

#
# Starfields
# 

StarFields = []

# Init Starfields
def prepareStarfield():

    print("Init starfields...")
    lj.WebStatus("Init starfields...")

    for field in range(lasernumber):

        StarFields.append({'stars': [], 'starfieldcount': 0, 'starspeed': 0.05, 'displayedstars': 5, 'num_stars': 50, 'max_depth': 20})
        for i in range(StarFields[field]['num_stars']):

            # A star is represented as a list with this format: [X,Y,Z]
            star = [randrange(-25,25), randrange(-25,25), randrange(1, StarFields[field]['max_depth'])]
            StarFields[field]['stars'].append(star)

#
# faces tracker
# 


TrckrPts =[[],[],[],[]] 
#print(TrckrPts)

def prepareTrckr():

  for l in range(lasernumber):
    #print()
    TrckrPts[l] = [[159.39, 137.68], [155.12, 159.31], [155.56, 180.13], [159.81, 201.6], [170.48, 220.51], [187.46, 234.81], [208.4, 244.68], [229.46, 248.21], [246.44, 244.91], [259.69, 234.83], [270.95, 221.51], [278.54, 204.66], [283.53, 185.63], [286.27, 165.79], [284.72, 144.84], [280.06, 125.01], [274.35, 118.7], [260.71, 117.23], [249.52, 118.86], [182.04, 121.5], [193.63, 114.79], [210.24, 114.77], [222.35, 117.57], [190.6, 137.49], [203.59, 132.42], [214.75, 137.58], [203.04, 140.46], [203.32, 136.53], [272.45, 141.57], [263.33, 135.42], [250.31, 138.89], [262.15, 143.27], [261.99, 139.37], [235.82, 131.74], [221.87, 156.09], [213.66, 165.88], [219.28, 173.53], [236.3, 175.25], [249.02, 174.4], [254.22, 167.81], [248.83, 157.39], [237.94, 147.51], [227.01, 168.39], [245.68, 170.02], [204.94, 197.32], [217.56, 192.77], [228.27, 190.55], [234.66, 192.19], [240.47, 191.09], [247.96, 193.87], [254.52, 199.19], [249.35, 204.25], [242.74, 207.16], [233.2, 207.87], [222.13, 206.52], [212.44, 203.09], [220.34, 198.74], [233.31, 200.04], [244.0, 199.6], [244.27, 197.8], [233.81, 197.44], [220.88, 196.99], [239.57, 162.69], [196.52, 133.86], [210.2, 133.98], [209.43, 139.41], [196.59, 139.47], [268.99, 137.59], [256.36, 136.02], [255.95, 141.5], [267.9, 142.85]]
    #print(l, ":",TrckrPts[l])
 
#
# ALl FXs points generation
#

def AllFX():
  global step, shapestep 

  for l in range(lasernumber):
    if AllFXDisplay[l]: #and 0 <= x0 < screen_size[0] - 2 and 0 <= y0 < screen_size[1] - 2:
              
       LAY = Layer[l]     
       dots = []
       ##log.err(str(l) + " "+ str(LAY))
       # Generators sending directly their points.
       if LAY['FX'] == "anim.Starfield":
           anim.Onefield(LAY, StarFields[l], hori=0, verti=0)

       elif LAY['FX'] == "anim.Trckr":
           anim.Trckr(LAY, TrckrPts[l])

       elif LAY['FX'] == "anim.Word":
           anim.Word(LAY)

       elif LAY['FX'] == "anim.User1":
           user.User1(LAY)

       elif LAY['FX'] == "anim.User2":
           user.User2(LAY)

       elif LAY['FX'] == "anim.User3":
           dots = user.User3(LAY)

       elif LAY['FX'] == "anim.User4":

           dots = user.User4(LAY)
           if LAY['FX'] != "Zero" or lent(dots) != 0:
               #print(dots, LAY['color'])
               lj.rPolyLineOneColor(dots, c = LAY['color'], layer = l, closed = LAY['closed'], xpos = LAY['Xcoord'] + LAY['stepvals'][LAY['step']] - (LAY['lineSize']/2), ypos = Layer[l]['Ycoord'], resize = LAY['scale'] * audioR, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])


       elif LAY['FX'] == "anim.Butterfly":
           anim.Butterfly(LAY)
       
       # Generic generators : return dots list 
       else:
           dots = eval(LAY['FX']+"(LAY)")
           if LAY['FX'] != "Zero" or lent(dots) != 0:
               #print(dots, LAY['color'])
               lj.rPolyLineOneColor(dots, c = LAY['color'], layer = l, closed = LAY['closed'], xpos = LAY['Xcoord'] + LAY['stepvals'][LAY['step']] - (LAY['lineSize']/2), ypos = Layer[l]['Ycoord'], resize = LAY['scale'] * audioR, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
           else:
               lj.rPolyLineOneColor((0,0,0), c = 0, layer = l, closed = LAY['closed'], xpos = LAY['Xcoord'] + LAY['stepvals'][LAY['step']] - (LAY['lineSize']/2), ypos = Layer[l]['Ycoord'], resize = LAY['scale'] * audioR, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
           # OSC cc Audio reactive audioR -> size
           
           # Animation
           if LAY['run']:

               lsteps = [ (1.0, 8),   (0.25, 3), (0.75, 3), (1.0, 10)]
               #Resampler(l,lsteps)

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
# Update Pose webUI
def UpdateAuroraUI():

    lj.WebStatus("Aurora Connected")


def UpdateKnobs(layernumber):

    LAY = Layer[layernumber]     

    lj.SendLJ("/forwardui", "aurora/word " + LAY['word'])

    lj.SendLJ("/forwardui", "aurora/Xcoord " + str(LAY['Xcoord']))
    lj.SendLJ("/forwardui", "aurora/Ycoord " + str(LAY['Ycoord']))
    lj.SendLJ("/forwardui", "aurora/scale "  + str(LAY['scale']))
    lj.SendLJ("/forwardui", "aurora/scandots " + str(LAY['scandots']))
    lj.SendLJ("/forwardui", "aurora/rotdirec X " + str(LAY['Xrotdirec']))
    lj.SendLJ("/forwardui", "aurora/rotdirec Y " + str(LAY['Yrotdirec']))
    lj.SendLJ("/forwardui", "aurora/rotdirec Z " + str(LAY['Zrotdirec']))

    lj.SendLJ("/forwardui", "aurora/steps " + str(LAY['steps']))
    lj.SendLJ("/forwardui", "aurora/stepmax " + str(LAY['stepmax']))
    lj.SendLJ("/forwardui", "aurora/linesize " + str(LAY['lineSize']))
    lj.SendLJ("/forwardui", "aurora/radius " + str(LAY['radius']))


prepareStarfield()
prepareTrckr()

log.info("Starting OSC server at " + str(gstt.myIP)+ " port "+ str(OSCinPort)+ " ...")
#print("TouchOSC", gstt.TouchOSCIP)
oscserver.addMsgHandler("/aurora/ljscene", OSCljscene)

oscserver.addMsgHandler("/aurora/noteon", OSCnoteon)
oscserver.addMsgHandler("/aurora/fx", OSCfx)
oscserver.addMsgHandler("/aurora/noteoff", OSCnoteoff)
#oscserver.addMsgHandler("/aurora/color", OSColor)
oscserver.addMsgHandler("/aurora/bpm",  OSCbpm)
oscserver.addMsgHandler("/aurora/clock", OSClock)
oscserver.addMsgHandler("/aurora/start", OSCstart)
oscserver.addMsgHandler("/aurora/stop", OSCstop)
oscserver.addMsgHandler("/aurora/part", OSCpart)

oscserver.addMsgHandler("/aurora/steps", OSCsteps)
oscserver.addMsgHandler("/aurora/stepmax", OSCstepmax)


oscserver.addMsgHandler("/aurora/rawcc", OSCrawcc)
oscserver.addMsgHandler("/aurora/cc", OSCcc)

oscserver.addMsgHandler("/aurora/audioR", OSCaudioR)
oscserver.addMsgHandler("/aurora/autioL", OSCaudioL)

oscserver.addMsgHandler("/aurora/Xcoord", OSCXcoord)
oscserver.addMsgHandler("/aurora/Ycoord", OSCYcoord)
oscserver.addMsgHandler("/aurora/linesize", OSClinesize)
oscserver.addMsgHandler("/aurora/scale", OSCale)
oscserver.addMsgHandler("/aurora/radius", OSCradius)
oscserver.addMsgHandler("/aurora/scandots", OSCandots)
oscserver.addMsgHandler("/aurora/scim", OSCim)

oscserver.addMsgHandler("/aurora/intensity", OSCintensity)
oscserver.addMsgHandler("/aurora/rotspeed", OSCrotspeed)
oscserver.addMsgHandler("/aurora/transamt", OSCtransamt)
oscserver.addMsgHandler("/aurora/rotdirec", OSCrotdirec)
oscserver.addMsgHandler("/aurora/trckr/frame", OSCtrckr)
# Add OSC generic layerugins commands : 'default", /ping, /quit, /pluginame/obj, /pluginame/var, /pluginame/adddest, /pluginame/deldest
lj.addOSCdefaults(oscserver)
oscserver.addMsgHandler( "default", OSChandler )
#anim.prepareSTARFIELD()

beatstepUI()

#beatstep.UpdatePatch(beatstep.patchnumber)

print("Updating Aurora UI...")
UpdateAuroraUI()

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

#Layer[1]['FX']="anim.StarField"
#Layer[0]['FX']="anim.Maxwell"

#lsteps = [ (1.0, 3), (0.25, 3), (0.75, 3), (1.0, 10)]
#Resampler(l,lsteps)
print(anim.randlinear2(8,0,100))

def Run():
    
    log.infog("Running...")
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
        log.err("Exception")
        traceback.print_exc()

    # Gently stop on CTRL C
    finally:

        lj.WebStatus("Aurora Disconnected")
        log.info("Stopping OSC...")
        lj.OSCstop()

        log.infog("Aurora Stopped.")

Run()

