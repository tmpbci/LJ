#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""

ArtNet/DMX Handler : 
v0.7.0


by Sam Neurohack 
from /team/laser

Artnet receving code from https://github.com/kongr45gpen/simply-artnet
Laser selection 
one universe / laser

Plugin selection 
banck change/scene/

"""


import random
import pysimpledmx
from serial.tools import list_ports
import serial,time
from threading import Thread
import socket
import struct
import types
from sys import platform, version
import sys
import argparse, traceback
import os
import log

is_py2 = version[0] == '2'

if is_py2:
    from OSC import OSCServer, OSCClient, OSCMessage
else:
    from OSC3 import OSCServer, OSCClient, OSCMessage

ljpath = r'%s' % os.getcwd().replace('\\','/')

# import from shell

#sys.path.append('../../libs')

#import from LJ
sys.path.append(ljpath +'/libs/')

import lj23layers as lj

#
# Init
#

OSCinPort = 8032


sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('',6454))

dmxeq = {}
dmxstates = []
dmxinit = False
universe = []


for i in range(1,514):
    dmxstates.append(-1)


print ("")
log.infog("Artnet v0.1")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Artnet & DMX for LJ")
argsparser.add_argument("-u","--universe",help="Universe, not implemented (0 by default)",type=int)
argsparser.add_argument("-s","--subuniverse",help="Subniverse, not implemented (0 by default)",type=int)
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)

args = argsparser.parse_args()


# Universe
if args.universe:
    universenb = args.universe
else:
    universenb = 0

# Universe
if args.subuniverse:
    subuniversenb = args.subuniverse
else:
    subuniversenb = 0

# Debug level
if args.verbose:
    debug = args.verbose
else:
    debug = 0

# Redis Computer IP
if args.redisIP  != None:
    redisIP  = args.redisIP
else:
    redisIP = '127.0.0.1'

# myIP
if args.myIP  != None:
    myIP  = args.myIP
else:
    myIP = '127.0.0.1'

r = lj.Config(redisIP, 255, "artnet")

lj.WebStatus("Artnet init...")

def lhex(h):
    return ':'.join(x.encode('hex') for x in h)


def senddmx0():
    for channel in range (1,512):
        senddmx(channel,0)

def senddmx(channel, value):

    print("Setting channel %d to %d" % (i,value))
    #mydmx.setChannel((channel + 1 ), value, autorender=True)
    # calling render() is better more reliable to actually sending data
    # Some strange bug. Need to add one to required dmx channel is done automatically
    mydmx.setChannel((channel ), value)
    mydmx.render()
    print("Sending DMX Channel : ", str(channel), " value : ", str(value))

def updateDmxValue(channel, val):

    #
    if dmxstates[channel] == -1:
        dmxstates[channel] = val

    # DMX UPDATE!!! WOW!!!
    if dmxstates[channel] != val:
        dmxstates[channel] = val
        print("updating channel", channel, "with ", val)
        if mydmx != False:
            senddmx(channel, ord(val))

        
# Search for DMX devices

#ljnozoids.WebStatus("Available serial devices")


print("Available serial devices...")
ports = list(list_ports.comports())

portnumber = 0

# Get all serial ports names
for i, p in enumerate(ports):

    print(i, ":", p)

    if p[0]== "/dev/ttyUSB0":
      portname[portnumber] = p[0]
      portnumber += 1


    if platform == 'darwin' and p[1].find("DMX USB PRO") != -1:
      portname[portnumber] = p[0]
      portnumber += 1


# ljnozoids.WebStatus("Found " + str(portnumber) +" Nozoids.")

print("Found", portnumber, "DMX devices")


if portnumber > 0:

    print("with serial names", portname)
    mydmx = pysimpledmx.DMXConnection(gstt.serdmx[0])
    senddmx0()
    time.sleep(1)

    # Send a random value to channel 1
    vrand=random.randint(0,255)
    senddmx(1,vrand)

else:
    mydmx = False
    print("No DMX found, Art-Net receiver only.")


#
# OSC
#

oscserver = OSCServer( (myIP, OSCinPort) )
oscserver.timeout = 0
#oscrun = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# default handler
def OSChandler(path, tags, args, source):

    oscaddress = ''.join(path.split("/"))
    print(("Default OSC Handler : msg from Client : " + str(source[0]),))
    print(("OSC address", path, "with",))
    if len(args) > 0:
        print(("args", args))
    else:
        print("noargs")
    #oscIPout = str(source[0])
    #osclient.connect((oscIPout, oscPORTout))


# RAW OSC Frame available ? 
def OSCframe():

    # clear timed_out flag
    print ("oscframe")
    oscserver.timed_out = False
    # handle all pending requests then return
    while not oscserver.timed_out:
        oscserver.handle_request()


# Stop osc server
def OSCstop():

    oscrun = False
    oscserver.close()


# /sendmx channel value
def OSCsendmx(path, tags, args, source):

    channel = args[0]
    val = args[1]
    updateDmxValue(channel, val)


lj.addOSCdefaults(oscserver)
lj.SendLJ("/pong", "artnet")
lj.WebStatus("Artnet Running...")

log.infog("Artnet running...")
print()

oscserver.addMsgHandler( "/sendmx", OSCsendmx )

#
# Running...
#

'''
print ("Starting, use Ctrl+C to stop")
print (lj.oscrun)
'''

try:

    while lj.oscrun:

        data = sock.recv(10240)
        if len(data) < 20:
            continue
        
        if data[0:7] != "Art-Net" or data[7] != "\0":
            print("artnet package")
            #lj.WebStatus("Artnet package")
            continue
        OSCframe() 

        if ord(data[8]) != 0x00 or ord(data[9]) != 0x50:
            print("OpDmx")
            continue

        print(("oscrun", lj.oscrun))
        protverhi = ord(data[10])
        protverlo = ord(data[11])
        sequence  = ord(data[12])
        physical  = ord(data[13])
        subuni    = ord(data[14])
        net       = ord(data[15])
        lengthhi  = ord(data[16])
        length    = ord(data[17])
        dmx       = data[18:]
    
        print((data[0:7], "version :",lhex(data[10])+lhex(data[11]), "sequence :", sequence, "physical", physical, "subuni",subuni,"net", net))
    
        for i in range(0,510):
            updateDmxValue(i+1,dmx[i])
 
       
except Exception:
  traceback.print_exc()

finally:

    lj.ClosePlugin()
    sock.close()
    OSCstop()
'''
import sys, socket, math, time
from ctypes import *

class Artnet:
    class ArtNetDMXOut(LittleEndianStructure):
        PORT = 0x1936
        _fields_ = [("id", c_char * 8),
                    ("opcode", c_ushort),
                    ("protverh", c_ubyte),
                    ("protver", c_ubyte),
                    ("sequence", c_ubyte),
                    ("physical", c_ubyte),         
                    ("universe", c_ushort),
                    ("lengthhi", c_ubyte),
                    ("length", c_ubyte),
                    ("payload", c_ubyte * 512)]
        
        def __init__(self):
            self.id = b"Art-Net"
            self.opcode = 0x5000
            self.protver = 14
            self.universe = 0
            self.lengthhi = 2

    def __init__(self):
        self.artnet = Artnet.ArtNetDMXOut()
        self.S = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)    
        for i in range(512):
            self.artnet.payload[i] = 0

    def send(self,data,IP,port):
        # send(送るデータ,IPアドレス,ポート番号)
        self.artnet.universe = port
        for i in range(512):
            if(i < len(data)):
                self.artnet.payload[i] = data[i]
            else:
                break
        self.S.sendto(self.artnet,(IP,Artnet.ArtNetDMXOut.PORT))

if __name__ == '__main__':
    artnet = Artnet()
    data = [0] * 512
    for i in range(150):
        data[i*3+0] = 0
        data[i*3+1] = 0
        data[i*3+2] = 0
artnet.send(data,"133.15.42.111",5)
'''
