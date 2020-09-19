#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

Maxwell Macros
v0.7.0

by Sam Neurohack 
from /team/laser

Launchpad set a "current path"

"""
 
from OSC3 import OSCServer, OSCClient, OSCMessage
import time
import numpy as np
import rtmidi
from rtmidi.midiutil import open_midiinput 
from threading import Thread
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF,
                                  PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)

import os, json
import midi3

if os.uname()[1]=='raspberrypi':
    pass

port = 8090
ip = "127.0.0.1"
mididest = 'Session 1'
djdest = 'Port'

midichannel = 1
computerIP = ['127.0.0.1','192.168.2.95','192.168.2.52','127.0.0.1',
              '127.0.0.1','127.0.0.1','127.0.0.1','127.0.0.1']
computer = 0

# store current value for computer 1
cc1 =[0]*140

current = {
    "patch":  0,
    "prefixLeft": "/osc/left/X", 
    "prefixRight": "/osc/right/X", 
    "suffix": "/amp",
    "path": "/osc/left/X/curvetype",
    "pathLeft": "/osc/left/X/curvetype",
    "pathRight": "/osc/left/X/curvetype",
    "previousmacro": -1,
    "LeftCurveType":  0,
    "lfo": 1,
    "rotator": 1,
    "translator": 1
    }

specificvalues = {

# Sine: 0-32, Tri: 33-64, Square: 65-96, Line: 96-127
"curvetype": {"sin": 0, "saw": 33, "squ": 95, "lin": 127},
"freqlimit": {"1": 0, "4": 26, "16": 52, "32": 80, "127": 127},
"amptype": {"constant": 0, "lfo1": 33, "lfo2": 95, "lfo3": 127},
"phasemodtype": {"linear": 0,"sin": 90},
"phaseoffsettype": {"manual": 0, "lfo1": 33, "lfo2": 95, "lfo3": 127},
"ampoffsettype": { "manual": 0, "lfo1": 33, "lfo2": 95, "lfo3": 127},
"inversion": {"off": 0, "on": 127},
"colortype": {"solid": 0, "lfo": 127},
"modtype": {"sin": 0,"linear": 127},
"switch": {"off": 0,"on": 127},
"operation": {"+": 0, "-": 50, "*": 127}
}


#
# Maxwell CCs 
# 

def FindCC(FunctionName):

    for Maxfunction in range(len(maxwell['ccs'])):
        if FunctionName == maxwell['ccs'][Maxfunction]['Function']:
            #print(FunctionName, "is CC", Maxfunction)
            return Maxfunction

def LoadCC():
    global maxwell

    print("Loading Maxwell CCs Functions...")

    if os.path.exists('maxwell.json'):
        #print('File maxwell.json exits')
        f=open("maxwell.json","r")

    else:
        if os.path.exists('../maxwell.json'):
            #print('File ../maxwell.json exits')
            f=open("../maxwell.json","r")

    s = f.read()
    maxwell = json.loads(s)
    print(len(maxwell['ccs']),"Functions")
    print("Loaded.")

# /cc cc number value
def cc(ccnumber, value, dest=mididest):

    #print('Output CC',[CONTROLLER_CHANGE+midichannel-1, ccnumber, value], dest)
    midi3.MidiMsg([CONTROLLER_CHANGE+midichannel-1,ccnumber,value], dest)

def NoteOn(note,velocity, dest=mididest):
    midi3.NoteOn(note,velocity, mididest)

def NoteOff(note, dest=mididest):
    midi3.NoteOn(note, mididest)


def Send(oscaddress,oscargs=''):

    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclient = OSCClient()
    osclient.connect((ip, port)) 

    print("sending OSC message : ", oscmsg, "to", ip, ":",port)
    try:
        osclient.sendto(oscmsg, (ip, port))
        oscmsg.clearData()
        return True
    except:
        print ('Connection to', ip, 'refused : died ?')
        return False



def ssawtooth(samples,freq,phase):

    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.sawtooth(2 * np.pi * freq * t[ww])
    return samparray

def ssquare(samples,freq,phase):

    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.square(2 * np.pi * freq * t[ww])
    return samparray

def ssine(samples,freq,phase):

    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = np.sin(2 * np.pi * freq  * t[ww])
    return samparray



def MixerLeft(value):

    if value == 127:
        Send("/mixer/value", 0)


def MixerRight(value):

    if value == 127:
        Send("/mixer/value", 127)

def MixerTempo(tempo):

    for counter in range(127):
        Send("/mixer/value", counter)

# Jog send 127 to left and 1 to right
# increase or decrease current CC defined in current path  
def jogLeft(value):
    path = current["pathLeft"]
    print("jog : path =",path, "CC :", FindCC(path), "value", value)
    MaxwellCC = FindCC(current["pathLeft"])
    if value == 127:
        # decrease CC
        if cc1[MaxwellCC] > 0:
            cc1[MaxwellCC] -= 1
    else:
        if cc1[MaxwellCC] < 127:
            cc1[MaxwellCC] += 1
    #print("sending", cc1[MaxwellCC], "to CC", MaxwellCC )
    cc(MaxwellCC, cc1[MaxwellCC] , dest ='to Maxwell 1')
    #RotarySpecifics(MaxwellCC, path[path.rfind("/")+1:len(path)], value)


# Jog send 127 to left and 1 to right
# increase or decrease current CC defined in current path  
def jogRight(value):
    path = current["pathRight"]
    print("jog : path =",path, "CC :", FindCC(path), "value", value)
    MaxwellCC = FindCC(current["pathRight"])
    if value == 127:
        # decrease CC
        if cc1[MaxwellCC] > 0:
            cc1[MaxwellCC] -= 1
    else:
        if cc1[MaxwellCC] < 127:
            cc1[MaxwellCC] += 1
    #print("sending", cc1[MaxwellCC], "to CC", MaxwellCC )
    cc(MaxwellCC, cc1[MaxwellCC] , dest ='to Maxwell 1')
    #RotarySpecifics(MaxwellCC, path[path.rfind("/")+1:len(path)], value)


# Parameter change  : to left 127 / to right 0 or 1
def RotarySpecifics( MaxwellCC, specificsname, value):
    global maxwell

    print("Maxwell CC :",MaxwellCC)
    print("Current :",maxwell['ccs'][MaxwellCC]['init'])
    print("Specifics :",specificvalues[specificsname])
    print("midi value :", value)


    elements = list(enumerate(specificvalues[specificsname]))
    print(elements)
    nextype = maxwell['ccs'][MaxwellCC]['init']

    for count,ele in elements: 

        if ele == maxwell['ccs'][MaxwellCC]['init']:
            if count > 0 and value == 127:
                nextype = elements[count-1][1]

            if count < len(elements)-1 and value < 2:
                #print("next is :",elements[count+1][1])
                nextype = elements[count+1][1]

    print("result :", nextype, "new value :", specificvalues[specificsname][nextype], "Maxwell CC", MaxwellCC)
    maxwell['ccs'][MaxwellCC]['init'] = nextype
    cc(MaxwellCC, specificvalues[specificsname][nextype], dest ='to Maxwell 1')


# Change type : trig with only with midi value 127 on a CC event
def ButtonSpecifics127( MaxwellCC, specificsname, value):
    global maxwell

    print("Maxwell CC :",MaxwellCC)
    print("Current :",maxwell['ccs'][MaxwellCC]['init'])
    print("Specifics :",specificvalues[specificsname])
    print("midi value :", value)


    elements = list(enumerate(specificvalues[specificsname]))
    print(elements)
    nextype = maxwell['ccs'][MaxwellCC]['init']

    for count,ele in elements: 

        if ele == maxwell['ccs'][MaxwellCC]['init']:
            if count >0 and value == 127:
                nextype = elements[count-1][1]

            if count < len(elements)-1 and value < 2:
                #print("next is :",elements[count+1][1])
                nextype = elements[count+1][1]

    print("result :", nextype, "new value :", specificvalues[specificsname][nextype], "Maxwell CC", MaxwellCC)
    maxwell['ccs'][MaxwellCC]['init'] = nextype
    cc(MaxwellCC, specificvalues[specificsname][nextype], dest ='to Maxwell 1')



# Left cue button 127 = on  0 = off
def PrevPatch(value):
    global current

    print('PrevPatch function')
    if value == 127 and current['patch'] - 1 > -1:
        cc(9, 127, dest=djdest)
        time.sleep(0.1)
        current['patch'] -= 1
        print("Current patch is now :",current['patch'])
        midi3.NoteOn(current['patch'], 127, 'to Maxwell 1')
        cc(9, 0, dest=djdest)

# Right cue button 127 = on  0 = off
def NextPatch(value):
    global current

    print('NextPatch function', current["patch"])
    if value == 127 and current["patch"] + 1 < 41:
        cc(3, 127, dest = djdest)
        current["patch"] += 1
        #ModeNote(current["patch"], 127, 'to Maxwell 1')
        midi3.NoteOn(current["patch"], 127, 'to Maxwell 1')
        print("Current patch is now :",current["patch"])
        time.sleep(0.1)
        cc(3, 0, dest = djdest)


# increase/decrease a CC
def changeCC(value, path):
    global current

    #path = current["pathLeft"]
    MaxwellCC = FindCC(path)
    cc1[MaxwellCC] += value
    print("Change Left CC : path =",path, "CC :", FindCC(path), "is now ", cc1[MaxwellCC])
    cc(MaxwellCC, cc1[MaxwellCC] , dest ='to Maxwell 1')


def PlusTenLeft(value):
    value = 10
    changeCC(value, current["pathLeft"])

def MinusTenLeft(value):
    value = -10
    changeCC(value, current["pathLeft"])

def PlusOneLeft(value):
    value = 1
    changeCC(value, current["pathLeft"])

def MinusOneLeft(value):
    value = -1
    changeCC(value, current["pathLeft"])

def PlusTenRight(value):
    value = 10
    changeCC(value, current["pathRight"])

def MinusTenRight(value):
    value = -10
    changeCC(value, current["pathRight"])

def PlusOneRight(value):
    value = 1
    changeCC(value, current["pathRight"])

def MinusOneRight(value):
    value = -1
    changeCC(value, current["pathRight"])



def ChangeCurveLeft(value):

    MaxwellCC = FindCC(current["prefixLeft"] + '/curvetype')
    RotarySpecifics(MaxwellCC, "curvetype", value)


def ChangeFreqLimitLeft(value):

    MaxwellCC = FindCC(current["prefixLeft"] + '/freqlimit')
    RotarySpecifics(MaxwellCC, "curvetype", value)


def ChangeATypeLeft(value):

    MaxwellCC = FindCC(current["prefixLeft"] + '/freqlimit')
    RotarySpecifics(MaxwellCC, "curvetype", value)

def ChangePMTypeLeft(value):

    MaxwellCC = FindCC(current["prefixLeft"] + '/phasemodtype')
    RotarySpecifics(MaxwellCC, "curvetype", value)

def ChangePOTypeLeft(value):

    MaxwellCC = FindCC(current["prefixLeft"] + '/phaseoffsettype')
    RotarySpecifics(MaxwellCC, "curvetype", value)


def ChangeAOTypeLeft(value):

    MaxwellCC = FindCC(current["prefixLeft"] + '/ampoffsettype')
    RotarySpecifics(MaxwellCC, "curvetype", value)


def ChangeCurveRight(value):

    MaxwellCC = FindCC(current["prefixRight"] + '/curvetype')
    RotarySpecifics(MaxwellCC, "curvetype", value)


def ChangeCurveLFO(value):

    MaxwellCC = FindCC('/lfo/'+ current["lfo"] +'/curvetype')
    RotarySpecifics(MaxwellCC, "curvetype", value)


def ChangeCurveRot(value):

    MaxwellCC = FindCC('/rotator/'+ current["rotator"] +'/curvetype')
    RotarySpecifics(MaxwellCC, "curvetype", value)


def ChangeCurveTrans(value):

    MaxwellCC = FindCC('/translator/'+ current["translator"] +'/curvetype')
    RotarySpecifics(MaxwellCC, "curvetype", value)



