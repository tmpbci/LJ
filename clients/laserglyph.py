# coding=UTF-8

'''
Anaglyphed rotating cube (for red and green glasses)

This client uses the drawing functions (polyline) provided by LJ in lj.py
You must check in lj.py if the redis server IP is correct.

LICENCE : CC
'''

import redis
import lj
import math
import time
import argparse

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Text Cycling for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-l","--laser",help="Laser number to be displayed (0 by default)",type=int)

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

lj.Config(redisIP,ljclient)


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
faces = [(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,3,7,6),(6,5,4,7),(7,3,0,4)]



def LeftShift(elevation):

			diff = elevation - map_plane_altitude
			return nadir * eye_spacing *  diff / (observer_altitude - elevation)

def RightShift(elevation):

			diff = map_plane_altitude - elevation
			return (1 - nadir) * eye_spacing * diff / (observer_altitude - elevation)

# If you want to use rgb for color :
def rgb2int(r,g,b):
	return int('0x%02x%02x%02x' % (r,g,b),0)
	

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

	while 1:

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

				Left.append( Proj(x+LeftShift(z*25),y,z,0,counter,0))
				Right.append(Proj(x+RightShift(z*25),y,z,0,counter,0))	


		# Drawing step, 2 possibilities 

		# Red and Green drawn by laser 0
		lj.PolyLineOneColor(Left,  c = red,    PL = 0, closed = True)
		lj.PolyLineOneColor(Right, c = green,   PL = 0, closed = True)
		lj.DrawPL(0)

		'''
		# Red on laser 1 and green on laser 2
		lj.PolyLineOneColor(Left,  c = red,    PL = 1, closed = True)
		lj.PolyLineOneColor(Right, c = green,   PL = 2, closed = True)
		lj.DrawPL(1)
		lj.DrawPL(2)		

		'''
		
		time.sleep(0.1)

		counter += 1
		if counter >360:
			counter =0

white = rgb2int(255,255,255)
red = rgb2int(255,0,0)
blue = rgb2int(0,0,255)
green = rgb2int(0,255,0)


Run()
