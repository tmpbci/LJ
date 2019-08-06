# coding=UTF-8
"""
Bhoreal
v0.7.0
Bhoreal Led matrix Handler 

Start a dedicated thread to handle incoming events from launchpad.

Cls()
AllColor(color) 
StarttBhoreal(port)  : Start animation 

Led Matrix can be access with X and Y coordinates and as midi note (0-63)

NoteOn(note,color)
NoteOff(note)
NoteOnXY(x,y,color):
NoteOffXY(x,y):
NoteXY(x,y):

gstt.BhorLeds[] array stores matrix current state

by Sam Neurohack 
from /team/laser

"""

import time
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF,
                                  PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)
import gstt, midi3
import sys

gstt.BhorLeds = [0]*65


Here = -1
from queue import Queue

def NoteOn(note,color):
    
    print ("bhoreal noteon", note, color)
    msg = [NOTE_ON, note, color]
    midi3.send(msg,"Bhoreal")
    gstt.BhorLeds[note]=color
    
def NoteOff(note):
    msg = [NOTE_OFF, note, 0]
    midi3.send(msg,"Bhoreal")
    gstt.BhorLeds[note]=0


def NoteOnXY(x,y,color):
    #print x,y
    msg = [NOTE_ON, NoteXY(x,y), color]
    midi3.send(msg,"Bhoreal")
    gstt.BhorLeds[NoteXY(x,y)]=color
    
def NoteOffXY(x,y):
    msg = [NOTE_OFF, NoteXY(x,y), 0]
    midi3.send(msg,"Bhoreal")
    gstt.BhorLeds[NoteXY(x,y)]=0


# Leds position are humans numbers 1-8. So -1 for pythonic array position 0-7
def NoteXY(x,y):
    note = (x -1)+ (y-1) * 8 
    return note

def Index(note):
    y=note/8
    x=note%8
    #print "Note : ",note
    #print "BhorIndex : ", x+1,y+1
    return int(x+1),int(y+1)

#    
# Bhoreal Start anim
#

# AllColor for bhoreal on given port

def AllColor(port,color):
    for led in range(0,64,1):
        msg = [NOTE_ON, led, color]
        midi3.send(msg,"Bhoreal")
 
# Cls for bhoreal on given port

def Cls(port):
    for led in range(0,64,1):
        msg = [NOTE_OFF, led, 0]
        midi3.send(msg,"Bhoreal")



def StartBhoreal(port):

    Cls(port)
    time.sleep(0.2)
    for color in range(0,126,1):
        AllColor(port,color)
        time.sleep(0.02)
    time.sleep(0.2)
    Cls(port)



def UpdateLine(line,newval):
    if gstt.BhorealHere  != -1:
        for led in range(8):
            NoteOffXY(led,line)
    
        NoteOnXY(newval,line,64)



# Update Laser 
def Noteon_Update(note):

    '''
    # forward new instruction ? 
    if gstt.MyLaser != gstt.Laser:
        doit = jumplaser.get(gstt.Laser)
        doit("/noteon",note)
    '''
    # 

 
    if note < 8:
        pass

    # 
    if note > 7 and note < 16:
        pass

    # 
    if  note > 15 and note < 24:
        pass

    # change current simulator PL
    if  note > 23 and note < 32:
        pass

    if note == 57 or note == 58:
        pass

    if note > 58:
        pass

'''
# todo 57  Color mode : Rainbow 
#      58  Color mode : RGB 

# Notes for Curve :  0-7
def UpdateCurve():
    print ("New Curve :", gstt.Curve)
    if gstt.BhorealHere  != -1:
        for led in range(0,8):
            NoteOff(led)
        NoteOn(gstt.Curve,20)
        
# Notes for set :  8-15 
def UpdateSet():
    print ("New Set :", gstt.Set)
    if gstt.BhorealHere  != -1:
        for led in range(9,17):
            NoteOff(led)
        NoteOn(gstt.Set+8,10)

# Note for current laser :  16-23 
def UpdateLaser():
    print ("New Laser :", gstt.Laser)
    if gstt.BhorealHere  != -1:
        for led in range(16,24):
            NoteOff(led)
        NoteOn(gstt.Laser+16,30)

# Note for PL displayed in pygame window :  24-31
def UpdateSimu():
    print ("New simuPL :", gstt.simuPL)
    if gstt.BhorealHere  != -1:
        for led in range(24,32):
            NoteOff(led)
        NoteOn(gstt.simuPL+24,40)
'''

#       
# Events from Bhoreal handling
#

# Process events coming from Bhoreal in a separate thread.
def MidinProcess(bhorqueue):

    #print()
    #print("bhoreal midi in process started with queue", bhorqueue)
    #print()
    bhorqueue_get = bhorqueue.get  
    while True:
    
        msg = bhorqueue_get()

        # Bhoreal Led pressed
        print ("Bhoreal Matrix : ", str(msg[1]), gstt.BhorLeds[msg[1]])

        if msg[0] == NOTE_ON and msg[2] == 64:
            # led 
            NoteOn(msg[1],64)

        # Bhoreal Led depressed
        elif msg[0] == NOTE_ON and msg[2] == 0:
            NoteOn(msg[1],0)

        '''
        
            print "Bhoreal Matrix : ", str(msg[1]), str(gstt.BhorLeds[msg[1]])
            
            if msg[1]< 8:
                gstt.Curve = msg[1]
                UpdateCurve()
            
            if msg[1]> 7 and msg[1] < 16:
                gstt.Set = msg[1]-8
                UpdateSet()

            if msg[1]> 15 and msg[1] < 24:
                gstt.Laser = msg[1]-16
                UpdateLaser()

            if msg[1]> 23 and msg[1] < 31:  
                gstt.simuPL = msg[1]-24
                UpdateSimu()

            #Bhoreal send back note on and off to light up the led.
            if msg[1]> 56:
                if gstt.BhorLeds[msg[1]] < 115:
                    gstt.BhorLeds[msg[1]] += 10
            #midi3.NoteOn(msg[1],gstt.BhorLeds[msg[1]])
            
            #time.sleep(0.1)
            #midi3.NoteOff(msg[1])
        '''
bhorqueue = Queue()


# New Bhoreal call back : new msg forwarded to Bhoreal queue 
class AddQueue(object):
    def __init__(self, portname):
        self.portname = portname
        self._wallclock = time.time()


    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.portname, self._wallclock, message))
        bhorqueue.put(message)
 
'''
# Old Bhoreal call back : new msg forwarded to Bhoreal queue 
class AddQueue(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        bhorqueue.put(message)
'''
