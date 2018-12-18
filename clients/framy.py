# coding=UTF-8

'''
LJay v0.8.0


LICENCE : CC
pclf, Sam Neurohack

'''

import math
import redis

redisIP = '192.168.1.13'
r = redis.StrictRedis(host=redisIP, port=6379, db=0)

point_list = []
pl = [[],[],[],[]]

def LineTo(xy, c, PL):
 
	pl[PL].append((xy + (c,)))

def Line(xy1, xy2, c, PL):
	LineTo(xy1, 0, PL)
	LineTo(xy2, c , PL)


def PolyLineOneColor(xy_list, c, PL , closed ):
	#print "--"
	#print "c",c
	#print "xy_list",xy_list
	#print "--"
	xy0 = None		
	for xy in xy_list:
		if xy0 is None:
			xy0 = xy
			#print "xy0:",xy0
			LineTo(xy0,0, PL)
		else:
			#print "xy:",xy
			LineTo(xy,c, PL)
	if closed:
		LineTo(xy0,c, PL)


# Computing points coordinates for rPolyline function from 3D and around 0,0 to pygame coordinates
def Pointransf(xy, xpos = 0, ypos =0, resize =1, rotx =0, roty =0 , rotz=0):

		x = xy[0] * resize
		y = xy[1] * resize
		z = 0

		rad = rotx * math.pi / 180
		cosaX = math.cos(rad)
		sinaX = math.sin(rad)

		y2 = y
		y = y2 * cosaX - z * sinaX
		z = y2 * sinaX + z * cosaX

		rad = roty * math.pi / 180
		cosaY = math.cos(rad)
		sinaY = math.sin(rad)

		z2 = z
		z = z2 * cosaY - x * sinaY
		x = z2 * sinaY + x * cosaY

		rad = rotz * math.pi / 180
		cosZ = math.cos(rad)
		sinZ = math.sin(rad)

		x2 = x
		x = x2 * cosZ - y * sinZ
		y = x2 * sinZ + y * cosZ

		#print xy, (x + xpos,y+ ypos)
		return (x + xpos,y+ ypos)
		'''
		to understand why it get negative Y
		
		# 3D to 2D projection
		factor = 4 * gstt.cc[22] / ((gstt.cc[21] * 8) + z)
		print xy, (x * factor + xpos,  - y * factor + ypos )
		return (x * factor + xpos,  - y * factor + ypos )
		'''

# Send 2D point list around 0,0 with 3D rotation resizing and reposition around xpos ypos
#def rPolyLineOneColor(self, xy_list, c, PL , closed, xpos = 0, ypos =0, resize =1, rotx =0, roty =0 , rotz=0):
def rPolyLineOneColor(xy_list, c, PL , closed, xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0):
	xy0 = None		
	for xy in xy_list:
		if xy0 is None:
			xy0 = xy
			LineTo(Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz),0, PL)
		else:
			LineTo(Pointransf(xy, xpos, ypos, resize, rotx, roty, rotz),c, PL)
	if closed:
		LineTo(Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz),c, PL)


# set all points for given laser. special behavior depends on GridDisplay flag
# 0: point list / 1: Grid 
def LinesPL(PL):

	if r.set('/pl/0/'+str(PL), str(pl[PL])) == True:
		return True
	else:
		return False

def ResetPL(self, PL):
	pl[PL] = []
