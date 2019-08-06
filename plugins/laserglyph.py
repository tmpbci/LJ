#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-


'''

Laserglyph
v0.1.0

Anaglyphed rotating cube (for red and green glasses)

This client uses the drawing functions (polyline) provided by LJ in lj.py

LICENCE : CC

by Sam Neurohack


'''
import sys
import os
print()
ljpath = r'%s' % os.getcwd().replace('\\','/')

# import from shell

sys.path.append(ljpath +'/../libs/')

#import from LJ
sys.path.append(ljpath +'/libs/')
print (ljpath+'/../libs/')

import lj23 as lj

from OSC3 import OSCServer, OSCClient, OSCMessage
import redis
import math
import time
import argparse

'''
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
#from osc4py3 import oscmethod as osm
from osc4py3.oscmethod import * 
'''

OSCinPort = 8004
oscrun = True
# myIP = "127.0.0.1"
PL = 0

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Text Cycling for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-l","--laser",help="Laser number to be displayed (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)

args = argsparser.parse_args()


if args.client:
	ljclient = args.client
else:
	ljclient = 0

if args.laser:
	plnumber = args.laser
else:
	plnumber = 0

# Redis Computer IP
if args.redisIP  != None:
	redisIP  = args.redisIP
else:
	redisIP = '127.0.0.1'

print("redisIP",redisIP)

# myIP
if args.myIP  != None:
	myIP  = args.myIP
else:
	myIP = '127.0.0.1'

print("myIP",myIP)

if args.verbose:
	debug = args.verbose
else:
	debug = 0


lj.Config(redisIP,ljclient,"glyph")

white = lj.rgb2int(255,255,255)
red = lj.rgb2int(255,0,0)
blue = lj.rgb2int(0,0,255)
green = lj.rgb2int(0,255,0)

width = 800
height = 600
centerX = width / 2
centerY = height / 2

# 3D to 2D projection parameters
fov = 256
viewer_distance = 2.2


# Anaglyph computation parameters for right and left eyes.
eye_spacing = 100
nadir = 0.5
observer_altitude = 30000
#observer_altitude = 10000
# elevation = z coordinate
# 0.0, -2000 pop out
map_plane_altitude = 0.0

# Cube coordinates
# Define the vertices that compose each of the 6 faces.
vertices = [
	(- 1.0, 1.0,- 1.0),
	( 1.0, 1.0,- 1.0),
	( 1.0,- 1.0,- 1.0),
	(- 1.0,- 1.0,- 1.0),
	(- 1.0, 1.0, 1.0),
	( 1.0, 1.0, 1.0),
	( 1.0,- 1.0, 1.0),
	(- 1.0,- 1.0, 1.0)
	]
#faces = [(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,3,7,6),(6,5,4,7),(7,3,0,4)]
faces = [(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,3,7,6),(7,3,0,4),(7,3,0,4)]
#							name, intensity, active, xy, color, red, green, blue, PL , closed):
Leftcube = lj.FixedObject('Leftcube', True, 255, [], red, 255, 0, 0, PL , True)
Rightcube = lj.FixedObject('Rightcube', True, 255, [], green, 0, 255, 0, PL , True)

# 'Destination' for each PL 
#                  name, number, active, PL , scene, laser
# PL 0
Dest0 = lj.DestObject('0', 0, True, 0 , 0, 0)
Dest1 = lj.DestObject('1', 1, True, 0 , 1, 1)

'''
viewgen3Lasers = [True,False,False,False]
# Add here, one by one, as much destination as you want for each PL. 
# LJ and OSC can remotely add/delete destinations here.

lj.Dests = {
    "0":       {"PL": 0, "scene": 0, "laser": 0},
    "1":       {"PL": 0, "scene": 1, "laser": 1}
    }

'''

def LeftShift(elevation):

			diff = elevation - map_plane_altitude
			return nadir * eye_spacing *  diff / (observer_altitude - elevation)

def RightShift(elevation):

			diff = map_plane_altitude - elevation
			return (1 - nadir) * eye_spacing * diff / (observer_altitude - elevation)


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
import types
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# OSC callbacks

# /viewgen/ljclient
def OSCljclient(path, tags, args, source):

    print("Got /viewgen/ljclient with value", args[0])
    lj.WebStatus("viewgen to virtual "+ str(args[0]))
    ljclient = args[0]
    lj.LjClient(ljclient)


def Proj(x,y,z,angleX,angleY,angleZ):

		rad = angleX * math.pi / 180
		cosa = math.cos(rad)
		sina = math.sin(rad)
		y2 = y
		y = y2 * cosa - z * sina
		z = y2 * sina + z * cosa
		
		rad = angleY * math.pi / 180
		cosa = math.cos(rad)
		sina = math.sin(rad)
		z2 = z
		z = z2 * cosa - x * sina
		x = z2 * sina + x * cosa

		rad = angleZ * math.pi / 180
		cosa = math.cos(rad)
		sina = math.sin(rad)
		x2 = x
		x = x2 * cosa - y * sina
		y = x2 * sina + y * cosa


		""" Transforms this 3D point to 2D using a perspective projection. """
		factor = fov / (viewer_distance + z)
		x = x * factor + centerX
		y = - y * factor + centerY
		return (x,y)

def Run():


	Left = []
	Right = []
	counter =0
	lj.WebStatus("LaserGlyph")
	lj.SendLJ("/glyph/start 1")

	# OSC Server callbacks
	print("Starting OSC server at",myIP," port",OSCinPort,"...")
	'''
	osc_startup()
	osc_udp_server(myIP, OSCinPort, "InPort")
	osc_method("/ping", lj.OSCping)
	osc_method("/quit*", quit)
	osc_method("/glyph/ljclient", OSCljclient)
	'''
	oscserver.addMsgHandler( "/glyph/ljclient", OSCljclient )

	# Add OSC generic plugins commands : 'default", /ping, /quit, /pluginame/obj, /pluginame/var, /pluginame/adddest, /pluginame/deldest
	lj.addOSCdefaults(oscserver)

	try:

		while lj.oscrun:

			lj.OSCframe()
			Left = []
			Right = []
	
			x = vertices[0][0]
			y = vertices[0][1]
			z = vertices[0][2]
	
			# The cube start always with vertice 0
			# LJ tracers will "move" the laser to this first point in black, then move to the next with second point color.
			# For more accuracy in dac emulator, repeat this first point.
	
			# Cube Y axis rotation of 'counter' angle and 3d-2d Proj function. 
			#Left.append( Proj(x+LeftShift(z*5),y,z,0,counter,0))
			#Right.append(Proj(x+RightShift(z*5),y,z,0,counter,0))	
	
	
			# Add all the cube points face by face.
			for fa in faces:
				for point in fa:
					x = vertices[point][0]
					y = vertices[point][1]
					z = vertices[point][2]
	
					Left.append(Proj(x+LeftShift(z*25),y,z,0,counter,0))
					Right.append(Proj(x+RightShift(z*25),y,z,0,counter,0))	
	
	
			# Drawing step, 2 possibilities 
	
			# Red and Green drawn by laser 0
			#lj.PolyLineOneColor(Left,  c = red,    PL = PL, closed = True)
			#lj.PolyLineOneColor(Right, c = green,   PL = PL, closed = True)

			lj.PolyLineOneColor(Left, c = Leftcube.color , PL = Leftcube.PL, closed = Leftcube.closed)
			lj.PolyLineOneColor(Right, c = Rightcube.color , PL = Rightcube.PL, closed = Rightcube.closed)
			#print(len(Left))

			#lj.DrawPL(PL)
			#print(Dest0.name, Dest1.name)
			lj.DrawDests()
	
			'''
			# Red on laser 1 and green on laser 2
			lj.PolyLineOneColor(Left,  c = red,    PL = 1, closed = True)
			lj.PolyLineOneColor(Right, c = green,   PL = 2, closed = True)
			lj.DrawPL(1)
			lj.DrawPL(2)		
	
			'''
			
			time.sleep(0.1)
	
			counter += 1
			if counter > 360:
				counter = 0

	except KeyboardInterrupt:
		pass

	# Gently stop on CTRL C

	finally:

		lj.ClosePlugin()


Run()
