#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-


'''

Square
v0.1.0

Anaglyphed rotating square (for red and green glasses)

This scene uses the drawing functions (polyline) provided by LJ in lj23.py

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

import lj23layers as lj

sys.path.append('../libs')
from OSC3 import OSCServer, OSCClient, OSCMessage
import redis
import math
import time
import argparse

OSCinPort = 8013

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Square example for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-s","--scene",help="LJ scene number (0 by default)",type=int)
#argsparser.add_argument("-l","--laser",help="Laser number to be displayed (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)

args = argsparser.parse_args()

if args.scene:
	ljscene = args.scene
else:
	ljscene = 0
'''
if args.laser:
	plnumber = args.laser
else:
	plnumber = 0
'''

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

# Useful variables init.
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
# algorythm come from anaglyph geo maps 
eye_spacing = 100
nadir = 0.5
observer_altitude = 30000
map_layerane_altitude = 0.0

# square coordinates : vertices that compose each of the square.
vertices = [
	(- 1.0, 1.0,- 1.0),
	( 1.0, 1.0,- 1.0),
	( 1.0,- 1.0,- 1.0),
	(- 1.0,- 1.0,- 1.0)
	]

face = [0,1,2,3]

#
# LJ inits
# 

layer = 0

# Setup LJ library mandatory properties for this layerugin
lj.Config(redisIP, ljscene, "square")

# Define properties for each drawn "element" : name, intensity, active, xy, color, red, green, blue, layer , closed
Leftsquare = lj.FixedObject('Leftsquare', True, 255, [], red, 255, 0, 0, layer , True)
Rightsquare = lj.FixedObject('Rightsquare', True, 255, [], green, 0, 255, 0, layer , True)

# 'Destination' for given layer : name, number, active, layer , scene, laser
Dest0 = lj.DestObject('0', 0, True, 0 , 0, 0) 	# Dest0 will send layer 0 points to scene 0, laser 0 

'''
TRICKS:

1/ How to have another laser drawing the same thing ?

That's a destination problem : just add another destination !

Dest1 = lj.DestObject('1', 1, True, 0 , 1, 1)	# Dest1 will also send layer 0 points to scene 1, laser 1 


2/ Different layers to different lasers ?

Say because of too much points you want Left element drawn by scene 0, laser 0 and right element by scene 0, laser 1

First define a different object/layer for each drawn element :

Leftsquare = lj.FixedObject('Leftsquare', True, 255, [], red, 255, 0, 0, 0 , True)		 # Left goes to layer 0
Rightsquare = lj.FixedObject('Rightsquare', True, 255, [], green, 0, 255, 0, 1 , True)	 # Right goes to layer 1

Define 2 destinations :

Dest0 = lj.DestObject('0', 0, True, 0 , 0, 0) 	# Dest0 will send layer 0 points to scene 0, laser 0 
Dest1 = lj.DestObject('1', 1, True, 1 , 0, 1)	# Dest1 will send layer 1 points to scene 0, laser 1 



3/ Different layers to one laser ?

You should consider adding all your points to one layer, but same as 1/ it's a destination problem, 
just add another destination with the same scene/laser for each layer

Dest1 = lj.DestObject('1', 1, True, 1 , 0, 0)	# Dest1 will also send layer 1 points to scene 0, laser 0 


4/ I want to animate/modify anything on the fly : I'm doing a game and suddenly my hero change color.

It's a declared object problem : say Hero is a Fixed Object, you can directly change value of 

Hero.name, Hero.active, Hero.intensity, Hero.xy, Hero.color, Hero.red, Hero.green, Hero.blue, Hero.layer, Hero.closed

For a character vanishing in one point you can decrease it's size : RelativeObjects has graphics computation. 
PNC.name, PNC.active, PNC.intensity, PNC.xy, PNC.color, PNC.red, PNC.green, PNC.blue, PNC.layer, PNC.closed, PNC.xpos, PNC.ypos, PNC.resize, PNC.rotx, PNC.roty, PNC.rotz


Same for Dest0 if it's a destObject : 
Dest0.name, Dest0.number, Dest0.active, Dest0.layer, Dest0.scene, Dest0.laser


DrawDests() will take care of all your declared drawn elements and Destinations.

'''


#
# Anaglyph computation : different X coordinate for each eye
#

def LeftShift(elevation):

			diff = elevation - map_layerane_altitude
			return nadir * eye_spacing *  diff / (observer_altitude - elevation)

def RightShift(elevation):

			diff = map_layerane_altitude - elevation
			return (1 - nadir) * eye_spacing * diff / (observer_altitude - elevation)

#
# OSC
#

oscserver = OSCServer( (myIP, OSCinPort) )
oscserver.timeout = 0


# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# OSC callbacks

# /square/ljscene
def OSCljscene(path, tags, args, source):

    print("Got /square/ljscene with value", args[0])
    lj.WebStatus("square to virtual "+ str(args[0]))
    ljscene = args[0]
    lj.Ljscene(ljscene)


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


#
# Main 
#

def Run():


	Left = []
	Right = []
	counter =0
	lj.WebStatus("Square")
	lj.SendLJ("/square/start 1")

	# OSC Server callbacks
	print("Starting OSC server at",myIP," port",OSCinPort,"...")
	oscserver.addMsgHandler( "/square/ljscene", OSCljscene )

	# Add OSC generic layerugins commands : 'default", /ping, /quit, /pluginame/obj, /pluginame/var, /pluginame/adddest, /pluginame/deldest
	lj.addOSCdefaults(oscserver)

	try:

		while lj.oscrun:

			lj.OSCframe()
			Left = []
			Right = []
	
			x = vertices[0][0]
			y = vertices[0][1]
			z = vertices[0][2]
	
			# LJ tracers will "move" the laser to this first point in black, then move to the next with second point color.
			# For more accuracy in dac emulator, repeat this first point.

			# Generate all points in square.
			for point in face:
				x = vertices[point][0]
				y = vertices[point][1]
				z = vertices[point][2]

				Left.append(Proj(x+LeftShift(z*25),y,z,0,counter,0))
				Right.append(Proj(x+RightShift(z*25),y,z,0,counter,0))	
	

			lj.PolyLineOneColor(Left, c = Leftsquare.color , layer = Leftsquare.layer, closed = Leftsquare.closed)
			lj.PolyLineOneColor(Right, c = Rightsquare.color , layer = Rightsquare.layer, closed = Rightsquare.closed)

			lj.DrawDests()
	
			
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
