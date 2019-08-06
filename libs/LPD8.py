#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
LPD8
v0.7.0

LPD8 Handler.
Start a dedicated thread to handle incoming events from LPD8 midi controller.

Depending on selected destination computer (Prog Chg + Pad number) actions will be done
locally or forwarded via OSC to given computer. Remote computer must run bhorpad or 
maxwellator.

# Note

# Program Change button selected : change destination computer

# CC rotary -> midi CC.         


by Sam Neurohack 
from /team/laser


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
import midi3, launchpad
#import midimacros, maxwellmacros
import traceback

from queue import Queue
#from libs import macros
import json, subprocess
from OSC3 import OSCServer, OSCClient, OSCMessage
import socket

print('LPD8 startup...')
myHostName = socket.gethostname()
print("Name of the localhost is {}".format(myHostName))
myIP = socket.gethostbyname(myHostName)
print("IP address of the localhost is {}".format(myIP))

myIP = "127.0.0.1"

print('Used IP', myIP)
OSCinPort = 8080
maxwellatorPort = 8090

LPD8queue = Queue()

mode = "maxwell"
mididest = 'Session 1'

midichannel = 1
CChannel = 0
CCvalue = 0
Here = -1

ModeCallback = ''
computerIP = ['127.0.0.1','192.168.2.95','192.168.2.52','127.0.0.1',
              '127.0.0.1','127.0.0.1','127.0.0.1','127.0.0.1']
computer = 0


# /cc cc number value
def cc(ccnumber, value, dest=mididest):

    midi3.MidiMsg([CONTROLLER_CHANGE+midichannel-1,ccnumber,value], dest)

def NoteOn(note,velocity, dest=mididest):
    midi3.NoteOn(note,velocity, mididest)

def NoteOff(note, dest=mididest):
    midi3.NoteOn(note, mididest)


def ComputerUpdate(comput):
    global computer

    computer = comput



# Client to export buttons actions from LPD8 or bhoreal

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
# Events from LPD8 buttons
#

# Process events coming from LPD8 in a separate thread.

def MidinProcess(LPD8queue):
    global computer

 
    while True:
        LPD8queue_get = LPD8queue.get
        msg = LPD8queue_get()
        #print (msg)

        # Note
        if msg[0]==NOTE_ON:
  
            # note mode
            ModeNote(msg[1], msg[2], mididest)

            '''
            # ModeOS
            if msg[2] > 0:
                ModeOS(msg[0])
            '''


        # Program Change button selected : change destination computer
        if msg[0]==PROGRAM_CHANGE:
        
            print("Program change : ", str(msg[1]))
            # Change destination computer mode
            print("Destination computer",int(msg[1]))
            computer = int(msg[1])


        # CC rotary -> midi CC.         
        if msg[0] == CONTROLLER_CHANGE:

            print("CC :", msg[1], msg[2])

            if computer == 0 or computer == 1:
                cc(int(msg[1]), int(msg[2]))

            else: 
                SendOSC(computerIP[computer-1], maxwellatorPort, '/cc', [int(msg[1]), int(msg[2])])

#
# Notes = midi notes
#

def ModeNote(note, velocity, mididest):


    print('computer',computer)

    # todo : decide whether its 0 or 1 !!!
    if computer == 0 or computer == 1:
        midi3.NoteOn(arg, velocity, mididest) 

    
    if velocity == 127:
        pass
        #print ('NoteON', BhorNoteXY(x,y),notename , "velocity", velocity )        
        #Disp(notename)
    else: 
        midi3.NoteOff(arg)
        #print ('NoteOFF', BhorNoteXY(x,y),notename , "velocity", velocity ) 



#
# Notes = OS Macros
#

def ModeOS(arg):


    macroname = 'n'+arg
    macronumber = findMacros(macroname,'OS')
    if macronumber != -1:
        
        eval(macros['OS'][macronumber]["code"])
    else:
        print("no Code yet")



LPD8queue = Queue()


# LPD8 Mini call back : new msg forwarded to LPD8 queue 
class LPD8AddQueue(object):
    def __init__(self, port):
        self.port = port
        #print("LPD8AddQueue", self.port)
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print()
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        LPD8queue.put(message)

#
# Modes :
# 

# Load Matrix only macros (for the moment) in macros.json 
def LoadMacros():
    global macros

    print()
    print("Loading LPD8 Macros...")
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



# Not assigned buttons
def DefaultMacro(arg):

    print ("DefaultMacro", arg)




#
# Default macros
#


LPD8macros = {

    "n1":      {"command": DefaultMacro, "default": 1},
    "n2":      {"command": DefaultMacro, "default": 2},
    "n3":      {"command": DefaultMacro, "default": 3},
    "n4":      {"command": DefaultMacro, "default": 4},
    "n5":      {"command": DefaultMacro, "default": 5},
    "n6":      {"command": DefaultMacro, "default": 6},
    "n7":      {"command": DefaultMacro, "default": 7},
    "n8":      {"command": DefaultMacro, "default": 8}
    }


def Run(macroname, macroargs=''):

        doit = LPD8macros[macroname]["command"]
        if macroargs=='':
            macroargs = LPD8macros[macroname]["default"]
        #print("Running", doit, "with args", macroargs )
        doit(macroargs)

LoadMacros()
