#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
LJ v0.8.0

Pygame Simulator plugin for LJ

LICENCE : CC
Sam Neurohack, loloster, 

OSC server with :

/simu/quit
/simu/newpl      new pl number to draw
/simu/newclient  new client number to draw
/ping

'''

#from __future__ import print_function 
import time 
import math
import random
import itertools
import traceback
import sys
import os
#import thread
import redis

import pdb
import types, ast, argparse, struct
import numpy as np

sys.path.append('../libs')

# import from LJ
ljpath = r'%s' % os.getcwd().replace('\\','/')
sys.path.append(ljpath +'/libs/')
#print ljpath+'/libs/'

import lj23 as lj

is_py2 = sys.version[0] == '2'
if is_py2:
    from OSC import OSCServer, OSCClient, OSCMessage
    #print ("Importing lj23 and OSC from libs...")
else:
    from OSC3 import OSCServer, OSCClient, OSCMessage



screen_size = [750,750]
pl = [[],[],[],[]]


print ("")
print ("LJ v0.8.0 : Pygame simulator")
print ("")
import pygame
print ("Arguments parsing if needed...")



#
# Arguments parsing
#

argsparser = argparse.ArgumentParser(description="One laser Simulator for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-l","--laser",help="Laser number to be displayed (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)

args = argsparser.parse_args()

if args.client:
    ljclient = args.client
else:
    ljclient = 0

# Laser choice
if args.laser:
    simuPL = args.laser
else:
    simuPL = 0

# Debug ?
if args.verbose:
    debug = args.verbose
else:
    debug = 0

# Redis Computer IP
if args.redisIP  != None:
    redisIP  = args.redisIP
else:
    redisIP = '127.0.0.1'

r = redis.StrictRedis(host=redisIP, port=6379, db=0)
lj.Config(redisIP,0,"simu")

# myIP
if args.myIP  != None:
    myIP  = args.myIP
else:
    myIP = '127.0.0.1'



#
# OSC 
#

oscIPin = myIP
oscPORTin = 8008

ljIP = redisIP
ljPort = 8002

print ("")
print ("Receiving on ", oscIPin, ":",str(oscPORTin))
oscserver = OSCServer( (oscIPin, oscPORTin) )
oscserver.timeout = 0
oscrun = True

def handle_timeout(self):
    self.timed_out = True

oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


def SendLJ(address, args):
    
    if debug >0:
            print("Sending to LJ...", address, args)
    
    osclientlj = OSCClient()
    osclientlj.connect((ljIP, ljPort)) 

    oscmsg = OSCMessage()
    oscmsg.setAddress(address)
    oscmsg.append(args)

    try:
        osclientlj.sendto(oscmsg, (ljIP, ljPort))
        oscmsg.clearData()
        return True

    except:
        print('Connection to LJ IP', ljIP,'port', ljPort, 'refused : died ?')
        return False

def WebStatus(message):

    SendLJ("/status",message)


# RAW OSC Frame available ? 
def osc_frame():

    # clear timed_out flag
    oscserver.timed_out = False
    # handle all pending requests then return
    while not oscserver.timed_out:
        oscserver.handle_request()

# /quit
def quit(path, tags, args, source):
    global oscrun

    oscrun = False
    pygame.quit()
    lj.ClosePlugin()
    

# /newPL pointlistnumber
def newPL(path, tags, args, source):

    user = ''.join(path.split("/"))
    print ("")
    print (user,path,args)
    print ("Simulator got a new point list number :", args[0])
    simuPL = args[0]

# /newClient clientnumber
def newClient(path, tags, args, source):

    user = ''.join(path.split("/"))
    print ("")
    print (user,path,args)
    print ("Simulator got a new client number : ", args[0])
    ljclient = args[0]


# Redis key 'n' -> numpy array a
# array 2 dimensions is also store in redis key : h time w values
def fromRedis(n):

   print ("get key", n)
   encoded = r.get(n)
   h, w = struct.unpack('>II',encoded[:8])
   print(h,w)
   a = np.frombuffer(encoded, dtype=np.int16, offset=8).reshape(h,w)
   return a


#
# Pygame screen
#

def RenderScreen(surface):

    if len(pl[simuPL]):
        
        xyc_prev = pl[simuPL][0]
        #pygame.draw.line(surface,self.black_hole_color,(x_bh_cur, y_bh_cur), (x_bh_next, y_bh_next))
        #pygame.draw.line(surface,self.spoke_color,(x_bh_cur, y_bh_cur), (x_area_cur, y_area_cur))
        for xyc in pl[simuPL]:
            c = int(xyc[2])
            if c: pygame.draw.line(surface,c,xyc_prev[:2],xyc[:2],3)
            xyc_prev = xyc
#
# Startup
#

SendLJ("/simu/start",1)
WebStatus("pysimu startup...")
pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("LJ Simulator")
clock = pygame.time.Clock()
update_screen = False

oscserver.addMsgHandler( "/quit", lj.OSCquit )
oscserver.addMsgHandler( "/ping", lj.OSCping )
#oscserver.addMsgHandler( "/simu/start", start )
oscserver.addMsgHandler( "/simu/newpl", newPL )
oscserver.addMsgHandler( "/simu/newclient", newClient )

print ("Simulator displays client", ljclient, "point list", str(simuPL))
WebStatus("pySimu "+ str(ljclient) + " " + str(simuPL))

#
# Main
#

try:

    while lj.oscrun:
    
        # pending osc message ?
        osc_frame()
    
        # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
    
        screen.fill(0)
        #print("/pl/"+ str(ljclient) + "/" + str(simuPL))
        #print r.get("/pl/"+ str(ljclient) + "/" + str(simuPL))
        if is_py2:
            pl[simuPL] = ast.literal_eval(r.get("/pl/"+ str(ljclient) + "/" + str(simuPL)))
        else:
            pl[simuPL] = eval(r.get("/pl/"+ str(ljclient) + "/" + str(simuPL)))

        #pl[simuPL] = fromRedis("/pl/"+ str(ljclient) + "/" + str(simuPL))

        if update_screen:
        	update_screen = False
        	RenderScreen(screen)
        	pygame.display.flip()
        else:
        	update_screen = True
    
        clock.tick(30)
        time.sleep(0.001)

except KeyboardInterrupt:
    pass

except Exception:
    traceback.print_exc()


finally:
    pygame.quit()
    lj.ClosePlugin()





