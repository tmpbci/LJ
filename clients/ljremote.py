#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''

LJ Remote control via OSC in python 

This is different than sending pointlist to draw. See pyclient or laserglyph for that.
Say your client want to display some information on the weUI status field or remote control any other LJ functions.

See commands.py for LJ functions list.
See Doctodo for all webUI elements.

LJ OSC server is listening on port 8002, talk to it.

'''
from OSC import OSCServer, OSCClient, OSCMessage

LJIP = "127.0.0.1"

osclientlj = OSCClient()
oscmsg = OSCMessage()
osclientlj.connect((LJIP, 8002)) 

def sendlj(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    #print ("sending to bhorosc : ",oscmsg)
    try:
        osclientlj.sendto(oscmsg, (LJIP, 8002))
        oscmsg.clearData()
    except:
        print ('Connection to LJ refused : died ?')
        pass
    #time.sleep(0.001)

# display pouet in status display
sendlj("/status","pouet")

# switch laser 0 ack led to green
sendlj("/lack/0", 1)