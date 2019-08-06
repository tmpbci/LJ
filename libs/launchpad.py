#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Launchpad
v0.7.0

Maunchpad mini Handler.
Start a dedicated thread to handle incoming events from launchpad.

Cls()
AllColorPad(color) 
StartLaunchPad(port)  : Start animation 

Led Matrix can be access with X and Y coordinates and as midi note (0-63)

PadNoteOn(note,color)
PadNoteOff(note)
PadNoteOnXY(x,y,color):
PadNoteOffXY(x,y):
PadNoteXY(x,y):

PadLeds[], PadTops[] and PadRights arrays stores matrix current state
 

Top raw and right column leds are numbered humanly 1-8. So -1 is for pythonic arrays position 0-7  

PadTopOn(number,color)
PadTopOff(number)
PadRightOn(number)
PadRightOff(number):

by Sam Neurohack 
from /team/laser

for python 2 & 3

"""


import time
import rtmidi
from rtmidi.midiutil import open_midiinput 
from threading import Thread
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF,
                                  PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)

from mido import MidiFile
import mido
import sys
import midi3
#import midimacros, maxwellmacros
import traceback

from queue import Queue
import scrolldisp
#from libs import macros
import json, subprocess
from OSC3 import OSCServer, OSCClient, OSCMessage
import socket


print('Launchpad Startup..')
myHostName = socket.gethostname()
print("Name of the localhost is {}".format(myHostName))
myIP = socket.gethostbyname(myHostName)
print("IP address of the localhost is {}".format(myIP))

myIP = "127.0.0.1"

print('Used IP', myIP)
OSCinPort = 8080
monomePort = 8000
maxwellatorPort = 8090

launchqueue = Queue()

mode = "maxwell"

mididest = 'Session 1'
midichannel = 1
CChannel = 0
CCvalue = 0

PadLeds = [0] * 64
PadTops= [0] * 8
PadRights= [0] * 8

Here = -1

ModeCallback = ''
# midi notes
LaunchLedMatrix = [(0,1,2,3,4,5,6,7),(16,17,18,19,20,21,22,23),(32,33,34,35,36,37,38,39),(48,49,50,51,52,53,54,55),(64,65,66,67,68,69,70,71),(80,81,82,83,84,85,86,87),(96,97,98,99,100,101,102,103),(112,113,114,115,116,117,118,119)]
# Notes
LaunchRight = (8,24,40,56,72,88,104,120) 
# CC
LaunchTop = (104,105,106,107,108,109,110,111)
PadTop = [0,0,0,0,0,0,0,0]
PadRight = [0,0,0,0,0,0,0,0]
PadMatrix = [0] * 64
TopSelection = [0] *8
computerIP = ['127.0.0.1','192.168.2.95','192.168.2.52','127.0.0.1',
              '127.0.0.1','127.0.0.1','127.0.0.1','127.0.0.1']
computer = 0



# /cc cc number value
def cc(ccnumber, value, dest=mididest):

    midi3.MidiMsg([CONTROLLER_CHANGE+midichannel-1,ccnumber,value], dest)



def Disp(text,device = 'Launchpad Mini'):

    print(device,midi3.FindInDevice(device))

    if (device == "Launchpad Mini" or device =='launchpad') and midi3.FindInDevice(device) != -1:
        scrolldisp.Display(text, color=(255,255,255), delay=0.2, mididest = 'launchpad')

    if device == 'bhoreal' and midi3.FindInDevice('Bhoreal'):
        scrolldisp.Display(text, color=(255,255,255), delay=0.2, mididest = device)


def PadNoteOn(note,color):
    (x,y) = BhorIndex(note)
    #print(note,x,y)
    PadNoteOnXY(x,y,color)


def PadNoteOff(note):
    (x,y) = BhorIndex(note)
    PadNoteOffXY(x,y)

def PadNoteOnXY(x,y,color):
    msg= [NOTE_ON, PadNoteXY(x,y), color]
    #print msg
    midi3.send(msg,"Launchpad")
    PadLeds[BhorNoteXY(x,y)]=color

    
def PadNoteOffXY(x,y):
    msg= [NOTE_OFF, PadNoteXY(x,y), 0]
    midi3.send(msg,"Launchpad")
    PadLeds[BhorNoteXY(x,y)]=0
        
def PadNoteXY(x,y):
    note = LaunchLedMatrix[int(y-1)][int(x-1)]
    return note

def PadIndex(note):
    y=note/16
    x=note%16
    return int(x+1),int(y+1)

def BhorIndex(note):
    y=note/8
    x=note%8
    #print "Note : ",note
    #print "BhorIndex : ", x+1,y+1
    return int(x+1),int(y+1)

def BhorNoteXY(x,y):
    note = (x -1)+ (y-1) * 8 
    return note

# top raw and right column leds are numbered humanly 1-8. So -1 is for pythonic arrays position 0-7  
def PadTopOn(number,color):
    msg= [CONTROLLER_CHANGE, LaunchTop[number-1], color]
    midi3.send(msg,"Launchpad")
    PadTops[number-1]=color

def PadTopOff(number):
    msg= [CONTROLLER_CHANGE, LaunchTop[number-1], 0]
    midi3.send(msg,"Launchpad")
    PadTops[number-1]=0

def PadRightOn(number,color):
    msg= [NOTE_ON, LaunchRight[number-1], color]
    midi3.send(msg,"Launchpad")
    PadRights[number-1]=color

def PadRightOff(number):
    msg= [NOTE_OFF, LaunchRight[number-1], 0]
    midi3.send(msg,"Launchpad")   
    PadRights[number-1]=0

def TopUpdate(button,color):
    #print(PadTop)
    PadTop = [0,0,0,0,0,0,0,0]
    PadTop[button] = color
    for pad in range(7):
        PadTopOn(pad+1,PadTop[pad])

def RightUpdate():
    for pad in range(9):
        PadRightOn(pad,PadRight[pad])

def MatrixUpdate():
    for pad in range(64):
        PadNoteOn(pad,PadMatrix[pad])

def MatrixSelect():
    MatrixUpdate()
    return 

def ComputerUpdate(comput):
    global computer

    computer = comput
    PadRightOn(computer+1,127)



# Client to export buttons actions from Launchpad or bhoreal

def SendOSC(ip,port,oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclient = OSCClient()
    osclient.connect((ip, port)) 

    print("sending OSC message : ", oscmsg, "to", ip, ":", port)

    try:
        osclient.sendto(oscmsg, (ip, port))
        oscmsg.clearData()
        return True
    except:
        print ('Connection to', ip, 'refused : died ?')
        return False


#
# LaunchPad start anim
#

# AllColor for bhoreal on given port
def AllColorPad(color):
    
    for led in range(0,64,1):
        PadNoteOn(led,color)
    '''
    for line in LaunchLedMatrix:
        for led in line:
            midiport[port].send_message([NOTE_ON, led, color])
    '''
    for rightled in range(8):
        PadRightOn(rightled+1,color)
    for topled in range(8):
        PadTopOn(topled+1,color)
        #midiport[port].send_message([CONTROLLER_CHANGE, topled, color])

def ClsMatrix():
    for led in range(0,64,1):
        PadNoteOff(led)

def ClsTop():
    for topled in range(8):
        PadTopOff(topled+1)

def ClsRight():

    for rightled in range(8):
        PadRightOff(rightled+1)

def Cls():

    ClsMatrix()
    ClsTop()
    ClsRight()
    ComputerUpdate(computer)

    '''
    for line in LaunchLedMatrix:
        for led in line:
            midiport[port].send_message([NOTE_OFF, led, 0])
    '''

def StartLaunchPad(port):

    #ClsPad(port)
    #time.sleep(0.3)
    AllColorPad(20)
    time.sleep(0.6)
    Cls()
    time.sleep(0.3)

#       
# Events from Launchpad Handling
#

# Process events coming from Launchpad in a separate thread.
def MidinProcess(launchqueue):
    global computer

    while True:
        launchqueue_get = launchqueue.get
        msg = launchqueue_get()
        #print (msg)

        if msg[0]==NOTE_ON:
  
            (x,y) = PadIndex(msg[1])

            # MATRIX = macros, notes, channels,...
            if x < 9:
                msg[1]= BhorNoteXY(x,y)
                macroname = "m"+str(y)+str(x)
                # Run Macro with matrix location and velocity
                Run(macroname, macroargs = int(msg[2]))

            # RIGHT = computer, this host or other computer
            if x == 9:
                print("Right Button : ", y)
                macroname = "r"+str(y)
                print(macroname)
                ClsRight()
                PadRightOn(y,127)
                print("Destination computer",y)
                computer = y
                #time.sleep(0.1)
                #PadRightOff(y)

        # TOP = Mode Note, CC, Os, Monome,..
        if msg[0]==CONTROLLER_CHANGE:
            print("Pad Top Button : ", str(msg[1]-103), "value",msg[2])
            TopUpdate(msg[1]-104,20)
            macroname = "t"+str(msg[1]-103)
            #print(macroname)
            Run(macroname, macroargs = (msg[1]-103,msg[2]))


launchqueue = Queue()
ModeCallback = "ModeNo"



# LaunchPad Mini call back : new msg forwarded to Launchpad queue 
class LaunchAddQueue(object):
    def __init__(self, port):
        self.port = port
        #print("LaunchAddQueue", self.port)
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print()
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        launchqueue.put(message)

#
# Modes : Top lines functions
# 

# Load Matrix only macros (for the moment) in macros.json 
def LoadMacros():
    global macros

    print()
    print("Loading Launchpad Macros...")
    f=open("macros.json","r")
    s = f.read()
    macros = json.loads(s)
    print(len(macros['OS']),"Macros")
    print("Loaded.")


# return macroname number for given type 'OS', 'Maxwell'
def findMacros(macroname,macrotype):

    #print("searching", macroname,'...')
    position = -1
    for counter in range(len(macros[macrotype])):
        #print (counter,macros[macrotype][counter]['name'],macros[macrotype][counter]['code'])
        if macroname == macros[macrotype][counter]['name']:
            #print(macroname, "is ", counter)
            position = counter
    return position


# Default top buttons : maxwell macros
def TopMacro(arg):

    topbutton, value = arg
    print ("topmacro", topbutton, "value", value)
    if value == 127:
        TopUpdate(topbutton-1,20)
        Disp("Ma")
        Disp('cr', 'bhoreal')
    ModeCallback = TopCallback

def TopCallback(arg):

    ClsMatrix()
    x,y,velocity = arg
    PadNoteOnXY(x,y,20)
    #print ('Macros OS', BhorNoteXY(x,y), "velocity", velocity )
    macroname = 'm'+str(y)+str(x)
    macronumber = findMacros(macroname,'Maxwell')
    if macronumber != -1:
        #print("code : ",macros['OS'][macronumber]["code"])
        eval(macros['Maxwell'][macronumber]["code"])
    else:
        print("no Code yet")

#
# Notes Macros
#

def ModeNote(arg):
    global ModeCallback


    topbutton, value = arg
    if value == 127:
        TopUpdate(topbutton-1,20)
        Disp("No")
        Disp('te', 'bhoreal')
        print("ModeNote")
   
    else:
        ClsMatrix()
    
    ModeCallback = "NoteCallback"


def NoteCallback(arg):

    #ClsMatrix()
    x,y,velocity = arg
    notename = midi3.midi2note(BhorNoteXY(x,y))

    print('computer',computer)

    # todo : decide whether its 0 or 1 !!!
    if computer == 0 or computer == 1:
        midi3.NoteOn(BhorNoteXY(x,y),velocity,'AutoTonic MIDI In') 
    else: 
        SendOSC(computerIP[computer-1],maxwellatorPort,'/note',[BhorNoteXY(x,y),velocity])

    if velocity == 127:
        PadNoteOnXY(x,y,20)
        #print ('NoteON', BhorNoteXY(x,y),notename , "velocity", velocity )        
        #Disp(notename)
    else: 
        PadNoteOnXY(x,y,0)
        #print ('NoteOFF', BhorNoteXY(x,y),notename , "velocity", velocity ) 

#
# CC Macros 
#

def ModeCC(arg):
    global ModeCallback
    
    topbutton, value = arg
    if value == 127:
        TopUpdate(topbutton-1,20)
        Disp('CC')
        Disp('  ', 'bhoreal')
        print("Mode CC")
        ModeCallback = "CCSelect"
        print("Please enter CC Channel")
        #ClsMatrix()
        Disp('Ch')

def CCSelect(arg):
    global ModeCallback, CChannel

    x,y, velocity = arg
    PadNoteOnXY(x,y,20)
    #print ('in CC channel callback x',x,'y',y)
    if velocity == 127:
        
        CChannel = BhorNoteXY(x,y)
        print("CC Channel", CChannel)
        print("Please enter CC Value")
        ModeCallback = "CCValue"
        Disp('Va')

def CCValue(arg):
    #ClsMatrix()
    x,y, velocity = arg
    PadNoteOnXY(x,y,20)
    #print ('in CC value callback x',x,'y',y)
    
    if velocity == 127:
        CCvalue = BhorNoteXY(x,y) * 2
        print("CC Channel", CChannel,"CC Value", CCvalue)


#
# OS Macros
#

def ModeOS(arg):
    global ModeCallback

    topbutton, value = arg
    if value == 127:
        Disp('Os')
        Disp('Ma', 'bhoreal')
        TopUpdate(topbutton-1,20)
        ModeCallback = "OSCallback"
    else:
        ClsMatrix()

def OSCallback(arg):

    ClsMatrix()
    x,y,velocity = arg
    PadNoteOnXY(x,y,20)
    #print ('Macros OS', BhorNoteXY(x,y), "velocity", velocity )
    macroname = 'm'+str(y)+str(x)
    macronumber = findMacros(macroname,'OS')
    if macronumber != -1:
        #print("code : ",macros['OS'][macronumber]["code"])
        eval(macros['OS'][macronumber]["code"])
    else:
        print("no Code yet")


#
# Monome emulation
#

prefix = '/box'

def ModeMonome(arg):
    global ModeCallback

    topbutton, value = arg
    if value == 127:
        TopUpdate(topbutton-1,20)
        Disp('Mo')
        Disp('me', 'bhoreal')
        ModeCallback = "MonomeCallback"

    else:
        ClsMatrix()


def MonomeCallback(arg):

    ClsMatrix()
    x,y,velocity = arg
    #PadNoteOnXY(x,y,20)

    SendOSC('127.0.0.1', monomePort, prefix+'/press', (x,y,1))
    SendOSC('127.0.0.1', monomePort, prefix+'/grid/key', (x,y,1))
  

#
# StartMode 
#

def ModeNo(arg):
    x,y,velocity = arg
    PadNoteOnXY(x,y,20)
    print ('Mode No x',x,'y',y,"note", PadNoteXY(x,y))

'''
def Mode(mode):
    global macros

    
    if mode == "maxwell":
        print("Launchpad in Maxwell mode")
        macros = maxwellmacros.buttons

    if mode == "generic":
        print("Launchpad in generic mode")
        macros = generic
'''


#
# Right column functions
# 

def RightMacro(number):

    print ("rightmacro",number)

#
# Default Pad macros
#


launchmacros = {

    "t":       {"command": TopMacro, "default": -1},
    "t1":      {"command": ModeNote, "default": ''},
    "t2":      {"command": ModeCC,   "default": ''},
    "t3":      {"command": ModeOS, "default": ''},
    "t4":      {"command": ModeMonome, "default": ''},
    "t5":      {"command": TopMacro, "default": 5},
    "t6":      {"command": TopMacro, "default": 6},
    "t7":      {"command": TopMacro, "default": 7},
    "t8":      {"command": TopMacro, "default": 8},
    
    "r1":      {"command": RightMacro, "default": 1},
    "r2":      {"command": RightMacro, "default": 2},
    "r3":      {"command": RightMacro, "default": 3},
    "r4":      {"command": RightMacro, "default": 4},
    "r5":      {"command": RightMacro, "default": 5},
    "r6":      {"command": RightMacro, "default": 6},
    "r7":      {"command": RightMacro, "default": 7},
    "r8":      {"command": RightMacro, "default": 8}
    }

#Mode("generic")


def Run(macroname, macroargs=''):

    #print ("macroargs", macroargs)

    # Matrix button -> parameters sent to current Function in ModeCallback
    if macroname.find("m") == 0:
        doit = eval(ModeCallback)
        doit((int(macroname[2]),int(macroname[1]), macroargs))
        #eval(ModeCallback)((int(macroname[2]),int(macroname[1]), macroargs),)


    # Otherwise do the macro
    else:

        doit = launchmacros[macroname]["command"]
        if macroargs=='':
            macroargs = launchmacros[macroname]["default"]
        #print("Running", doit, "with args", macroargs )
        doit(macroargs)

#ComputerUpdate(computer)
LoadMacros()


'''

Docs Community About
monome
osc : opensound control / serialosc protocol

what is serialosc? how does it work?
discovering and connecting to serialosc devices

serialosc server listens on port 12002.

when devices are connected, serialosc spawns new ports for each device. querying the server allows you to discover the port number for each device. (this supersedes the zeroconf method, which is still in place for legacy compatibility).
messages sent to serialosc server

/serialosc/list si <host> <port>

request a list of the currently connected devices, sent to host:port

/serialosc/notify si <host> <port>

request that next device change (connect/disconnect) is sent to host:port. to keep receiving the notifications, send another message to /serialosc/notify from the notify handler.
messages received from serialosc server

/serialosc/device ssi <id> <type> <port>

currently connected device id and type, at this port

/serialosc/add s <id>

device added

/serialosc/remove s <id>

device removed
to serialosc device
sys

these messages can be sent to a serialosc device to change settings.

/sys/port i <port>

change computer port

/sys/host s <host>

change computer host

/sys/prefix s <prefix>

change message prefix (filtering)

/sys/rotation i <degrees>

rotate the monome by degrees, where degrees is one of 0, 90, 180, 270. this replaces /cable

/sys/info si <host> <port>

/sys/info i <port>

/sys/info

info

request information (settings) about this device

/info can take the following arguments:

/info si <host> <port> (send /sys/info messages to host:port)

/info i <port> (send to localhost:port)

/info (send to current computer application's host:port)

example:

to serialosc:
    /sys/info localhost 9999
from serialosc to localhost:9999:
    /sys/id m0000045
    /sys/size 8 16
    /sys/host localhost
    /sys/port 23849
    /sys/prefix /nubs
    /sys/rotation 270

from serialosc

these messages are sent from serialosc to the computer port.

the messages below are sent after a /sys/info request is received.
sys

/sys/port i report computer port

/sys/host s report computer host

/sys/id s report device id

/sys/prefix s report prefix

/sys/rotation i report grid device rotation

/sys/size ii report grid device size

to device
grid

/grid/led/set x y s

set led at (x,y) to state s (0 or 1).

/grid/led/all s

set all leds to state s (0 or 1).

/grid/led/map x_offset y_offset s[8]

Set a quad (8×8, 64 buttons) in a single message.

Each number in the list is a bitmask of the buttons in a row, one number in the list for each row. The message will fail if the list doesn’t have 8 entries plus offsets.

taken apart:

(/grid/led/map)  <- the message/route
               (8 8)  <- the offsets
                    (1 2 4 8 16 32 64 128)  <- the bitmasks for each row

examples

/grid/led/map 0 0 4 4 4 4 8 8 8 8
/grid/led/map 0 0 254 253 125 247 239 36 191 4

Offsets must be mutliples of 8.

/grid/led/row x_offset y s[..]

Set a row in a quad in a single message.

Each number in the list is a bitmask of the buttons in a row, one number in the list for each row being updated.

examples (for 256)

/grid/led/row 0 0 255 255
/grid/led/row 8 5 255

examples (for 64)

/grid/led/row 0 0 232
/grid/led/row 0 3 129

Offsets must be mutliples of 8. Offsets for monome64 should always be zero.

/grid/led/col x y_offset s[..]

Set a column in a quad in a single message.

Each number in the list is a bitmask of the buttons in a column, one number in the list for each row being updated.

examples (for 256)

/grid/led/col 0 0 255 255 (updates quads 1 and 3)
/grid/led/col 13 8 255 (updates quad 4 due to offset.)

examples (for 64)

/grid/led/col 0 0 232
/grid/led/col 6 0 155

Offsets must be mutliples of 8. Offsets for monome64 should always be zero.

/grid/led/intensity i

variable brightness:

Valid values for ‘l’ below are in the range [0, 15].

January 2011 devices only support four intensity levels (off + 3 brightness levels). The value passed in /level/ messages will be “rounded down” to the lowest available intensity as below:

    [0, 3] - off
    [4, 7] - low intensity
    [8, 11] - medium intensity
    [12, 15] - high intensity

June 2012 devices allow the full 16 intensity levels.

/grid/led/level/set x y l
/grid/led/level/all l
/grid/led/level/map x_off y_off l[64]
/grid/led/level/row x_off y l[..]
/grid/led/level/col x y_off l[..]

tilt

/tilt/set n s

set active state of tilt sensor n to s (0 or 1, 1 = active, 0 = inactive).
arc

led 0 is north. clockwise increases led number. These can be viewed and tested in the browser at http://nomeist.com/osc/arc/

/ring/set n x l

set led x (0-63) on encoder n (0-1 or 0-3) to level l (0-15)

/ring/all n l

set all leds on encoder n (0-1 or 0-3) to level l (0-15)

/ring/map n l[64]

set all leds on encoder n (0-1 or 0-3) to 64 member array l[64]

/ring/range n x1 x2 l

set leds on encoder n (0-1 or 0-3) between (inclusive) x1 and x3 to level l (0-15). direction of set is always clockwise, with wrapping.
from device
grid

/grid/key x y s

key state change at (x,y) to s (0 or 1, 1 = key down, 0 = key up).
tilt

/tilt n x y z

position change on tilt sensor n, integer (8-bit) values (x, y, z)
arc

/enc/delta n d

position change on encoder n by value d (signed). clockwise is positive.

/enc/key n s

key state change on encoder n to s (0 or 1, 1 = key down, 0 = key up)

    Info@monome.org

'''