# coding=UTF-8

'''
Anaglyphed cube

LICENCE : CC
'''

import redis
import framy
import math
import time
import numpy as np

# IP defined in /etd/redis/redis.conf
redisIP = '127.0.0.1'
r = redis.StrictRedis(host=redisIP, port=6379, db=0)


width = 800
height = 600
centerX = width / 2
centerY = height / 2

fov = 256
viewer_distance = 2.2

eye_spacing = 100
nadir = 0.5
observer_altitude = 30000
# elevation = z coordinate
 
# 0.0  or -2000 pop out)
map_plane_altitude = 0.0 

samparray = [0] * 100
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

# Define the vertices that compose each of the 6 faces. These numbers are
# indices to the vertices list defined above.
#faces = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)]
faces = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)]

def LeftShift(elevation):

			diff = elevation - map_plane_altitude
			return nadir * eye_spacing *  diff / (observer_altitude - elevation)

def RightShift(elevation):

			diff = map_plane_altitude - elevation
			return (1 - nadir) * eye_spacing * diff / (observer_altitude - elevation)

# If you want to use rgb for color :
def rgb2int(r,g,b):
	return int('0x%02x%02x%02x' % (r,g,b),0)


def ssawtooth(samples,freq,phase):

	t = np.linspace(0+phase, 1+phase, samples)
	for ww in range(samples):
		samparray[ww] = signal.sawtooth(2 * np.pi * freq * t[ww])
	return samparray

def ssquare(samples,freq,phase):

	t = np.linspace(0+phase, 1+phase, samples)
	for ww in range(samples):
		samparray[ww] = signal.square(2 * np.pi * freq * t[ww])
	return samparray

def ssine(samples,freq,phase):

	t = np.linspace(0+phase, 1+phase, samples)
	for ww in range(samples):
		samparray[ww] = np.sin(2 * np.pi * freq  * t[ww])
	return samparray


	
def shader2scrX(s):
    a1, a2 = -1,1  
    b1, b2 = -width/2, width/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))
	
def shader2scrY(s):
    a1, a2 = -1,1  
    b1, b2 = -heigth/2, heigth/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))
	

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



def Draw2PL():

	Shape = []
	Left = []
	Right = []
	counter =0

	while 1:
		Shape = []
		Left = []
		Right = []
		for fa in faces:
			#print ""
			#print "face",fa

			for point in fa:
				#print ""
				#print "point ", point 
				x = vertices[point][0]
				y = vertices[point][1]
				z = vertices[point][2]
				#print x,y,z
				#print "left",x+LeftShift(z*25),y,z, Proj(x+LeftShift(z*25),y,z)
				#print "right",x+RightShift(z*25),y,z, Proj(x+RightShift(z*25),y,z)


				#Shape.append(Proj(x,y,z,0,0,counter))
				Left.append( Proj(x+LeftShift(z*5),y,z,0,0,counter))
				Right.append(Proj(x+RightShift(z*5),y,z,0,0,counter))	

		#framy.PolyLineOneColor(Shape, c = white,  PL = 0, closed = False)
		framy.PolyLineOneColor(Left,  c = red,    PL = 1, closed = False)
		framy.PolyLineOneColor(Right, c = green,   PL = 2, closed = False)
		'''
		framy.rPolyLineOneColor(Shape, c = white,  PL = 0, closed = False, xpos = 200, ypos = 250, resize = 1.5, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Left,  c = red,    PL = 1, closed = False, xpos = 200, ypos = 250, resize = 1.5, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Right, c = blue,   PL = 2, closed = False, xpos = 200, ypos = 250, resize = 1.5, rotx =0, roty =0 , rotz=0)
		'''
		#print framy.LinesPL(0)
		#print framy.LinesPL(1)
		#print framy.LinesPL(2)

		#counter -= 1
		#if counter >360:
		#	counter =0


def Draw1PL():

	Shape = []
	Left = []
	Right = []
	counter =0

	while 1:
	
		yfactor = 10
		Left = []
		Right = []
		x = -1
		z = -0.1
		for step in y0:

			Left.append( Proj(x+LeftShift(z*25),step/yfactor,z,0,0,0))
			Right.append(Proj(x+RightShift(z*25),step/yfactor,z,0,0,0))	
			x += 0.02

		framy.rPolyLineOneColor(Left,  c = red,    PL = 0, closed = False, xpos = 0, ypos = 10, resize = 1.5, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Right, c = green,   PL = 0, closed = False, xpos = 0, ypos = 10, resize = 1.5, rotx =0, roty =0 , rotz=0)



		Left = []
		Right = []
		x = -1
		z = 0
		for step in y1:

			Left.append( Proj(x+LeftShift(z*25),step/yfactor,z,0,0,0))
			Right.append(Proj(x+RightShift(z*25),step/yfactor,z,0,0,0))	
			x += 0.02

		framy.rPolyLineOneColor(Left,  c = red,    PL = 0, closed = False, xpos = 0, ypos = 25, resize = 1.5, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Right, c = green,   PL = 0, closed = False, xpos = 0, ypos = 25, resize = 1.5, rotx =0, roty =0 , rotz=0)



		Left = []
		Right = []
		x = -1
		z = 0.1
		for step in y2:

			Left.append( Proj(x+LeftShift(z*25),step/yfactor,z,0,0,0))
			Right.append(Proj(x+RightShift(z*25),step/yfactor,z,0,0,0))	
			x += 0.02

		framy.rPolyLineOneColor(Left,  c = red,    PL = 0, closed = False, xpos = 0, ypos = 50, resize = 1.5, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Right, c = green,   PL = 0, closed = False, xpos = 0, ypos = 50, resize = 1.5, rotx =0, roty =0 , rotz=0)




		'''
		framy.rPolyLineOneColor(Shape, c = white,  PL = 0, closed = False, xpos = 200, ypos = 250, resize = 1.5, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Left,  c = red,    PL = 1, closed = False, xpos = 200, ypos = 250, resize = 1.5, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Right, c = blue,   PL = 2, closed = False, xpos = 200, ypos = 250, resize = 1.5, rotx =0, roty =0 , rotz=0)
		'''
		framy.LinesPL(0)
		time.sleep(0.1)

white = rgb2int(255,255,255)
red = rgb2int(255,0,0)
blue = rgb2int(0,0,255)
green = rgb2int(0,255,0)

y0 = ssine(100,5,-0.5)
y1 = ssine(100,5,0)
y2 = ssine(100,5,0.5)

Draw1PL()