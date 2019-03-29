#!/usr/bin/python2.7
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

'''
#from __future__ import print_function 
import time 
import math
import random
import itertools
import sys
import os
#import thread
import redis
import pygame
import pdb
import types, ast, argparse
from OSC import OSCServer, OSCClient, OSCMessage

screen_size = [750,750]
pl = [[],[],[],[]]


print ("")
print ("LJ v0.8.0 : Pygame simulator")
print ("")
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
OSCRunning = True

def handle_timeout(self):
    self.timed_out = True

oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


def sendLJ(address, args):
    
    if debug >0:
            print "Sending to LJ...", address, args
    
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
        print 'Connection to LJ IP', ljIP,'port', ljPort, 'refused : died ?'
        return False


# RAW OSC Frame available ? 
def osc_frame():

    # clear timed_out flag
    oscserver.timed_out = False
    # handle all pending requests then return
    while not oscserver.timed_out:
        oscserver.handle_request()

# /quit
def quit(path, tags, args, source):

    pygame.quit()
    print "pySimu Stopped by /quit."
    sys.exit()

# /start : 0 exit
def start(path, tags, args, source):

    print args, type(args)
    if args[0] == 0:
        pygame.quit()
        print "pySimu stopped by /start 0"
        sys.exit()

# Answer to LJ pings
def ping(path, tags, args, source):
    # Will receive message address, and message data flattened in s, x, y
    print "Simu got /ping with value", args[0]
    print "Simu replied with /pong simu"
    sendLJ("/pong","simu")



# /newPL pointlistnumber
def newPL(path, tags, args, source):

    user = ''.join(path.split("/"))
    print ""
    print user,path,args
    print "Simulator got a new point list number :", args[0]
    simuPL = args[0]

# /newClient clientnumber
def newClient(path, tags, args, source):

    user = ''.join(path.split("/"))
    print ""
    print user,path,args
    print "Simulator got a new client number : ", args[0]
    ljclient = args[0]

oscserver.addMsgHandler( "/quit", quit )
oscserver.addMsgHandler( "/ping", ping )
oscserver.addMsgHandler( "/pysimu/start", start )
oscserver.addMsgHandler( "/pysimu/newpl", newPL )
oscserver.addMsgHandler( "/pysimu/newclient", newClient )


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


pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("LJ Simulator")
clock = pygame.time.Clock()
update_screen = False

print ("Simulator displays client", ljclient, "point list", str(simuPL))

#
# Main
#

try:

    while True:
    
        # pending osc message ?
        osc_frame()
    
        # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
    
        screen.fill(0)
        pl[simuPL] = ast.literal_eval(r.get("/pl/"+ str(ljclient) + "/" + str(simuPL)))
    
        if update_screen:
        	update_screen = False
        	RenderScreen(screen)
        	pygame.display.flip()
        else:
        	update_screen = True
    
        clock.tick(30)
        # time.sleep(0.001)

except KeyboardInterrupt:
    pass

finally:
    pygame.quit()
    print "pySimu Stopped."




