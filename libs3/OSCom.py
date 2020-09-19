#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
OSCcom for jamidi v0.1b

OSCom.Start(serverIP, OSCPORT) 
default handler : handler(path, tags, args, source)
register particular OSC command in Start(): i.e oscserver.addMsgHandler( "/n", Note)

Launch

print("Launching OSC Server", serverIP,':', OSCPORT)
OSCom.Start(serverIP, OSCPORT) 

'''

from . import midi3

#import socket
import types, json
from .OSC3 import OSCServer, OSCClient, OSCMessage
import _thread, time
from . import gstt
import WScom, UDPcom
from . import midi3

#base36 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]


def GetTime():
  return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True


def Start(serverIP, OSCPORT):
    global oscserver

    #print(GetTime(),gstt.oscname, gstt.Confs[gstt.oscname][0]["midichan"])
    #print(gstt.Confs)
    #print(gstt.Confs[gstt.oscname])
    for i in range(len(gstt.Confs[gstt.oscname])):
      print((GetTime(),gstt.oscname, gstt.Confs[gstt.oscname][i]["midichan"]))

    oscserver = OSCServer( (serverIP, OSCPORT) )
    oscserver.timeout = 0
    # funny python's way to add a method to an instance of a class
    import types
    oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)
    
    oscserver.addMsgHandler( "default", handler )
    oscserver.addMsgHandler( "/n", Note)
    oscserver.addMsgHandler( "/c", CC)
    oscserver.addMsgHandler( "/p", PB)
    _thread.start_new_thread(osc_thread, ())


# RAW OSC Frame available ? 
def OSCframe():
    # clear timed_out flag
    oscserver.timed_out = False
    # handle all pending requests then return
    while not oscserver.timed_out:
        oscserver.handle_request()




# OSC server Thread : handler, dacs reports and simulator points sender to UI.
def osc_thread():


    #print("osc Thread launched")
    try:
        while True:

            time.sleep(0.005)
            OSCframe()

    except Exception as e:
        import sys, traceback
        print('\n---------------------')
        print(('Exception: %s' % e))
        print('- - - - - - - - - - -')
        traceback.print_tb(sys.exc_info()[2])
        print("\n")




# Properly close the system. Todo
def Stop():
    oscserver.close()


# default handler
def handler(path, tags, args, source):

    oscaddress = ''.join(path.split("/"))
    print()
    print(("Jamidi Default OSC Handler got from " + str(source[0]),"OSC msg", path, "args", args))
    #print("OSC address", path)
    #print("find.. /bhoreal ?", path.find('/bhoreal'))
    if len(args) > 0:
        #print("with args", args)
        pass

    '''
    # for example
    if path == '/truc':
        arg1 =  args[0]
        arg2 = args[1])
    '''

'''
MIDI NOTES
=n in ORCA
/n in OSC
        ORCA    OSC
        =nmonv /n m o n v
        m : midi channel (0-15 / ORCA 0-F)
        o : octave       (0-8 / ORCA 0-7)   
        n : Note         A to G 
        v : velocity     0-Z will output (v/36)*127

'''
def Note(path, tags, args, source):

    #print('Note from ORCA received',args)

    midichannel = int(args[0],36)
    octave = int(args[1],36)
    note = args[2]
    velocity = int((int(args[3],36)/36)*127)

    if note.istitle() == True:
        notename = str(note)+ str(octave)
    else:
        notename = str(note)+ "#"+ str(octave)

    if gstt.debug > 0:
        print(("incoming note", note, octave, notename, midi3.note2midi(notename) ))

    for mididevice in midi3.findJamDevices(gstt.oscname):
        midi3.NoteOn(midi3.note2midi(notename), velocity, mididevice)
        #midi3.NoteOn(int(wspath[1]), int(wspath[2]), gstt.Confs[wscommand[1]][0]["mididevice"])


'''
CC
=c in ORCA
/c in OSC
    
        ORCA  OSC
        =cmcd /c m n d
        m : midi channel 
        n : number   (0-35 / ORCA 0-Z)
        d : data      0-Z will output (d/36)*127
'''
def CC(path, tags, args, source):

    midichannel = int(args[0],36)
    ccvr = int(args[1],36)
    ccvl = int((int(args[2],36)/36)*127)

    if  gstt.debug > 0:
        print(("ccvr=%d/ccvl=%d"%(ccvr,ccvl)))
    if gstt.oscname == "ocs2":
        gstt.crtvalueOCS2[ccvr]=ccvl
    else:
        gstt.crtvalueMMO3[ccvr]=ccvl

    for mididevice in midi3.findJamDevices(gstt.oscname):
        midi3.cc(gstt.Confs[gstt.oscname][0]["midichan"], ccvr, ccvl, mididevice)



def PB(path, tags, args, source):

    #print("Pitch number",ccnumber, value)
    midichannel = int(args[0])
    ccnumber = int(args[1])
    ccdata = int(args[3])

'''
# If needed to send some OSC 
def SendOSC(ip,port,oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclient = OSCClient()
    osclient.connect((ip, port)) 

    if gstt.debug == True :
        print("sending OSC message : ", oscmsg, "to", ip, ":", port)

    try:
        osclient.sendto(oscmsg, (ip, port))
        oscmsg.clearData()
        return True
    except:
        print ('Connection to', ip, 'refused : died ?')
        return False
'''
