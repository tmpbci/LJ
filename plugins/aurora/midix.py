
#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Midi3 light version for soundt/Jamidi/clapt
v0.7.0

Midi Handler : 

- Hook to the MIDI host
- Enumerate connected midi devices and spawn a process/device to handle incoming events

by Sam Neurohack 
from /team/laser

Midi conversions from https://github.com/craffel/pretty-midi

"""

import time
from threading import Thread

import rtmidi
from rtmidi.midiutil import open_midiinput 
from rtmidi.midiconstants import (CHANNEL_PRESSURE, CONTROLLER_CHANGE, NOTE_ON, NOTE_OFF,
                                  PITCH_BEND, POLY_PRESSURE, PROGRAM_CHANGE, TIMING_CLOCK, SONG_CONTINUE, SONG_START, SONG_STOP)
import mido
from mido import MidiFile

import traceback
import weakref
import sys
from sys import platform
import os
import re
from collections import deque
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
    from queue import Queue
    from OSC import OSCServer, OSCClient, OSCMessage
else:
    from queue import Queue
    from OSC3 import OSCServer, OSCClient, OSCMessage


print("")

midiname = ["Name"] * 16
midiport = [rtmidi.MidiOut() for i in range(16) ]

OutDevice = [] 
InDevice = []

midisync = True

# max 16 midi port array 

midinputsname = ["Name"] * 16
midinputsqueue = [Queue() for i in range(16) ]
midinputs = []

# False = server / True = Client
gstt.clientmode = False

#Mser = False

MidInsNumber = 0


clock = mido.Message(type="clock")

start = mido.Message(type ="start")
stop = mido.Message(type ="stop")
ccontinue = mido.Message(type ="continue")
reset = mido.Message(type ="reset")
songpos = mido.Message(type ="songpos")

#mode = "maxwell"

'''
print "clock",clock)
print "start",start)
print "continue", ccontinue)
print "reset",reset)
print "sonpos",songpos)
'''

try:
    input = raw_input
except NameError:
    # Python 3
    Exception = Exception


STATUS_MAP = {
    'noteon': NOTE_ON,
    'noteoff': NOTE_OFF,
    'programchange': PROGRAM_CHANGE,
    'controllerchange': CONTROLLER_CHANGE,
    'pitchbend': PITCH_BEND,
    'polypressure': POLY_PRESSURE,
    'channelpressure': CHANNEL_PRESSURE
}


def SendAU(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclientlj = OSCClient()
    osclientlj.connect((gstt.myIP, 8090)) 

    # print("MIDI Aurora sending itself OSC :", oscmsg, "to localhost:8090")
    try:
        osclientlj.sendto(oscmsg, (gstt.myIP, 8090))
        oscmsg.clearData()
    except:
        log.err('Connection to Aurora refused : died ?')
        pass
    #time.sleep(0.001

def SendUI(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclientlj = OSCClient()
    osclientlj.connect((gstt.TouchOSCIP, gstt.TouchOSCPort)) 

    #print("MIDI Aurora sending UI :", oscmsg, "to",gstt.TouchOSCIP,":",gstt.TouchOSCPort)
    try:
        osclientlj.sendto(oscmsg, (gstt.TouchOSCIP, gstt.TouchOSCPort))
        oscmsg.clearData()
    except:
        log.err('Connection to Aurora UI refused : died ?')
        pass
    #time.sleep(0.001


def GetTime():
  return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

notes = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
def midi2note(midinote):

    print("midinote",midinote, "note", notes[midinote%12]+str(round(midinote/12)))
    return notes[midinote%12]+str(round(midinote/12))


def note2midi(note_name):
    """Converts a note name in the format
    ``'(note)(accidental)(octave number)'`` (e.g. ``'C#4'``) to MIDI note
    number.
    ``'(note)'`` is required, and is case-insensitive.
    ``'(accidental)'`` should be ``''`` for natural, ``'#'`` for sharp and
    ``'!'`` or ``'b'`` for flat.
    If ``'(octave)'`` is ``''``, octave 0 is assumed.
    Parameters
    ----------
    note_name : str
        A note name, as described above.
    Returns
    -------
    note_number : int
        MIDI note number corresponding to the provided note name.
    Notes
    -----
        Thanks to Brian McFee.
    """

    # Map note name to the semitone
    pitch_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    # Relative change in semitone denoted by each accidental
    acc_map = {'#': 1, '': 0, 'b': -1, '!': -1}

    # Reg exp will raise an error when the note name is not valid
    try:
        # Extract pitch, octave, and accidental from the supplied note name
        match = re.match(r'^(?P<n>[A-Ga-g])(?P<off>[#b!]?)(?P<oct>[+-]?\d+)$',
                         note_name)

        pitch = match.group('n').upper()
        offset = acc_map[match.group('off')]
        octave = int(match.group('oct'))

    except:
        raise ValueError('Improper note format: {}'.format(note_name))
    # Convert from the extrated ints to a full note number
    return 12*(octave + 1) + pitch_map[pitch] + offset



def hz2midi(frequency):
    """Convert a frequency in Hz to a (fractional) note number.
    Parameters
    ----------
    frequency : float
        Frequency of the note in Hz.
    Returns
    -------
    note_number : float
        MIDI note number, can be fractional.
    """
    # MIDI note numbers are defined as the number of semitones relative to C0
    # in a 440 Hz tuning
    return 12*(np.log2(frequency) - np.log2(440.0)) + 69

def midi2hz(note_number):
    """Convert a (fractional) MIDI note number to its frequency in Hz.
    Parameters
    ----------
    note_number : float
        MIDI note number, can be fractional.
    Returns
    -------
    note_frequency : float
        Frequency of the note in Hz.
    """
    # MIDI note numbers are defined as the number of semitones relative to C0
    # in a 440 Hz tuning
    return 440.0*(2.0**((note_number - 69)/12.0))  

# /cc cc number value
def cc(midichannel, ccnumber, value, mididest):

    if gstt.debug>0:
        print("Midix sending Midi channel", midichannel, "cc", ccnumber, "value", value, "to", mididest)

    MidiMsg([CONTROLLER_CHANGE+midichannel-1, ccnumber, value], mididest)





#
# MIDI Startup and handling
#
      
mqueue  = Queue()
inqueue = Queue()
bpm = 0
running = True
samples = deque()
last_clock = None


#
# Events from Generic MIDI Handling
#

def MidinProcess(inqueue, portname):

    inqueue_get = inqueue.get
    bpm = 0
    samples = deque()
    last_clock = None

    while True:
        time.sleep(0.001)
        msg = inqueue_get()
        #print("")
        #print("Generic from", portname,"msg : ", msg)
        

        # NOTE ON message on all midi channels   
        if NOTE_ON -1 < msg[0] < 160 and msg[2] !=0 :

            MidiChannel = msg[0]-144
            MidiNote = msg[1]
            MidiVel = msg[2]
            print()
            print("NOTE ON :", MidiNote, 'velocity :', MidiVel, "Channel", MidiChannel)
            #print("Midi in process send /aurora/noteon "+str(msg[1])+" "+str(msg[2]))
            SendAU("/aurora/noteon",[MidiChannel, msg[1], msg[2]])

            '''
            # Sampler mode : note <63 launch snare.wav / note > 62 kick.wav 
            if MidiNote < 63 and MidiVel >0:
        
                if platform == 'darwin':
                    os.system("afplay snare.wav")
                else:
                    os.system("aplay snare.wav")
        
        
            if MidiNote > 62 and MidiVel >0:
              
                if platform == 'darwin':
                    os.system("afplay kick.wav")
                else:
                    os.system("aplay kick.wav")
            '''   
                
        # NOTE OFF or Note with 0 velocity on all midi channels
        if NOTE_OFF -1 < msg[0] < 145 or (NOTE_OFF -1 < msg[0] < 160 and msg[2] == 0):

            print("NOTE_off :",NOTE_OFF)
            if msg[0] > 143:
                MidiChannel = msg[0]-144
            else:
                MidiChannel = msg[0]-128
            #print("NOTE OFF :", MidiNote, "Channel", MidiChannel)
            #print("Midi in process send /aurora/noteoff "+str(msg[1]))
            SendAU("/aurora/noteoff",[MidiChannel, msg[1]])


        # # CC on all Midi Channels 
        if CONTROLLER_CHANGE -1 < msg[0] < 192:

            MidiChannel = msg[0]-175
            print()
            #print("channel", MidiChannel, "CC :", msg[1], msg[2])
            print("Midi in process send /aurora/rawcc "+str(msg[0]-175-1)+" "+str(msg[1])+" "+str(msg[2]))
            SendAU("/aurora/rawcc",[msg[0]-175-1, msg[1], msg[2]])
            
        '''
        # MMO-3 Midi CC message CHANNEL 1          
        if CONTROLLER_CHANGE -1 < msg[0] < 192:
            print("channel 1 (MMO-3) CC :", msg[1], msg[2])
            print("Midi in process send /mmo3/cc/"+str(msg[1])+" "+str(msg[2])+" to WS")
            WScom.send("/mmo3/cc/"+str(msg[1])+" "+str(msg[2]))


        # OCS-2 Midi CC message CHANNEL 2        
        if msg[0] == CONTROLLER_CHANGE+1:
            print("channel 2 (OCS-2) CC :", msg[1], msg[2])

            print("Midi in process send /ocs2/cc/"+str(msg[1])+" "+str(msg[2])+" to WS")
            WScom.send("/ocs2/cc/"+str(msg[1])+" "+str(msg[2]))
        '''

        if msg[0] == TIMING_CLOCK:
            now = time.time()

            if last_clock is not None:
                samples.append(now - last_clock)
            last_clock = now

            if len(samples) > 24:
                samples.popleft()

            if len(samples) >= 2:
                #bpm = 2.5 / (sum(samples) / len(samples))
                #print("%.2f bpm" % bpm)

                bpm = round(2.5 / (sum(samples) / len(samples)))        # Against BPM lot very tiny change :
                sync = True
                # print("MIDI BPM", bpm)
            
            #print("Midi clock : BPM", bpm)
            SendAU("/aurora/clock",[])
            # SendAU("/aurora/bpm",[bpm])


        if msg[0] in (SONG_CONTINUE, SONG_START):
            running = True
            #print("START/CONTINUE received.")
            #print("Midi in process send /aurora/start")
            SendAU("/aurora/start",[])


        if msg[0] == SONG_STOP:
            running = False
            #print("STOP received.")
            #print("Midi in process send /aurora/stop")
            SendAU("/aurora/stop",[])

        '''
        # other midi message  
        if msg[0] != NOTE_OFF and  msg[0] != NOTE_ON and msg[0] != CONTROLLER_CHANGE:
            pass
            
            print("from", portname,"other midi message")
            MidiMsg(msg[0],msg[1],msg[2],mididest)
        '''

#def NoteOn(note, color, mididest):
#https://pypi.org/project/python-rtmidi/0.3a/
# NOTE_ON=#90 et NOTE_OFF=#80 on ajoute le channel (0 le premier) pour envoyer effectivement sur le channel
def NoteOn(note, color, mididest, midichannel=0):
    global MidInsNumber

    if gstt.debug >0:
        print("Sending", note, color, "to", mididest, "on channel", midichannel)

    for port in range(MidInsNumber):

        # To mididest
        if midiname[port].find(mididest) == 0:
            midiport[port].send_message([NOTE_ON+midichannel, note, color])

        # To All 
        elif mididest == "all" and midiname[port].find(mididest) != 0:
            midiport[port].send_message([NOTE_ON+midichannel, note, color])




def NoteOff(note, mididest):
    global MidInsNumber


    for port in range(MidInsNumber):

        # To mididest
        if midiname[port].find(mididest) != -1:
            midiport[port].send_message([NOTE_OFF, note, 0])

        # To All 
        elif mididest == "all" and midiname[port].find(mididest) == -1:
                midiport[port].send_message([NOTE_OFF, note, 0])


       
# Generic call back : new msg forwarded to queue 
class AddQueue(object):
    def __init__(self, portname, port):
        self.portname = portname
        self.port = port
        #print "AddQueue", port)
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        #print "inqueue : [%s] @%0.6f %r" % ( self.portname, self._wallclock, message))
        message.append(deltatime)
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

        print("Adding OutDevice name", self.name, "kind", self.kind, "port", self.port)

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
        log.info("MIDIout...")
        print("List and attach to available devices on host with IN port :")
    
        # Display list of available midi IN devices on the host, create and start an OUT instance to talk to each of these Midi IN devices 
        midiout = rtmidi.MidiOut()
        available_ports = midiout.get_ports()
    
        for port, name in enumerate(available_ports):
    
            midiname[port]=name
            midiport[port].open_port(port)
            #print )
            #print "New OutDevice [%i] %s" % (port, name))

            OutDevice.append(OutObject(name, "generic", port))
    
        #print "")      
        print(len(OutDevice), "Out devices")
        #ListOutDevice()
        MidInsNumber = len(OutDevice)+1

def ListOutDevice():

    for item in OutObject.getinstances():

        print(item.name)

def FindOutDevice(name):

    port = -1
    for item in OutObject.getinstances():
        #print "searching", name, "in", item.name)
        if name == item.name:
            #print 'found port',item.port)
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

        print("Adding InDevice name", self.name, "kind", self.kind, "port", self.port)

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
    log.info("MIDIin...")
    
    # client mode
    if gstt.debug > 0:
        if gstt.clientmode == True:
            print("midi3 in client mode")
        else: 
            print("midi3 in server mode")

    print("List and attach to available devices on host with OUT port :")

    if platform == 'darwin':
        mido.set_backend('mido.backends.rtmidi/MACOSX_CORE')

    genericnumber = 0

    for port, name in enumerate(mido.get_input_names()):


        outport = FindOutDevice(name)
        midinputsname[port]=name
        
        #print "name",name, "Port",port, "Outport", outport)
        # print "midinames", midiname)
        
        #ListInDevice()

        try:
            #print name, name.find("RtMidi output"))
            if name.find("RtMidi output") > -1:
                print("No thread started for device", name)
            else:
                portin = object
                port_name = ""
                portin, port_name = open_midiinput(outport)

                if midisync == True:
                    portin.ignore_types(timing=False)

                #midinputs.append(portin)
                InDevice.append(InObject(name, "generic", outport, portin))
                
                thread = Thread(target=MidinProcess, args=(midinputsqueue[port],port_name))
                thread.setDaemon(True)
                thread.start() 

                #print "Thread launched for midi port", port, "portname", port_name, "Inname", midiname.index(port_name)
                #print "counter", InObject.counter
                #midinputs[port].set_callback(AddQueue(name),midinputsqueue[port])
                #midinputs[port].set_callback(AddQueue(name))
                #genericnumber += 1
                InDevice[InObject.counter-1].rtmidi.set_callback(AddQueue(name,port))

        except Exception:
            traceback.print_exc()
                    
    #print "")      
    print(InObject.counter, "In devices")
    #ListInDevice()


def ListInDevice():

    #print "known IN devices :"
    for item in InObject.getinstances():

        print(item.name)
    print("")

def FindInDevice(name):

    port = -1
    for item in InObject.getinstances():
        #print "searching", name, "in", item.name)
        if name in item.name:
            #print 'found port',item.port)
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

# mididest : all or specifiname, won't be sent to launchpad or Bhoreal.
def MidiMsg(midimsg, mididest):
    
   
    desterror = -1

    print("jamidi3 got midimsg", midimsg, "for", mididest)

    for port in range(len(OutDevice)):
        # To mididest
        if midiname[port].find(mididest) != -1:
            if gstt.debug>0:
                print("jamidi3 sending to name", midiname[port], "port", port, ":", midimsg)
            midiport[port].send_message(midimsg)
            desterror = 0

    if desterror == -1:
        print("mididest",mididest, ": ** This midi destination doesn't exists **")

    # send midi msg over ws.
    #if gstt.clientmode == True:
    #    ws.send("/ocs2/cc/1 2")


'''
def NoteOn(note, velocity, mididest):
    global MidInsNumber

    
    for port in range(MidInsNumber):

        # To mididest
        if midiname[port].find(mididest) == 0:
            midiport[port].send_message([NOTE_ON, note, velocity])
'''


def listdevice(number):
	
	return midiname[number]


	
def check():

    OutConfig()
    InConfig()
    

	
