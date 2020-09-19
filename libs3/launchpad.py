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

colors : off 64 / full green 16 / yellow 127 / full red 3 

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
sys.path.append('libs/')
import os

import midi3, gstt
#import midimacros, maxwellmacros
import traceback

from queue import Queue
import scrolldisp, maxwellccs, beatstep, bhoreal
#from libs import macros
import json, subprocess
from OSC3 import OSCServer, OSCClient, OSCMessage
import socket

print()
print('Launchpad Startup..')
#myHostName = socket.gethostname()
#print("Name of the localhost is {}".format(myHostName))
#myIP = socket.gethostbyname(myHostName)
#myIP = socket.gethostbyname('')
#print("IP address of the localhost is {}".format(myIP))

#myIP = "127.0.0.1"
#print('Used IP', myIP)

monomePort = 8000


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


nocolor = 64
green = 16
yellow = 127
red = 3 

#nbmacro = 64
#ModeCallback = ''
# midi notes
LaunchLedMatrix = [(0,1,2,3,4,5,6,7),(16,17,18,19,20,21,22,23),(32,33,34,35,36,37,38,39),(48,49,50,51,52,53,54,55),(64,65,66,67,68,69,70,71),(80,81,82,83,84,85,86,87),(96,97,98,99,100,101,102,103),(112,113,114,115,116,117,118,119)]
# Notes
LaunchRight = (8,24,40,56,72,88,104,120) 
# CC
LaunchTop = (104,105,106,107,108,109,110,111)
PadTop = [0,0,0,0,0,0,0,0]
PadRight = [0,0,0,0,0,0,0,0]
PadMatrix = [0] * 64
matrix1 = [1,1]
matrix2 = [1,1]
matrix3 = [1,1]
TopSelection = [0] *8
computer = 0



# /cc cc number value
def cc(ccnumber, value, dest=mididest):

    gstt.ccs[gstt.lasernumber][ccnumber]= value
    if gstt.lasernumber == 0:
        midi3.MidiMsg([CONTROLLER_CHANGE+midichannel-1, ccnumber, value], dest)
    else:
        SendOSC(gstt.computerIP[gstt.lasernumber], gstt.MaxwellatorPort, '/cc/'+str(ccnumber),[value])
    SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/cc/'+str(ccnumber), [value])

#       
# Events from OSC
#

# Client to export buttons actions from Launchpad or bhoreal

def SendOSC(ip,port,oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclient = OSCClient()
    osclient.connect((ip, port)) 

    #print("Launchpad sending OSC message : ", oscmsg, "to", ip, ":", port)

    try:
        osclient.sendto(oscmsg, (ip, port))
        oscmsg.clearData()
        return True
    except:
        print ('Connection to', ip, 'refused : died ?')
        return False


def FromOSC(path, args):

    print(path, args)
    if path.find('/button') > -1:

        print()
        print('Launchpad OSC got', path, path[1:2], args[0])

        
        # Button pressed
        if args[0] == 1.0:

            # Matrix button
            if path[1:2] == 'm':
                number = BhorNoteXY(int(path[3:4]),int(path[2:3]))
                #number = PadNoteXY(int(path[3:4]), int(path[2:3]))
                #print('led on', number)
                LedOn(number)

            # top button : Layer change 
            if path[1:2] == 't':

                number = int(path[2:3])
                print("Pad Top Button : ", number, "on")
                TopUpdate(number -1, 127)
                if number < len(gstt.LaunchpadLayers):
                    ChangeLayer(number-1)

            # right button : Laser number
            if path[1:2] == 'r':

                number = int(path[2:3])
                #macroname = path[1:4]
                print("Right Button : ", number, "on")
                #ClsRight()
                PadRightOn(number, 0)
                RightUpdate()
                SendOSC(gstt.myIP, 8090, '/laser/led/'+str(number), [1])
                gstt.lasernumber = number
                #gstt.computer = number


        # Button released
        else:

            # Matrix
            if path[1:2] == 'm':
                #number = PadNoteXY(int(path[3:4]), int(path[2:3]))
                number = BhorNoteXY(int(path[3:4]),int(path[2:3]))
                print('led off', number)
                LedOff(number)

            # top button
            if path[1:2] == 't':

                number = int(path[2:3])
                print("Pad Top Button : ", number, "off")
                SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/t'+ str(number) +'/button', [1])

            # right button
            if path[1:2] == 'r':

                number = int(path[2:3])
                print("Right Button : ", number, "off")
                PadRightOn(number, 127)
                SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/r'+ str(number) +'/button', [1])
                #RightUpdate()

 

        #padCC('m'+path[2:4], int(args[0]))


#
# LaunchPad UIs
#

def Disp(text,device = 'Launchpad Mini'):

    print(device,midi3.FindInDevice(device))

    if (device == "Launchpad Mini" or device =='launchpad') and midi3.FindInDevice(device) != -1:
        scrolldisp.Display(text, color=(255,255,255), delay=0.2, mididest = 'launchpad')

    if device == 'bhoreal' and midi3.FindInDevice('Bhoreal'):
        scrolldisp.Display(text, color=(255,255,0), delay=0.2, mididest = device)


def PadNoteOn(note,color):
    (x,y) = BhorIndex(note)
    #print('PadNoteon', note, x, y, color)
    PadNoteOnXY(x,y,color)


def PadNoteOff(note):
    (x,y) = BhorIndex(note)
    #print('PadNoteOFF', note, x, y)
    PadNoteOffXY(x,y)

def PadNoteOnXY(x,y,color):
    msg= [NOTE_ON, PadNoteXY(x,y), color]
    #print(msg)
    midi3.send(msg,"Launchpad")
    PadLeds[BhorNoteXY(x,y)]=color

    
def PadNoteOffXY(x,y):
    msg= [NOTE_OFF, PadNoteXY(x,y), 0]
    #print(msg)
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
def PadTopOn(number, color):
    msg= [CONTROLLER_CHANGE, LaunchTop[number-1], color]
    midi3.send(msg,"Launchpad")
    PadTops[number-1]=color

def PadTopOff(number):
    msg= [CONTROLLER_CHANGE, LaunchTop[number-1], 0]
    midi3.send(msg,"Launchpad")
    PadTops[number-1]=0

def PadRightOn(number, color):
    msg= [NOTE_ON, LaunchRight[number-1], color]
    midi3.send(msg,"Launchpad")
    PadRights[number-1]=color

def PadRightOff(number):
    msg= [NOTE_OFF, LaunchRight[number-1], 0]
    midi3.send(msg,"Launchpad")   
    PadRights[number-1]=0

def TopUpdate(button, color):
    #print(PadTop)
    PadTop = [0,0,0,0,0,0,0,0]
    PadTop[button] = color
    for pad in range(7):
        PadTopOn(pad+1, PadTop[pad])

def RightUpdate():
    for pad in range(8):
        print(pad,PadRight[pad])
        PadRightOn(pad, PadRight[pad])
        if PadRight[pad] ==0:
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/r'+ str(pad) +'/button', [0])
        else:
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/r'+ str(pad) +'/button', [1])

def MatrixUpdate():
    for pad in range(64):
        PadNoteOn(pad, PadMatrix[pad])

def MatrixSelect():
    MatrixUpdate()
    return 

def ComputerUpdate(comput):
    global computer

    computer = comput
    PadRightOn(computer+1,127)


# AllColor for launchpad on given port
def AllColorPad(color):
    
    print('AllColorPad')
    for led in range(0,64,1):
        PadNoteOn(led,color)
    '''
    for line in LaunchLedMatrix:
        for led in line:
            midiport[port].send_message([NOTE_ON, led, color])
    '''
    for rightled in range(8):
        PadRightOn(rightled+1, color)
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
        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/r'+ str(rightled+1) +'/button', [0])


# ClsPatch 3th lines for Launchpad on given port

def ClsPatchs(port):
    for led in range(0,24,1):
        msg = [NOTE_OFF, led, 0]
        midi3.send(msg,"launchpad")


def Cls():

    ClsMatrix()
    ClsTop()
    ClsRight()
    ComputerUpdate(computer)


def Start(port):

    #ClsPad(port)
    #time.sleep(0.3)
    SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/on', [1])
    #AllColorPad(20)
    time.sleep(1)

    for color in range(64,128,1):
        #AllColorPad(color)
        PadNoteOn(color-64, color)
        #print("color", color)
    time.sleep(0.5)
    #Cls()
    #time.sleep(0.3)
    #UpdateDisplay()
    #PadRightOn(gstt.lasernumber, 127)
    #RightUpdate()
    TopUpdate(gstt.LaunchpadLayer, 127)



def DisplayFunctionsLeds():

    for led in range(40,64):
        #print(gstt.LaunchpadLayers[gstt.LaunchpadLayer])
        PadNoteOn(led, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["color"])
        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad', [1])
    #macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["code"]

def DisplayPatchs():

    for led in range(0,64):
        print('Display Patch',macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]])
        if macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["code"] == 'patch' and (str(led + 1) in gstt.patchs['pattrstorage']['slots']) != False:
            PadNoteOn(led, 19)

def UpdateDisplay():

    print('Launchpad Update Display...')
    #ClsMatrix()

    # Reseting small OSC leds
    '''
    for led in range(0,nbmacro,1):
        print(led, "off")
        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/bhoreal/' + macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["name"]+'/led', [0.0])
    '''
    
    for led in range(0,8,1):

        # first launchpad line is first maxwell presets line
        if str(led+1) in gstt.patchs['pattrstorage']['slots'] != False:
            PadNoteOn(led, 127)
        else:
            PadNoteOn(led, 64)
        
        # second launchpad line is 3rd maxwell presets line
        if str(16+led+1) in gstt.patchs['pattrstorage']['slots'] != False:
            PadNoteOn(8+led, 127)
        else:
            PadNoteOn(8+led, 64)

         # 3rd launchpad line is 5th maxwell presets line
        if str(32+led+1) in gstt.patchs['pattrstorage']['slots'] != False:
            PadNoteOn(16+led, 127)
        else:
            PadNoteOn(16+led, 64)


    for led in range(24,nbmacro,1):
            # light up hardware Launchpad led
            PadNoteOn(led, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["color"])

            macrocode = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["code"]
            macrotype = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["type"]
            macrocc = maxwellccs.FindCC(macrocode)
            macrolaser = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["laser"]
            macroname = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["name"]
            buttonname = macroname
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macroname+'/led', [0.0])
            #print(macrocode,macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led])
            macronumber = findMacros(macroname, gstt.LaunchpadLayers[gstt.LaunchpadLayer])

            # Maxwell osc commmand like /lfo/1/freq
            if (macrocode[:macrocode.rfind('/')] in maxwellccs.shortnames) == True:

                # OSC button : Display short text with type value like sin, saw,... 
                typevalue = macrocode[macrocode.rfind('/')+1:]
                values = list(enumerate(maxwellccs.specificvalues[typevalue]))
                init = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["init"]
                SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+macroname, [maxwellccs.shortnames[macrocode[:macrocode.rfind('/')]]+" "+values[init][1]])
                #PadNoteOn(macronumber, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"])
                
                if macrotype =='buttonmulti':
                    # Need to be optimized : this part will be done as many times as many buttons.
                    # Reset all OSC buttons 
                    macrochoices = list(macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["choices"].split(","))
                    #print("Resetting choices", macrochoices)
                    for choice in macrochoices:
                        #print(choice, macronumber, gstt.ccs[macrolaser][macrocc], maxwellccs.FindCC(macrocode), maxwellccs.specificvalues[typevalue][values[init][1]])
                        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+choice+'/led', [0])
                        PadNoteOn(findMacros(choice, gstt.LaunchpadLayers[gstt.LaunchpadLayer]), macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"])
                    
                    #maxwellccs.cc(maxwellccs.FindCC(macrocode), maxwellccs.specificvalues[typevalue][values[init][1]], 'to Maxwell 1')
                    #PadNoteOn(macronumber, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                    #SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+buttonname+'/led', [1])
                    #print(macronumber, macroname,macrocode,"CC",maxwellccs.FindCC(macrocode), "cc value", gstt.ccs[macrolaser][macrocc],"macrochoices", macrochoices,"values", values,"initvalue",maxwellccs.maxwell['ccs'][maxwellccs.FindCC(macrocode)]['init'])
                    #print(macronumber, macroname,macrocode,"CC",maxwellccs.FindCC(macrocode), "cc value", gstt.ccs[macrolaser][macrocc],"macrochoices", macrochoices)
                    if gstt.ccs[macrolaser][macrocc] == 0:
                        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+macrochoices[0]+'/led', [1])
                        PadNoteOn(findMacros(macrochoices[0], gstt.LaunchpadLayers[gstt.LaunchpadLayer]), macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                        #PadNoteOn(led, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                        #print(macrochoices[0])
                    if gstt.ccs[macrolaser][macrocc] == 127:
                        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+macrochoices[1]+'/led', [1])
                        PadNoteOn(findMacros(macrochoices[1], gstt.LaunchpadLayers[gstt.LaunchpadLayer]), macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                        #print(macrochoices[1])
                    if gstt.ccs[macrolaser][macrocc] == 254:
                        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+macrochoices[2]+'/led', [1])
                        PadNoteOn(findMacros(macrochoices[2], gstt.LaunchpadLayers[gstt.LaunchpadLayer]), macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                        #print(macrochoices[2])
                    if gstt.ccs[macrolaser][macrocc] == 381:
                        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+macrochoices[3]+'/led', [1])
                        PadNoteOn(findMacros(macrochoices[3], gstt.LaunchpadLayers[gstt.LaunchpadLayer]), macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                        #print(macrochoices[3])
                    

                if gstt.ccs[macrolaser][macrocc] == 127 and macrotype !='buttonmulti':
                    #print(macronumber, gstt.ccs[macrolaser][macrocc], maxwellccs.FindCC(macrocode), maxwellccs.specificvalues[typevalue][values[init][1]], macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                    SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+macroname+'/led', [1])
                    PadNoteOn(macronumber, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                #SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["name"], [maxwellccs.shortnames[macrocode[:macrocode.rfind('/')]]+" "+macrocode[macrocode.rfind('/')+1:]])
                ###SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][led]["name"], [maxwellccs.shortnames[macrocode[:macrocode.rfind('/')]]])
                
            # Code in maxwellccs library : skip "maxwellccs." display only Empty. maxwellccs.Empty will call maxwellccs.Empty() 
            elif macrocode.find('maxwellccs') ==0:
                SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macroname, [macrocode[11:]])

            else:
                SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macroname, [macrocode])
            #macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["code"]

def UpdateCC(ccnumber, value, laser = 0):

    print('Launchpad UpdateCC', ccnumber, value)
    # update iPad UI
    for macronumber in range(nbmacro):
        macrocode = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["code"]
        
        if macrocode == maxwellccs.maxwell['ccs'][ccnumber]['Function']:
           
            macroname = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["name"]
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+macroname+'/value', [format(gstt.ccs[laser][ccnumber], "03d")])
            break

def ChangeLayer(layernumber, laser = 0):

    
    gstt.LaunchpadLayer = layernumber
    # update iPad UI
    print('New Launchpad layer :', layernumber)
    SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/status', [gstt.LaunchpadLayers[gstt.LaunchpadLayer]])
    
    UpdateDisplay()
    

#       
# Events from Midi
#


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


# Process events coming from Launchpad in a separate thread.
def MidinProcess(launchqueue):
    global computer

    while True:
        launchqueue_get = launchqueue.get
        msg = launchqueue_get()
        #print (msg)

        if msg[0]==NOTE_ON:
  
            (x,y) = PadIndex(msg[1])
            #print('launchpad midi got', msg, x, y)


            # MATRIX = macros, notes, channels,...
            if x < 9:

                # Launchpad Led pressed
                print ("Launchpad Matrix : ", BhorNoteXY(x,y), PadLeds[BhorNoteXY(x,y)])

                # A led is pressed
                if msg[0] == NOTE_ON and msg[2] == 127:
                    LedOn(BhorNoteXY(x,y))
                  
                # Launchpad Led depressed
                elif msg[0] == NOTE_ON and msg[2] == 0:
                    LedOff(BhorNoteXY(x,y))


            # RIGHT = computer, this host or other computer
            if x == 9:
                    
                    macroname = "r"+str(y)
                    print("Right Button : ", y, macroname)
                    ClsRight()
                    PadRightOn(y, 127)
                    print("Destination laser :",y)
                    gstt.lasernumber = y
                    gstt.computer = y
                    #time.sleep(0.1)
                    #PadRightOff(y)


        # TOP = Mode Note, CC, Os, Monome,..
        if msg[0]==CONTROLLER_CHANGE:
            
            TopUpdate(msg[1]-104, 127)
            macroname = "t"+str(msg[1]-103)
            print("Pad Top Button : ", str(msg[1]-103), "value",msg[2], macroname)
            if msg[1]-103 < len(gstt.LaunchpadLayers):
                ChangeLayer(msg[1]-104)
            # Run(macroname, macroargs = (msg[1]-103,msg[2]))




def LedOn(number):

    macrocode = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["code"]
    macrocolor = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["color"]
    macrotype = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["type"]
    print('Launchpad Ledon number', number,'code',macrocode,"maxled",number%8+16*(number//7))

    # Patch 
    if macrocode == "patch":
        realnumber = number%8+16*(number//7)
        # If patch exist in loaded maxwell patchs
        if (str(realnumber+1) in gstt.patchs['pattrstorage']['slots']) == True:
            print('Launchpad ledon', number, '/pad/' + macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][realnumber]["name"]+'/led')
            # Reset color of previous selected led
            #PadNoteOn(gstt.patchnumber[0],127)
            # Change color of pushed led
            bhoreal.NoteOn(realnumber, 127)
            
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/bhoreal/' +macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][realnumber]["name"]+'/button', [1])
            bhoreal.NoteOn(gstt.patchnumber[0],18)
            PadNoteOn(number, 21)
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/bhoreal/' +macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][gstt.patchnumber[0]]["name"]+'/button', [0])
            SendOSC(gstt.computerIP[gstt.lasernumber], 8090, '/bhoreal/note', realnumber)
            gstt.patchnumber[gstt.lasernumber] = realnumber
        else:
            print("No Maxwell patch here !")
    
    # Code 
    else:
        # maxwell OSC path 
        if macrocode.find('/') > -1:
            padCC(macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["name"],1)
            #PadNoteOn(number, macrocolor-1)

        # code function : add (), call function then light up.
        else:
            eval(macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["code"]+"()")
            PadNoteOn(number, macrocolor-1)
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["name"]+'/led', [1.0])


def LedOff(number):

    print('Ledoff number', number)
    # Non patch & non multibutton led : light on hardware led.
    if macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["code"] != 'patch' and macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["type"] !='buttonmulti' and macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["type"] !='buttontoggle':
        PadNoteOn(number, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["color"])
        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["name"]+'/led', [0])
    
    # Existing Patch led :   
    elif (str(number + 1) in gstt.patchs['pattrstorage']['slots']) == True:
        SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/' + macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][number]["name"]+'/led', [1.0])


# Send to Maxwell a pad value given its Launchpad matrix name
def padCC(buttonname, state):

    macronumber = findMacros(buttonname, gstt.LaunchpadLayers[gstt.LaunchpadLayer])
    print('padCC : name', buttonname,"number", macronumber,"state", state)
    
    if macronumber != -1:

        # Button pressed
        if state == 1:

            macrocode = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["code"]
            typevalue = macrocode[macrocode.rfind('/')+1:]
            values = list(enumerate(maxwellccs.specificvalues[typevalue]))
            init = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["init"]
            macrotype = macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["type"]
            #print("matrix", buttonname, "macrocode", macrocode, "typevalue", typevalue,"macronumber", macronumber, "values", values, "init", init, "value", values[init][1], "cc", maxwellccs.FindCC(macrocode), "=", maxwellccs.specificvalues[typevalue][values[init][1]] )

            if init <0:

                # toggle button OFF -2 / ON -1
                if init == -2:
                    # goes ON
                    print(macrocode, 'ON')
                    maxwellccs.cc(maxwellccs.FindCC(macrocode), 127, 'to Maxwell 1')
                    macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["init"] = -1
                    PadNoteOn(macronumber, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                    print('/pad/'+buttonname+'/led 1')
                    SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+buttonname+'/led', [1])
                else:
                    # goes OFF
                    print(macrocode, 'OFF')
                    maxwellccs.cc(maxwellccs.FindCC(macrocode), 0, 'to Maxwell 1')
                    macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["init"] = -2
                    PadNoteOn(macronumber, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"])
                    print('/pad/'+buttonname+'/led 0')
                    SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+buttonname+'/led', [0])

            if macrotype =='buttonmulti':

                # Reset all OSC buttons 
                macrochoices = list(macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["choices"].split(","))
                #rint("Resetting choices", macrochoices)
                for choice in macrochoices:
                    print(choice, macronumber)
                    SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+choice+'/led', [0])
                    PadNoteOn(findMacros(choice, gstt.LaunchpadLayers[gstt.LaunchpadLayer]), macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"])
                
                #print(maxwellccs.FindCC(macrocode),maxwellccs.specificvalues[typevalue][values[init][1]] )                
                maxwellccs.cc(maxwellccs.FindCC(macrocode), maxwellccs.specificvalues[typevalue][values[init][1]], 'to Maxwell 1')
                PadNoteOn(macronumber, macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]][macronumber]["color"]-1)
                SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+buttonname+'/led', [1])
        
        if state == 0:
            # Button released
            print('reselect button /Launchpad/'+'m'+buttonname+'/button')
            SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/'+buttonname+'/led', [1])

    



launchqueue = Queue()
ModeCallback = "ModeNo"



#
# Modes : Top lines functions
# 

# Load Matrix only macros (for the moment) in launchpad.json 
def LoadMacros():
    global macros, nbmacro

    #print()
    print("Loading Launchpad Macros...")

    if os.path.exists('libs/launchpad.json'):
        #print('File is libs/launchpad.json')
        f=open("libs/launchpad.json","r")
    
    elif os.path.exists('../launchpad.json'):
        #print('File is ../launchpad.json')
        f=open("../launchpad.json","r")

    elif os.path.exists('launchpad.json'):
        #print('File is launchpad.json')
        f=open("launchpad.json","r")

    elif os.path.exists(ljpath+'/../../libs/launchpad.json'):
        #print('File is '+ljpath+'/../../libs/launchpad.json')
        f=open(ljpath+"/../../libs/launchpad.json","r")

    s = f.read()
    macros = json.loads(s)
    print(len(macros['OS']),"Macros")
    nbmacro = len(macros[gstt.LaunchpadLayers[gstt.LaunchpadLayer]])
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
    #print ("topmacro", topbutton, "value", value)
    if value == 127:
        TopUpdate(topbutton-1, 127)
        Disp("M1")
        Disp('M1', 'bhoreal')
    ModeCallback = Maxwell1Callback


 
#ComputerUpdate(computer)
LoadMacros()
SendOSC(gstt.TouchOSCIP, gstt.TouchOSCPort, '/pad/status', ['Running'])



#
# Notes Macros
#

'''
def ModeNote(arg):
    global ModeCallback


    topbutton, value = arg
    if value == 127:
        TopUpdate(topbutton-1,20)
        Disp("No")
        Disp('te','bhoreal')
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
        SendOSC(gstt.computerIP[computer-1],gstt.maxwellatorPort,'/note',[BhorNoteXY(x,y),velocity])

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
        Disp('CC', 'bhoreal')
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
        Disp('Os', 'bhoreal')
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
        print("code : ",macros['OS'][macronumber]["code"])
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
        Disp('no', 'bhoreal')
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
# Maxwell 1 : Left
#


def ModeMaxwell1(arg):
    global ModeCallback

    topbutton, value = arg
    if value == 127:
        print("matrix1", matrix1)
        TopUpdate(topbutton-1,20)
        Disp('M1')
        Disp('M1', 'bhoreal')
        print("Mode Maxwell1")
        ModeCallback = "Maxwell1Callback"

    else:
        ClsMatrix()
        print("matrix1", matrix1, matrix1[0], matrix1[1])
        PadNoteOnXY(matrix1[0],matrix1[1],20)



def Maxwell1Callback(arg):

    ClsMatrix()
    x,y,velocity = arg
    #print(x,y)
    matrix1 = [x,y]
    print("matrix1", matrix1)
    PadNoteOnXY(x,y,20)
    #print ('Macros OS', BhorNoteXY(x,y), "velocity", velocity )
    macroname = 'm'+str(y)+str(x)
    macronumber = findMacros(macroname,'Maxwell1')
    if macronumber != -1:
        macro = macros['Maxwell1'][macronumber]["code"]
        print("Maxwell1 Callback :",macro)
        if macro.count('/') > 0:
            if macro.find('left') ==0:
                maxwellccs.current["pathLeft"]= macro
                print("New pathLeft", maxwellccs.current["pathLeft"])
            else:
                maxwellccs.current["path"]= macro
                print("New path", maxwellccs.current["path"])

            print("matrix1", matrix1)      
        else:
            #print(macro+"("+str(velocity)+")")
            eval(macro+"("+str(velocity)+")")
    else:
        print("no callback")
    
    #SendOSC('127.0.0.1', monomePort, prefix+'/press', (x,y,1))
    #SendOSC('127.0.0.1', monomePort, prefix+'/grid/key', (x,y,1))


#
# Maxwell 2 : Right
#


def ModeMaxwell2(arg):
    global ModeCallback

    topbutton, value = arg
    if value == 127:
        TopUpdate(topbutton-1,20)
        Disp('M2')
        Disp('M2', 'bhoreal')
        print("Mode Maxwell2")
        ModeCallback = "Maxwell2Callback"

    else:
        ClsMatrix()
        PadNoteOnXY(matrix2[0],matrix2[1],20)



def Maxwell2Callback(arg):

    ClsMatrix()
    x,y,velocity = arg
    matrix2 = [x,y]
    PadNoteOnXY(x,y,20)
    #print ('Macros OS', BhorNoteXY(x,y), "velocity", velocity )
    macroname = 'm'+str(y)+str(x)
    macronumber = findMacros(macroname,'Maxwell2')
    if macronumber != -1:
        macro = macros['Maxwell2'][macronumber]["code"]
        print("Maxwell2 Callback : ",macro)
        if macro.count('/') > 0:
            if macro.find('right') ==0:
                maxwellccs.current["pathRight"]= macro
                print("New pathRight", maxwellccs.current["pathRight"])
            else:
                maxwellccs.current["path"]= macro
                print("New path", maxwellccs.current["path"])
        else:
            #print(macro+"("+str(velocity)+")")
            eval(macro+"("+str(velocity)+")")
    else:
        print("no callback")
    
    #SendOSC('127.0.0.1', monomePort, prefix+'/press', (x,y,1))
    #SendOSC('127.0.0.1', monomePort, prefix+'/grid/key', (x,y,1))
    


#
# Maxwell 3 : Right
#


def ModeMaxwell3(arg):
    global ModeCallback

    topbutton, value = arg
    if value == 127:
        TopUpdate(topbutton-1,20)
        Disp('M3')
        Disp('M3', 'bhoreal')
        print("Mode Maxwell3")
        ModeCallback = "Maxwell3Callback"

    else:
        ClsMatrix()
        PadNoteOnXY(matrix3[0],matrix3[1],20)



def Maxwell3Callback(arg):

    ClsMatrix()
    x,y,velocity = arg
    matrix3 = [x,y]
    PadNoteOnXY(x,y,20)
    #print ('Macros OS', BhorNoteXY(x,y), "velocity", velocity )
    macroname = 'm'+str(y)+str(x)
    macronumber = findMacros(macroname,'Maxwell3')
    if macronumber != -1:
        macro = macros['Maxwell3'][macronumber]["code"]
        print("Maxwell3 Callback : ",macro)
        if macro.count('/') > 0:
            maxwellccs.current["path"]= macro
            print("New path", maxwellccs.current["path"]) 
        else:
            #print(macro+"("+str(velocity)+")")
            eval(macro+"("+str(velocity)+")")
    else:
        print("no callback")
    
    #SendOSC('127.0.0.1', monomePort, prefix+'/press', (x,y,1))
    #SendOSC('127.0.0.1', monomePort, prefix+'/grid/key', (x,y,1))
    



#
# StartMode 
#

def ModeNo(arg):
    x,y,velocity = arg
    PadNoteOnXY(x,y,20)
    print ('Mode No x',x,'y',y,"note", PadNoteXY(x,y))


def Mode(mode):
    global macros

    
    if mode == "maxwell":
        print("Launchpad in Maxwell mode")
        macros = maxwellmacros.buttons

    if mode == "generic":
        print("Launchpad in generic mode")
        macros = generic


#
# Right column functions
# 

def RightMacro(number):

    print ("rightmacro",number)




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