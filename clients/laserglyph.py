# coding=UTF-8

'''
Anaglyphed cube

LICENCE : CC
'''

import redis
import framy
import math
import time

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
#observer_altitude = 10000
# elevation = z coordinate
 
# 0.0  or -2000 pop out)
map_plane_altitude = 0.0 

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



def Draw2PL():

	Shape = []
	Left = []
	Right = []
	counter =0

	while 1:
		Shape = []
		Left = []
		Right = []

		x = vertices[0][0]
		y = vertices[0][1]
		z = vertices[0][2]

		Left.append( Proj(x+LeftShift(z*5),y,z,0,0,counter))
		Right.append(Proj(x+RightShift(z*5),y,z,0,0,counter))	

		#framy.PolyLineOneColor(Shape, c = white,  PL = 0, closed = False)
		framy.PolyLineOneColor(Left,  c = red,    PL = 1, closed = False)
		framy.PolyLineOneColor(Right, c = green,   PL = 2, closed = False)

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
		framy.rPolyLineOneColor(Shape, c = white,  PL = 0, closed = False, xpos = 200, ypos = 250, resize = 1, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Left,  c = red,    PL = 1, closed = False, xpos = 200, ypos = 250, resize = 1, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Right, c = blue,   PL = 2, closed = False, xpos = 200, ypos = 250, resize = 1, rotx =0, roty =0 , rotz=0)
		'''
		#counter += 1
		#if counter >360:
		#	counter =0


def Draw1PL():

	Shape = []
	Left = []
	Right = []
	counter =0

	while 1:
		#Shape = []
		Left = []
		Right = []

		# Polyline will "move" the laser to this first point in black, then move to the next with second point color.
		# For more accuracy in dac emulator, repeat this first point.
		# Here the cube start always with vertice 0

		x = vertices[0][0]
		y = vertices[0][1]
		z = vertices[0][2]

		Left.append( Proj(x+LeftShift(z*5),y,z,0,counter,0))
		Right.append(Proj(x+RightShift(z*5),y,z,0,counter,0))	
		
		for fa in faces:
			#print ""
			#print "face",fa

			for point in fa:
				#print ""
				#print "point ", point 
				x = vertices[point][0]
				y = vertices[point][1]
				z = vertices[point][2]
				#print x,y,z,counter
				#if point == 0:
				#	print Proj(x+LeftShift(z*5),y,z,0,0,counter)
				#print "left", Proj(x+LeftShift(z*25),y,z,0,counter,0)
				#print "right",x+RightShift(z*25),y,z, Proj(x+RightShift(z*25),y,z)


				#Shape.append(Proj(x,y,z,0,0,counter))
				Left.append( Proj(x+LeftShift(z*25),y,z,0,counter,0))
				Right.append(Proj(x+RightShift(z*25),y,z,0,counter,0))	

		#framy.PolyLineOneColor(Shape, c = white,  PL = 0, closed = False)
		#print Left
		framy.PolyLineOneColor(Left,  c = red,    PL = 0, closed = True)
		framy.PolyLineOneColor(Right, c = green,   PL = 0, closed = True)

		'''
		framy.rPolyLineOneColor(Shape, c = white,  PL = 0, closed = False, xpos = 200, ypos = 250, resize = 1, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Left,  c = red,    PL = 1, closed = False, xpos = 200, ypos = 250, resize = 1, rotx =0, roty =0 , rotz=0)
		framy.rPolyLineOneColor(Right, c = blue,   PL = 2, closed = False, xpos = 200, ypos = 250, resize = 1, rotx =0, roty =0 , rotz=0)
		'''
		framy.LinesPL(0)
		time.sleep(0.1)
		counter += 1
		if counter >360:
			counter =0

white = rgb2int(255,255,255)
red = rgb2int(255,0,0)
blue = rgb2int(0,0,255)
green = rgb2int(0,255,0)


Draw1PL()
	#r.set('/pl/0/0', str(pl0))
# S = (e / 2) (d - p) / (a - d)


'''
# /pl/clientnumber/lasernumber pointlist

# Consider you're client 0
# Send to laser 0 (see mainy.conf)
r.set('/pl/0/0', str(pl0))

# Send to laser 1 (see mainy.conf)
r.set('/pl/0/1', str(pl1))
# Send to laser 2 (see mainy.conf)
r.set('/pl/0/2', str(pl1))
'''
