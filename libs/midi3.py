#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Midi3
v0.7.0

Midi Handler : 

- Hook to the MIDI host
- Enumerate connected midi devices and spawn a process/device to handle incoming events
- Provide sending functions to 
    - found midi devices with IN port
    - OSC targets /noteon /noteoff /cc (see midi2OSC).
- Launchpad mini led matrix from/to, see launchpad.py
- Bhoreal led matrix from/to, see bhoreal.py


todo :

Midi macros : plusieurs parametres evoluant les uns apres les autres ou en meme temps.
cadence

by Sam Neurohack 
from /team/laser

for python 2 & 3

Laser selection 
one universe / laser

Plugin selection 
bank change/scene/


"""


import time

import rtmidi
from rtmidi.midiutil import open_midiinput 
from threading import Thread
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF,
                                  PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE)
import mido
from mido import MidiFile
import traceback
import weakref
import sys
from sys import platform

print()
print('Midi startup...')

import gstt, bhoreal, launchpad, LPD8
from queue import Queue
#from OSC3 import OSCServer, OSCClient, OSCMessage


midiname = ["Name"] * 16
midiport = [rtmidi.MidiOut() for i in range(16) ]

OutDevice = [] 
InDevice = []

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


clock = mido.Message(type="clock")

start = mido.Message(type ="start")
stop = mido.Message(type ="stop")
ccontinue = mido.Message(type ="continue")
reset = mido.Message(type ="reset")
songpos = mido.Message(type ="songpos")

mode = "maxwell"

'''
print("clock",clock)
print("start",start)
print("continue", ccontinue)
print("reset",reset)
print("sonpos",songpos)
'''

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

# OSC targets list
midi2OSC = {
      "lj": {"oscip": "127.0.0.1", "oscport": 8002, "notes": False, "msgs": False},
      "nozoid": {"oscip": "127.0.0.1", "oscport": 8003, "notes": False, "msgs": False},
      "dump": {"oscip": "127.0.0.1", "oscport": 8040, "notes": True, "msgs": True},
      "maxwell": {"oscip": "127.0.0.1", "oscport": 8012, "notes": True, "msgs": True}
      }

notes = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
def midi2note(midinote):

    print("midinote",midinote, "note", notes[midinote%12]+str(round(midinote/12)))
    return notes[midinote%12]+str(round(midinote/12))


#mycontroller.midiport[LaunchHere].send_message([CONTROLLER_CHANGE, LaunchTop[number-1], color])

def send(msg,device):

    '''
    # if device is the midi name
    if device in midiname:
        deviceport = midiname.index(device)
        midiport[deviceport].send_message(msg)
    '''
    if device == "Launchpad":
        #print LaunchHere
        midiport[launchpad.Here].send_message(msg)

    if device == "Bhoreal":
        midiport[bhoreal.Here].send_message(msg)

# mididest : all, launchpad, bhoreal, specificname
def NoteOn(note,color, mididest):
    global MidInsNumber

    gstt.note = note
    gstt.velocity = color
    
    for port in range(MidInsNumber):

        # To Launchpad, if present.
        if mididest == "launchpad" and midiname[port].find(LaunchMidiName) == 0:
            launchpad.PadNoteOn(note%64,color)

        # To Bhoreal, if present.
        elif mididest == "bhoreal" and midiname[port].find(BhorealMidiName) == 0:
            gstt.BhorLeds[note%64]=color
            midiport[port].send_message([NOTE_ON, note%64, color])
            #bhorosc.sendosc("/bhoreal", [note%64 , 0])

        # To mididest
        elif midiname[port].find(mididest) == 0:
            midiport[port].send_message([NOTE_ON, note, color])

        # To All 
        elif mididest == "all" and midiname[port].find(mididest) != 0 and  midiname[port].find(BhorealMidiName) != 0 and midiname[port].find(LaunchMidiName) != 0:
            midiport[port].send_message([NOTE_ON, note, color])

        #virtual.send_message([NOTE_ON, note, color])

    for OSCtarget in midi2OSC:
        if (OSCtarget == mididest or mididest == 'all') and midi2OSC[OSCtarget]["notes"]:
            OSCsend(OSCtarget, "/noteon", [note, color])

# mididest : all, launchpad, bhoreal, specificname 
def NoteOff(note, mididest):
    global MidInsNumber

    gstt.note = note
    gstt.velocity = 0

    for port in range(MidInsNumber):

        # To Launchpad, if present.
        if mididest == "launchpad" and midiname[port].find(LaunchMidiName) == 0:
            launchpad.PadNoteOff(note%64)

        # To Bhoreal, if present.
        elif mididest == "bhoreal" and midiname[port].find(BhorealMidiName) == 0:
            midiport[port].send_message([NOTE_OFF, note%64, 0])
            gstt.BhorLeds[note%64] = 0
            #bhorosc.sendosc("/bhoreal", [note%64 , 0])

        # To mididest
        elif midiname[port].find(mididest) != -1:
            midiport[port].send_message([NOTE_OFF, note, 0])

        # To All 
        elif mididest == "all" and midiname[port].find(mididest) == -1 and  midiname[port].find(BhorealMidiName) == -1 and midiname[port].find(LaunchMidiName) == -1:
                midiport[port].send_message([NOTE_OFF, note, 0])
        
        #virtual.send_message([NOTE_OFF, note, 0])

    for OSCtarget in midi2OSC:
        if (OSCtarget == mididest or mididest == 'all') and midi2OSC[OSCtarget]["notes"]:
            OSCsend(OSCtarget, "/noteoff", note)


# mididest : all or specifiname, won't be sent to launchpad or Bhoreal.
def MidiMsg(midimsg, mididest):
    #print("MidiMsg", midimsg, "Dest", mididest)

    for port in range(MidInsNumber):
        ##print("port",port,"midiname", midiname[port])
        
        # To mididest
        if midiname[port].find(mididest) != -1:
            #print("sending to name", midiname[port],midimsg)
            midiport[port].send_message(midimsg)

        # To All 
        elif mididest == "all" and midiname[port].find(mididest) == -1 and  midiname[port].find(BhorealMidiName) == -1 and midiname[port].find(LaunchMidiName) == -1:
            #print("all sending to port",port,"name", midiname[port])
            midiport[port].send_message(midimsg)

    for OSCtarget in midi2OSC:
        if (OSCtarget == mididest or mididest == 'all') and midi2OSC[OSCtarget]["msgs"]:
             OSCsend(OSCtarget, "/cc", [midimsg[1], midimsg[2]])


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
            print("Midi OSCSend : sending", oscmsg,"to", name, "at", ip , ":", port)
        
        osclient.sendto(oscmsg, (ip, port))
        oscmsg.clearData()   
        return True

    except:
        if gstt.debug > 0:
            print('Midi OSCSend : Connection to IP', ip ,':', port,'refused : died ?')
        #sendWSall("/status No plugin.")
        #sendWSall("/status " + name + " is offline")
        #sendWSall("/" + name + "/start 0")
        #PluginStart(name)
        return False

def Webstatus(message):
    OSCsend("lj","/status", message)

#
# MIDI Startup and handling
#
      
mqueue  = Queue()
inqueue = Queue()

#
# Events from Generic MIDI Handling
#
'''
def midinProcess(midiqueue):

    midiqueue_get = midiqueue.get
    while True:
        msg = midiqueue_get()
        print("midin ", msg)
        time.sleep(0.001)
'''
# Event from Bhoreal or Launchpad
# Or it could be the midinprocess in launchpad.py or bhoreal.py
def MidinProcess(inqueue, portname):

    inqueue_get = inqueue.get
    mididest = "to Maxwell 1"
    while True:
        time.sleep(0.001)
        msg = inqueue_get()
        #print("Midinprocess", msg[0])
        
        # Note On
        if msg[0]==NOTE_ON:
            print ("from", portname, "noteon", msg[1])
            NoteOn(msg[1],msg[2],mididest)
            # Webstatus(''.join(("note ",msg[1]," to ",msg[2])))
                
        # Note Off
        if msg[0]==NOTE_OFF:
            print("from", portname,"noteoff")
            NoteOff(msg[1],msg[2], mididest)
            # Webstatus(''.join(("note ",msg[1]," to ",msg[2])))
                
        # Midi CC message          
        if msg[0] == CONTROLLER_CHANGE:
            print("from", portname,"CC :", msg[1], msg[2])
            '''
            Webstatus("CC :" + str(msg[1]) + " " + str(msg[2]))
            for OSCtarget in midi2OSC:
                if OSCtarget["notes"]:
                    pass
                    #OSCsend(OSCtarget, "/CC", note)
            '''
        # other midi message  
        if msg[0] != NOTE_OFF and  msg[0] != NOTE_ON and msg[0] != CONTROLLER_CHANGE:
            print("from", portname,"other midi message")
            MidiMsg(msg[0],msg[1],msg[2],mididest)
            # Webstatus(''.join(("msg : ",msg[0],"  ",msg[1],"  ",msg[2])))

       
# Generic call back : new msg forwarded to queue 
class AddQueue(object):
    def __init__(self, portname, port):
        self.portname = portname
        self.port = port
        #print("AddQueue", port)
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        #print("inqueue : [%s] @%0.6f %r" % ( self.portname, self._wallclock, message))
        midinputsqueue[self.port].put(message)


#    
# MIDI OUT Handling
#


class OutObject():

    _instances = set()
    counter = 0

    def __init__(self, name, kind, port):

        self.name = name
        self.kind = kind
        self.port = port
        
        self._instances.add(weakref.ref(self))
        OutObject.counter += 1

        print(self.name, "kind", self.kind, "port", self.port)

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
        OutObject.counter -= 1



def OutConfig():
    global midiout, MidInsNumber
    
    # 
    if len(OutDevice) == 0:
        print("")
        print("MIDIout...")
        print("List and attach to available devices on host with IN port :")
    
        # Display list of available midi IN devices on the host, create and start an OUT instance to talk to each of these Midi IN devices 
        midiout = rtmidi.MidiOut()
        available_ports = midiout.get_ports()
    
        for port, name in enumerate(available_ports):
    
            midiname[port]=name
            midiport[port].open_port(port)
            #print("Will send to [%i] %s" % (port, name))
            #MidIns[port][1].open_port(port)
                
            # Search for a Bhoreal
            if name.find(BhorealMidiName) == 0:
                
                OutDevice.append(OutObject(name, "bhoreal", port))
                print("Bhoreal start animation")
                bhoreal.Here = port
                bhoreal.StartBhoreal(port)
                time.sleep(0.2)
    
            # Search for a LaunchPad
            elif name.find(LaunchMidiName) == 0:
                
                OutDevice.append(OutObject(name, "launchpad", port))
                print("Launchpad mini start animation")
                launchpad.Here = port
                launchpad.StartLaunchPad(port)
                time.sleep(0.2)

            # Search for a LPD8
            elif name.find('LPD8') == 0:
                
                OutDevice.append(OutObject(name, "LPD8", port))
                #print("LPD8 mini start animation")
                LPD8.Here = port
                #LPD8.StartLPD8(port)
                time.sleep(0.2)

            # Search for a Guitar Wing
            elif name.find("Livid") == 0:
                OutDevice.append(OutObject(name, "livid", port))
                print("Livid Guitar Wing start animation")
                gstt.WingHere = port
                print(gstt.WingHere)
                
                #guitarwing.StartWing(port)
                time.sleep(0.2)    
            else:
                
                OutDevice.append(OutObject(name, "generic", port))
    
        #print("")      
        print(len(OutDevice), "Out devices")
        #ListOutDevice()
        MidInsNumber = len(OutDevice)+1

def ListOutDevice():

    for item in OutObject.getinstances():

        print(item.name)

def FindOutDevice(name):

    port = -1
    for item in OutObject.getinstances():
        #print("searching", name, "in", item.name)
        if name == item.name:
            #print('found port',item.port)
            port = item.port
    return port


def DelOutDevice(name):

    Outnumber = Findest(name)
    print('deleting OutDevice', name)

    if Outnumber != -1:
        print('found OutDevice', Outnumber)
        delattr(OutObject, str(name))
        print("OutDevice", Outnumber,"was removed")
    else:
        print("OutDevice was not found")



#    
# MIDI IN Handling 
# Create processing thread and queue for each device
#

class InObject():

    _instances = set()
    counter = 0

    def __init__(self, name, kind, port, rtmidi):

        self.name = name
        self.kind = kind
        self.port = port
        self.rtmidi = rtmidi
        self.queue = Queue()
        
        self._instances.add(weakref.ref(self))
        InObject.counter += 1

        #print("Adding InDevice name", self.name, "kind", self.kind, "port", self.port,"rtmidi", self.rtmidi, "Queue", self.queue)

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
        InObject.counter -= 1


def InConfig():

    print("")
    print("MIDIin...")
    print("List and attach to available devices on host with OUT port :")

    if platform == 'darwin':
        mido.set_backend('mido.backends.rtmidi/MACOSX_CORE')

    genericnumber = 0

    for port, name in enumerate(mido.get_input_names()):

        #print()
        # Maxwell midi IN & OUT port names are different 
        
        if name.find("from ") == 0:
            #print ("name",name)
            name = "to "+name[5:]
            #print ("corrected to",name)

        outport = FindOutDevice(name)
        midinputsname[port]=name
        
        #print("name",name, "Port",port, "Outport", outport)
        
        '''
        # New Bhoreal found ?
        if name.find(BhorealMidiName) == 0:

            try:
                bhorealin, port_name = open_midiinput(outport) # weird rtmidi call port number is not the same in mido enumeration and here

                BhoreralDevice = InObject(port_name, "bhoreal", outport, bhorealin)
                print("BhorealDevice.queue",BhoreralDevice.queue )
                # thread launch to handle all queued MIDI messages from Bhoreal device    
                thread = Thread(target=bhoreal.MidinProcess, args=(bhoreal.bhorqueue,))
                thread.setDaemon(True)
                thread.start()
                print("Attaching MIDI in callback handler to Bhoreal : ",  name, "port", port, "portname", port_name)
                BhoreralDevice.rtmidi.set_callback(bhoreal.AddQueue(port_name))
            except Exception:
                traceback.print_exc()

        '''
        # Old Bhoreal found ?
        if name.find(BhorealMidiName) == 0:

            try:
                bhorealin, port_name = open_midiinput(outport) # weird rtmidi call port number is not the same in mido enumeration and here
            except (EOFError, KeyboardInterrupt):
                sys.exit

            #midinputs.append(bhorealin)
            InDevice.append(InObject(name, "bhoreal", outport, bhorealin))
            # thread launch to handle all queued MIDI messages from Bhoreal device    

            thread = Thread(target=bhoreal.MidinProcess, args=(bhoreal.bhorqueue,))
            #thread = Thread(target=bhoreal.MidinProcess, args=(InDevice[port].queue,))
            thread.setDaemon(True)
            thread.start()
            #print("midinputs[port]", midinputs[port])
            print(name)
            InDevice[port].rtmidi.set_callback(bhoreal.AddQueue(name))
            #midinputs[port].set_callback(bhoreal.AddQueue(name))

        '''

        # New LaunchPad Mini Found ?
        if name.find(LaunchMidiName) == 0:
   
            
            try:
                launchin, port_name = open_midiinput(outport)
            except (EOFError, KeyboardInterrupt):
                sys.exit()

            LaunchDevice = InObject(port_name, "launchpad", outport, launchin)
            thread = Thread(target=launchpad.MidinProcess, args=(launchpad.launchqueue,))
            thread.setDaemon(True)
            thread.start()
            print("Attaching MIDI in callback handler to Launchpad : ", name, "port", port, "portname", port_name)
            LaunchDevice.rtmidi.set_callback(launchpad.LaunchAddQueue(name))

        '''
 
        # Old LaunchPad Mini Found ?
        if name.find(LaunchMidiName) == 0:
   
            
            try:
                launchin, port_name = open_midiinput(outport)
            except (EOFError, KeyboardInterrupt):
                sys.exit()
            #midinputs.append(launchin)
            InDevice.append(InObject(name, "launchpad", outport, launchin))

            thread = Thread(target=launchpad.MidinProcess, args=(launchpad.launchqueue,))
            #thread = Thread(target=launchpad.MidinProcess, args=(InDevice[port].queue,))
            thread.setDaemon(True)
            thread.start()
            print(name, "port", port, "portname", port_name)
            InDevice[port].rtmidi.set_callback(launchpad.LaunchAddQueue(name))
            #launchin.set_callback(launchpad.LaunchAddQueue(name))

 
        # LPD8 Found ?
        if name.find('LPD8') == 0:
   
            print()
            print('LPD8 Found..')
            
            try:
                LPD8in, port_name = open_midiinput(outport)
            except (EOFError, KeyboardInterrupt):
                sys.exit()
            #midinputs.append(LPD8in)
            InDevice.append(InObject(name, "LPD8", outport, LPD8in))
            print ("Launching LPD8 thread..")
            thread = Thread(target=LPD8.MidinProcess, args=(LPD8.LPD8queue,))
            #thread = Thread(target=LPD8.MidinProcess, args=(InDevice[port].queue,))
            thread.setDaemon(True)
            thread.start()
            print(name, "port", port, "portname", port_name)
            InDevice[port].rtmidi.set_callback(LPD8.LPD8AddQueue(name))
  

        # Everything that is not Bhoreal or Launchpad
        if name.find(BhorealMidiName) != 0 and name.find(LaunchMidiName) != 0 and name.find('LPD8') != 0:

            try:
                #print (name, name.find("RtMidi output"))
                if name.find("RtMidi output") > -1:
                    print("No thread started for device", name)
                else:
                    portin = object
                    port_name = ""
                    portin, port_name = open_midiinput(outport)
                    #midinputs.append(portin)
                    InDevice.append(InObject(name, "generic", outport, portin))
                    
                    thread = Thread(target=MidinProcess, args=(midinputsqueue[port],port_name))
                    thread.setDaemon(True)
                    thread.start() 

                    print(name, "port", port, "portname", port_name)
                    #midinputs[port].set_callback(AddQueue(name),midinputsqueue[port])
                    #midinputs[port].set_callback(AddQueue(name))
                    #genericnumber += 1
                    InDevice[port].rtmidi.set_callback(AddQueue(name,port))

            except Exception:
                traceback.print_exc()
                        
    #print("")      
    print(InObject.counter, "In devices")
    #ListInDevice()


def ListInDevice():

    for item in InObject.getinstances():

        print(item.name)

def FindInDevice(name):

    port = -1
    for item in InObject.getinstances():
        #print("searching", name, "in", item.name)
        if name in item.name:
            #print('found port',item.port)
            port = item.port
    return port


def DelInDevice(name):

    Innumber = Findest(name)
    print('deleting InDevice', name)

    if Innumber != -1:
        print('found InDevice', Innumber)
        delattr(InObject, str(name))
        print("InDevice", Innumber,"was removed")
    else:
        print("InDevice was not found")


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

def End():
    global midiout
    
    #midiin.close_port()
    midiout.close_port()
  
    #del virtual
    if launchpad.Here != -1:
        del launchpad.Here
    if bhoreal.Here  != -1:
        del bhoreal.Here
    if LPD8.Here  != -1:
        del LPD8.Here


def listdevice(number):
	
	return midiname[number]
	
def check():

    OutConfig()
    InConfig()
    
    #return listdevice(255)
	
	