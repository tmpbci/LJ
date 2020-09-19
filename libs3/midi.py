#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
LJay/LJ
v0.7.0

Midi Handler 

Deprecated, see midi3

by Sam Neurohack 
from /team/laser

"""

print "importing midi 0"
import time

import rtmidi
from rtmidi.midiutil import open_midiinput 
from threading import Thread
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF,
                                  PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)
import mido
from mido import MidiFile
#import mido
import sys
from serial.tools import list_ports
import serial

from sys import platform
import gstt

# import bhoroscp

import bhoreal
import launchpad
from OSC import OSCServer, OSCClient, OSCMessage
#import orbits


midiname = ["Name"] * 16
midiport = [rtmidi.MidiOut() for i in range(16) ]



is_py2 = sys.version[0] == '2'
if is_py2:
    from Queue import Queue
else:
    from queue import Queue

# max 16 midi port array 

midinputsname = ["Name"] * 16
midinputsqueue = [Queue() for i in range(16) ]
midinputs = []


BhorealMidiName = "Bhoreal"
LaunchMidiName = "Launch"

BhorealPort, Midi1Port, Midi2Port, VirtualPort, MPort = -1,-1,-1, -1, -1
VirtualName = "LaunchPad Mini"
Mser = False

# Myxolidian 3 notes chords list
Myxo = [(59,51,54),(49,52,56),(49,52,56),(51,54,57),(52,56,59),(52,56,59),(54,57,48),(57,49,52)]
MidInsNumber = 0

try:
    input = raw_input
except NameError:
    # Python 3
    StandardError = Exception


STATUS_MAP = {
    'noteon': NOTE_ON,
    'noteoff': NOTE_OFF,
    'programchange': PROGRAM_CHANGE,
    'controllerchange': CONTROLLER_CHANGE,
    'pitchbend': PITCH_BEND,
    'polypressure': POLY_PRESSURE,
    'channelpressure': CHANNEL_PRESSURE
}

# OSC destination list for incoming midi
midi2OSC = {
      "lj": {"oscip": "127.0.0.1", "oscport": 8002, "notes": False, "msgs": False},
      "nozoid": {"oscip": "127.0.0.1", "oscport": 8003, "notes": False, "msgs": False},
      "dump": {"oscip": "127.0.0.1", "oscport": 8040, "notes": True, "msgs": True}
      }



#mycontroller.midiport[LaunchHere].send_message([CONTROLLER_CHANGE, LaunchTop[number-1], color])

def send(device,msg):

    '''
    # if device is the midi name
    if device in midiname:
        deviceport = midiname.index(device)
        midiport[deviceport].send_message(msg)
    '''
    if device == "Launchpad":
        #print LaunchHere
        midiport[gstt.LaunchHere].send_message(msg)

    if device == "Bhoreal":
        midiport[gstt.BhorealHere].send_message(msg)

def NoteOn(note, color):
    global MidInsNumber

    gstt.note = note
    gstt.velocity = color
    
    for port in range(MidInsNumber):

        if midiname[port].find(LaunchMidiName) == 0:
            launchpad.PadNoteOn(note%64,color)

        if midiname[port].find(BhorealMidiName) == 0:
            gstt.BhorLeds[note%64]=color
            midiport[port].send_message([NOTE_ON, note%64, color])
            #bhorosc.sendosc("/bhoreal", [note%64 , color])

        if midiname[port].find(BhorealMidiName) != 0 and midiname[port].find(LaunchMidiName) != 0:
            midiport[port].send_message([NOTE_ON, note, color])

        #virtual.send_message([NOTE_ON, note, color])

    for OSCtarget in midi2OSC:
        if midi2OSC[OSCtarget]['notes']:
            pass
            #OSCsend(OSCtarget, "/noteon", [note, color])

    
def NoteOff(note):
    global MidInsNumber

    gstt.note = note
    gstt.velocity = 0
    for port in range(MidInsNumber):

        if midiname[port].find(LaunchMidiName) == 0:
            launchpad.PadNoteOff(note%64)

        if midiname[port].find(BhorealMidiName) == 0:
            midiport[port].send_message([NOTE_OFF, note%64, 0])
            gstt.BhorLeds[note%64]=0
            #bhorosc.sendosc("/bhoreal", [note%64 , 0])

        if midiname[port].find(BhorealMidiName) != 0 and midiname[port].find(LaunchMidiName) != 0:
            midiport[port].send_message([NOTE_OFF, note, 0])
        #virtual.send_message([NOTE_OFF, note, 0])

    for OSCtarget in midi2OSC:
        if midi2OSC[OSCtarget]["notes"]:
            pass
            #OSCsend(OSCtarget, "/noteoff", note)



def MidiMsg(midimsg):

    print ("MidiMsg", midimsg)
    for port in range(MidInsNumber):
        if midiname[port].find(BhorealMidiName) != 0:
            midiport[port].send_message(midimsg)
  

def OSCsend(name, oscaddress, oscargs =''):


    ip = midi2OSC[name]["oscip"]
    port = midi2OSC[name]["oscport"]
    osclient = OSCClient()
    osclient.connect((ip, port)) 
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)

    try:
        if gstt.debug > 0:
            print("Midi OSCSend : sending", oscmsg, "to", name, "at", gstt.LjayServerIP, ":", PluginPort)
        osclient.sendto(oscmsg, (ip, port))
        oscmsg.clearData()
        #if gstt.debug >0:
        #   print oscaddress, oscargs, "was sent to",name     
        return True

    except:
        if gstt.debug > 0:
            print ('Midi OSCSend : Connection to IP', ip ,':', port,'refused : died ?')
        #sendWSall("/status No plugin.")
        #sendWSall("/status " + name + " is offline")
        #sendWSall("/" + name + "/start 0")
        #PluginStart(name)
        return False

def WebStatus(message):
    OSCsend("lj","/status", message)

#
# MIDI Startup and handling
#
      
mqueue  = Queue()
inqueue = Queue()

#
# Events from Generic MIDI Handling
#

def midinProcess(midiqueue):

    midiqueue_get = midiqueue.get
    while True:
        msg = midiqueue_get()
        print ("midin ", msg)
        time.sleep(0.001)

# Event from Bhoreal or Launchpad
def MidinProcess(inqueue):

    inqueue_get = inqueue.get
    while True:
        time.sleep(0.001)
        msg = inqueue_get()
        print ("Midinproces", msg[0])
        
        # Note On
        if msg[0]==NOTE_ON:
            NoteOn(msg[1],msg[2])
            #if bhorosc.oscdevice == 1:
            WebStatus(''.join(("note ",msg[1]," to ",msg[2])))
                
        # Note Off
        if msg[0]==NOTE_OFF:
            print ("noteoff")
            NoteOff(msg[1],msg[2])
            #if bhorosc.oscdevice == 1:
            WebStatus(''.join(("note ",msg[1]," to ",msg[2])))
                
        # Midi CC message          
        if msg[0] == CONTROLLER_CHANGE:
            print ("CC :", msg[1], msg[2])
            WebStatus("CC :" + str(msg[1]) + " " + str(msg[2]))
            #orbits.RotX(msg[2])
            for OSCtarget in midi2OSC:
                if OSCtarget["notes"]:
                    pass
                    #OSCsend(OSCtarget, "/CC", note)

        # other midi message  
        if msg[0] != NOTE_OFF and  msg[0] != NOTE_ON:

            MidiMsg(msg[0],msg[1],msg[2])
            #if bhorosc.oscdevice == 1:
            WebStatus(''.join(("msg : ",msg[0],"  ",msg[1],"  ",msg[2])))

       
# Generic call back : new msg forwarded to queue 
class AddQueue(object):
    def __init__(self, port):
        self.port = port
        print ("AddQueue", port)
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        inqueue.put(message)


#    
# MIDI OUT Handling
#

def OutConfig():
    global midiout, MidInsNumber
	
    print("")
    print("MIDIout...")
    print("List and attach to available devices on host with IN port :")

    # Display list of available midi IN devices on the host, create and start an OUT instance to talk to each of these Midi IN devices 
    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()

    for port, name in enumerate(available_ports):

        midiname[port]=name
        midiport[port].open_port(port)
        print("Will send to [%i] %s" % (port, name))
        #MidIns[port][1].open_port(port)
            
        # Search for a Bhoreal
        if name.find(BhorealMidiName) == 0:
            print("Bhoreal start animation")
            gstt.BhorealHere = port
            bhoreal.StartBhoreal(port)
            bhoreal.UpdateCurve()
            bhoreal.UpdateSet()
            bhoreal.UpdateLaser()
            bhoreal.UpdateSimu()
            time.sleep(0.2)

        # Search for a LaunchPad
        if name.find(LaunchMidiName) == 0:
            print("Launchpad mini start animation")
            gstt.LaunchHere = port
            print(gstt.LaunchHere)
            launchpad.StartLaunchPad(port)
            time.sleep(0.2)

        # Search for a Guitar Wing
        if name.find("Livid") == 0:
                print("Livid Guitar Wing start animation")
                gstt.WingHere = port
                print(gstt.WingHere)
                #guitarwing.StartWing(port)
                time.sleep(0.2)        

    print ("")     
    MidInsNumber = port+1


#    
# MIDI IN Handling 
# Create processing thread and queue for each device
#
def InConfig():

    print("")
    print("MIDIin...")
    print("List and attach to available devices on host with OUT port :")
    if  platform == 'darwin':
        mido.set_backend('mido.backends.rtmidi/MACOSX_CORE')
    for port, name in enumerate(mido.get_input_names()):

        #print (name)
        midinputsname[port]=name
        print(port,name)
        
        # Bhoreal found ?
        if name.find(BhorealMidiName) == 0:

            # thread launch to handle all queued MIDI messages from Bhoreal device    
            thread = Thread(target=bhoreal.MidinProcess, args=(bhoreal.bhorqueue,))
            thread.setDaemon(True)
            thread.start()
            try:
                bhorealin, port_name = open_midiinput(port+1) # weird rtmidi call port number is not the same in mido enumeration and here
            except (EOFError, KeyboardInterrupt):
                sys.exit()

            midinputs.append(bhorealin)
            print("Attaching MIDI in callback handler to Bhoreal : ", name)
            midinputs[port].set_callback(bhoreal.AddQueue(name))
            print("Bhor",port,port_name)
        
        # LaunchPad Mini Found ?
        if name.find(LaunchMidiName) == 0:

            # thread launch to handle all queued MIDI messages from LauchPad device    
            thread = Thread(target=launchpad.LaunchMidinProcess, args=(launchpad.launchqueue,))
            thread.setDaemon(True)
            thread.start()
            try:
                launchin, port_name = open_midiinput(port+1) # weird port number is not the same in mido enumeration and here
            except (EOFError, KeyboardInterrupt):
                sys.exit()

            midinputs.append(launchin)
            print ("Attaching MIDI in callback handler to Launchpad : ", name)
            launchin.set_callback(launchpad.LaunchAddQueue(name))
            #print "Launch",port,port_name
        
        # all other devices

        '''
        

        port = mido.open_ioport(name,callback=AddQueue(name))
        
        This doesn't work on OS X on French system "Réseau Session" has a bug with accent.
        Todo : stop using different midi framework.
        
        if name.find(BhorealMidiName) != 0 and name.find(LaunchMidiName) != 0:
            thread = Thread(target=midinProcess, args=(midinputsqueue[port],))
            thread.setDaemon(True)
            thread.start()    
            try:
                port = mido.open_ioport(name,callback=AddQueue(name))
                #port_port, port_name = open_midiinput(port)
            except (EOFError, KeyboardInterrupt):
                sys.exit()

            #midinputs.append(port_port)
            print "Attaching MIDI in callback handler to : ", name
            #midinputs[port].set_callback(AddQueue(name))
            #MIDInport = mido.open_ioport("Laser",virtual=True,callback=MIDIn)
            
        '''
   
        if name.find(BhorealMidiName) != 0 and name.find(LaunchMidiName) != 0:
            thread = Thread(target=midinProcess, args=(midinputsqueue[port],))
            thread.setDaemon(True)
            thread.start()    
                     
 
            try:
                port_port, port_name = open_midiinput(port)
            except (EOFError, KeyboardInterrupt):
                sys.exit()

            midinputs.append(port_port)
            print("Attaching MIDI in callback handler to : ", name)
            midinputs[port].set_callback(AddQueue(name))
            #MIDInport = mido.open_ioport("Laser",virtual=True,callback=MIDIn)
            

def End():
    global midiout
    
    #midiin.close_port()
    midiout.close_port()
  
    #del virtual
    if gstt.LaunchHere != -1:
        del gstt.LaunchHere
    if gstt.BhorealHere  != -1:
        del gstt.BhorealHere


def listdevice(number):
	
	return midiname[number]
	
def check():

    InConfig()
    OutConfig()
    #return listdevice(255)
	
	