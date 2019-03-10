# coding=UTF-8

'''
LJ v0.8.1 in python3
Some LJ functions useful for python clients (was framy.py)

OSC functions commented, waiting working on OSC in python3 

Config(redisIP, client number) 
PolyLineOneColor
rPolyLineOneColor

Text(word, color, PL, xpos, ypos, resize, rotx, roty, rotz) : Display a word
Send(adress,message) : remote control. See commands.py
WebStatus(message) : display message on webui
DrawPL(point list number) : once you stacked all wanted elements, like 2 polylines, send them to lasers.
rgb2int(r,g,b)

OSCstart(): Start the OSC system.
OSCframe():
OSCstop(): Properly close the OSC system
OSCping(value): Answer to LJ pings

setup_controls(joystick) 

XboxController : getLeftHori, getLeftVert, getRightHori, getRightVert, getLeftTrigger, getRightTrigger
Ps3Controller : getLeftHori, getLeftVert, getRightHori, getRightVert, getLeftTrigger, getRightTrigger, getUp, getDown, getLeft, getRight, getFire1, getFire2(self):
MySaitekController : getLeftHori,getLeftVert, getRightHori,getRightVert, getLeftTrigger,getRightTrigger
MyThrustController : getLeftHori, getLeftVert, getRightHori, getRightVert, getLeftTrigger, getRightTrigger
CSLController : getLeftHori,getLeftVert,getRightHori, getRightVert,getLeftTrigger,getRightTrigger,getFire1,getFire2
my USB Joystick : getUp,getDown,getLeft,getRight,etLeftTrigger, getRightTrigger,getFire1, getFire2


LICENCE : CC
Sam Neurohack

'''

import math
import redis

# Import needed modules from osc4py3
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse


redisIP = '127.0.0.1'
r = redis.StrictRedis(host=redisIP, port=6379, db=0)

ClientNumber = 0

point_list = []
pl = [[],[],[],[]]

#
# OSC interaction with LJ
#

def OSCstart():
	# Start the system.
	osc_startup()
	#osc_udp_client(redisIP, 8002, "LJ 8002")

def OSCframe():
	#print("OSCprocess")
	osc_process()

# Properly close the system. Todo
def OSCstop():
	osc_terminate()


# Answer to LJ pings
def OSCping(value):
    # Will receive message address, and message data flattened in s, x, y
    print("I got /ping with value", value)
    Send("/pong",value)


def Send(oscaddress,oscargs=''):
        
    try:
        msg = oscbuildparse.OSCMessage(oscaddress, None, [oscargs])
        osc_send(msg, "LJ 8002")
       	OSCframe()

    except:
        print ('Connection to LJ refused : died ?')
        pass
'''
def handlerfunction(s, x, y):
    # Will receive message data unpacked in s, x, y
    pass

def handlerfunction2(address, s, x, y):
    # Will receive message address, and message data flattened in s, x, y
    pass

# Make server channels to receive packets.
osc_udp_server("127.0.0.1", 3721, "localhost")
osc_udp_server("0.0.0.0", 3724, "anotherserver")
'''



ASCII_GRAPHICS = [

# caracteres corrects

	[(-50,30), (-30,-30), (30,-30), (10,30), (-50,30)],							#0
	[(-20,30), (0,-30), (-20,30)], 												#1
	[(-30,-10), (0,-30), (30,-10), (30,0), (-30,30), (30,30)],					#2
	[(-30,-30), (0,-30), (30,-10), (0,0), (30,10), (0,30), (-30,30)],				#3
	[(30,10), (-30,10), (0,-30), (0,30)],											#4
	[(30,-30), (-30,-30), (-30,0), (0,0), (30,10), (0,30), (-30,30)],				#5
	[(30,-30), (0,-30), (-30,-10), (-30,30), (0,30), (30,10), (30,0), (-30,0)],	#6
	[(-30,-30), (30,-30), (-30,30)],												#7
	[(-30,30), (-30,-30), (30,-30), (30,30), (-30,30), (-30,0), (30,0)],			#8
	[(30,0), (-30,0), (-30,-10), (0,-30), (30,-30), (30,10), (0,30), (-30,30)],	#9

# caracteres a implementer	
	[(-30,10), (30,-10), (30,10), (0,30), (-30,10), (-30,-10), (0,-30), (30,-10)], #:
	[(-30,-10), (0,-30), (0,30)], [(-30,30), (30,30)],							#;
	[(-30,-10), (0,-30), (30,-10), (30,0), (-30,30), (30,30)],					#<
	[(-30,-30), (0,-30), (30,-10), (0,0), (30,10), (0,30), (-30,30)],				#=
	[(30,10), (-30,10), (0,-30), (0,30)],											#>
	[(30,-30), (-30,-30), (-30,0), (0,0), (30,10), (0,30), (-30,30)],				#?
	[(30,-30), (0,-30), (-30,-10), (-30,30), (0,30), (30,10), (30,0), (-30,0)],	#@

# Caracteres corrects
	

	[(-30,30), (-30,-30), (30,-30), (30,30), (30,0), (-30,0)],				#A
	[(-30,30), (-30,-30), (30,-30), (30,30), (30,0), (-30,0)],				#A
	[(-30,30), (-30,-30), (30,-30), (30,30), (-30,30), (-30,0), (30,0)],		#B
	[(30,30), (-30,30), (-30,-30), (30,-30)],									#C
	[(-30,30), (-30,-30), (30,-30), (30,30), (-30,30)],						#D
	[(30,30), (-30,30), (-30,-0), (30,0), (-30,0), (-30,-30), (30,-30)],		#E
	[(-30,30), (-30,-0), (30,0), (-30,0), (-30,-30), (30,-30)],				#F
	[(0,0), (30,0), (30,30), (-30,30), (-30,-30),(30,-30)],					#G
	[(-30,-30), (-30,30), (-30,0), (30,0), (30,30), (30,-30)],				#H
	[(0,30), (0,-30)],														#I
	[(-30,30), (0,-30), (0,-30), (-30,-30), (30,-30)],						#J
	[(-30,-30), (-30,30), (-30,0), (30,-30), (-30,0), (30,30)],				#K
	[(30,30), (-30,30), (-30,-30)],											#L
	[(-30,30), (-30,-30), (0,0), (30,-30), (30,30)],							#M
	[(-30,30), (-30,-30), (30,30), (30,-30)],									#N
	[(-30,30), (-30,-30), (30,-30), (30,30), (-30,30)],						#O
	[(-30,0), (30,0), (30,-30), (-30,-30), (-30,30)],							#P
	[(30,30), (30,-30), (-30,-30), (-30,30), (30,30),(35,35)],				#Q
	[(-30,30), (-30,-30), (30,-30), (30,0), (-30,0), (30,30)],				#R
	[(30,-30), (-30,-30), (-30,0), (30,0), (30,30), (-30,30)],				#S
	[(0,30), (0,-30), (-30,-30), (30,-30)],									#T
	[(-30,-30), (-30,30), (30,30), (30,-30)],									#U
	[(-30,-30), (0,30), (30,-30)],											#V
	[(-30,-30), (-30,30), (0,0), (30,30), (30,-30)],							#W
	[(-30,30), (30,-30)], [(-30,-30), (30,30)],								#X
	[(0,30), (0,0), (30,-30), (0,0), (-30,-30)],								#Y
	[(30,30), (-30,30), (30,-30), (-30,-30)],									#Z
	
				# A implementer	

	[(-30,-10), (0,-30), (0,30)], [(-30,30), (30,30)],							#[
	[(-30,-10), (0,-30), (30,-10), (30,0), (-30,30), (30,30)],					#\
	[(-30,-30), (0,-30), (30,-10), (0,0), (30,10), (0,30), (-30,30)],				#]
	[(30,10), (-30,10), (0,-30), (0,30)],											#^
	[(30,-30), (-30,-30), (-30,0), (0,0), (30,10), (0,30), (-30,30)],				#_
	[(30,-30), (0,-30), (-30,-10), (-30,30), (0,30), (30,10), (30,0), (-30,0)],	#`
	
			# Implementé
	
	[(-20,20), (-20,-20), (20,-20), (20,20), (20,0), (-20,0)],				#a
	[(-20,20), (-20,-20), (20,-20), (20,20), (-20,20), (-20,0), (20,0)],		#b
	[(20,20), (-20,20), (-20,-20), (20,-20)],									#c
	[(-20,20), (-20,-20), (20,-20), (20,20), (-20,20)],						#d
	[(20,20), (-20,20), (-20,-0), (20,0), (-20,0), (-20,-20), (20,-20)],		#e
	[(-20,20), (-20,-0), (20,0), (-20,0), (-20,-20), (20,-20)],				#f
	[(0,0), (20,0), (20,20), (-20,20), (-20,-20),(20,-20)],					#g
	[(-20,-20), (-20,20), (-20,0), (20,0), (20,20), (20,-20)],				#H
	[(0,20), (0,-20)],														#I
	[(-20,20), (0,-20), (0,-20), (-20,-20), (20,-20)],						#J
	[(-20,-20), (-20,20), (-20,0), (20,-20), (-20,0), (20,20)],				#K
	[(20,20), (-20,20), (-20,-20)],											#L
	[(-20,20), (-20,-20), (0,0), (20,-20), (20,20)],							#M
	[(-20,20), (-20,-20), (20,20), (20,-20)],									#N
	[(-20,20), (-20,-20), (20,-20), (20,20), (-20,20)],						#O
	[(-20,0), (20,0), (20,-20), (-20,-20), (-20,20)],							#P
	[(20,20), (20,-20), (-20,-20), (-20,20), (20,20),(25,25)],				#Q
	[(-20,20), (-20,-20), (20,-20), (20,0), (-20,0), (20,20)],				#R
	[(20,-20), (-20,-20), (-20,0), (20,0), (20,20), (-20,20)],				#S
	[(0,20), (0,-20), (-20,-20), (20,-20)],									#T
	[(-20,-20), (-20,20), (20,20), (20,-20)],									#U
	[(-20,-20), (0,20), (20,-20)],											#V
	[(-20,-20), (-20,20), (0,0), (20,20), (20,-20)],							#W
	[(-20,20), (20,-20)], [(-20,-20), (20,20)],								#X
	[(0,20), (0,0), (20,-20), (0,0), (-20,-20)],								#Y
	[(20,20), (-20,20), (20,-20), (-20,-20)],									#Z

	[(-2,15), (2,15)]															# Point a la place de {
]

def rgb2int(r,g,b):
    return int('0x%02x%02x%02x' % (r,g,b),0)


def Config(redisIP,client):
	global ClientNumber

	r = redis.StrictRedis(host=redisIP, port=6379, db=0)	
	ClientNumber = client
	osc_udp_client(redisIP, 8002, "LJ 8002")


def LjClient(client):
	global ClientNumber

	ClientNumber = client
 

 
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
			LineTo(xy0,c, PL)
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
			LineTo(Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz),c, PL)
		else:
			LineTo(Pointransf(xy, xpos, ypos, resize, rotx, roty, rotz),c, PL)
	if closed:
		LineTo(Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz),c, PL)

 
def LinesPL(PL):
	print ("Stupido !! your code is to old : use DrawPL() instead of LinesPL()")
	DrawPL(PL)

def DrawPL(PL):
	#print '/pl/0/'+str(PL), str(pl[PL])
	if r.set('/pl/'+str(ClientNumber)+'/'+str(PL), str(pl[PL])) == True:
		pl[PL] = []
		return True
	else:
		return False

def ResetPL(self, PL):
	pl[PL] = []



def DigitsDots(number,color):
	dots =[]
	for dot in ASCII_GRAPHICS[number]:
		#print dot
		dots.append((gstt.xy_center[0]+dot[0],gstt.xy_center[1]+dot[1],color))
		#self.point_list.append((xy + (c,)))
	return dots

def CharDots(char,color):

	dots =[]
	for dot in ASCII_GRAPHICS[ord(char)-46]:
		dots.append((dot[0],dot[1],color))
	return dots

def Text(message,c, PL, xpos, ypos, resize, rotx, roty, rotz):

	dots =[]

	l = len(message)
	i= 0
	#print message
	
	for ch in message:
		
		#print ""
		# texte centre en x automatiquement selon le nombre de lettres l
		x_offset = 26 * (- (0.9*l) + 3*i)
		#print i,x_offset
		# if digit 
		if ord(ch)<58:
			char_pl_list = ASCII_GRAPHICS[ord(ch) - 48]
		else: 
			char_pl_list = ASCII_GRAPHICS[ord(ch) - 46 ]
			
		char_draw = []
		#dots.append((char_pl_list[0][0] + x_offset,char_pl_list[0][1],0))

		for xy in char_pl_list:
			char_draw.append((xy[0] + x_offset,xy[1],c))
		i +=1
		#print ch,char_pl_list,char_draw			
		rPolyLineOneColor(char_draw, c, PL , False, xpos, ypos, resize, rotx, roty, rotz)
		#print ("laser",PL,"message",message)
		#dots.append(char_draw)



import re

def setup_controls(joystick):
	"""
	Joystick wrapper.
	"""
	if re.search('playstation', joystick.get_name(), re.I):
		return Ps3Controller(joystick)

	elif re.search('X-box', joystick.get_name(), re.I):
		return XboxController(joystick)

	elif re.search('Saitek', joystick.get_name(), re.I):
		return MySaitekController(joystick)
	
	elif re.search('Thrustmaster dual analog 3.2', joystick.get_name(), re.I):
		return MyThrustController(joystick)
		
	elif re.search('2n1 USB', joystick.get_name(), re.I):
		return CSLController(joystick)

	elif re.search('Joystick', joystick.get_name(), re.I):
		return USBController(joystick)

	return Controller(joystick)

class Controller(object):

	def __init__(self, joystick):
		"""Pass a PyGame joystick instance."""
		self.js = joystick

	def getLeftHori(self):
		return self.js.get_axis(2)

	def getLeftVert(self):
		return self.js.get_axis(3)

	def getRightHori(self):
		return self.js.get_axis(0)

	def getRightVert(self):
		return self.js.get_axis(1)

	def getLeftTrigger(self):
		return self.js.get_button(9)

	def getRightTrigger(self):
		return self.js.get_button(2)

class XboxController(Controller):

	def __init__(self, joystick):
		super(XboxController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(3)

	def getRightVert(self):
		return self.js.get_axis(4)

	def getLeftTrigger(self):
		return self.js.get_axis(2)

	def getRightTrigger(self):
		return self.js.get_button(11)

class Ps3Controller(Controller):

#up  4 _DOWN   6 left  7 right 5 croix  14 rond 13 triangle 12

	def __init__(self, joystick):
		super(Ps3Controller, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(2)

	def getRightVert(self):
		return self.js.get_axis(3)

	def getLeftTrigger(self):
		# TODO: Verify
		return self.js.get_button(8)

	def getRightTrigger(self):
		# TODO: Verify
		return self.js.get_button(9)

	def getUp(self):
		return self.js.get_button(4)

	def getDown(self):
		return self.js.get_button(6)

	def getLeft(self):
		return self.js.get_button(7)

	def getRight(self):
		return self.js.get_button(5)

	def getFire1(self):
		return self.js.get_button(14)

	def getFire2(self):
		return self.js.get_button(13)


class MySaitekController(Controller):

	def __init__(self, joystick):
		super(MySaitekController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(3)

	def getRightVert(self):
		return self.js.get_axis(2)

	def getLeftTrigger(self):
		return self.js.get_button(6)

	def getRightTrigger(self):
		return self.js.get_button(7)

class MyThrustController(Controller):

	def __init__(self, joystick):
		super(MyThrustController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(2)

	def getRightVert(self):
		return self.js.get_axis(3)

	def getLeftTrigger(self):
		return self.js.get_button(5)

	def getRightTrigger(self):
		return self.js.get_button(7)


class CSLController(Controller):

	def __init__(self, joystick):
		super(CSLController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(2)

	def getLeftVert(self):
		return self.js.get_axis(3)

	def getRightHori(self):
		return self.js.get_axis(0)

	def getRightVert(self):
		return self.js.get_axis(1)

	def getLeftTrigger(self):
		return self.js.get_button(6)

	def getRightTrigger(self):
		return self.js.get_button(7)

	def getFire1(self):
		return self.js.get_button(2)

	def getFire2(self):
		return self.js.get_button(1)

class USBController(Controller):


# my USB Joystick 
#up  axis 0 -1 DOWN axis 0 1 left axis 1 1 right axis 1 -1 bouton gauche 10 bouton droite 9

	def __init__(self, joystick):
		super(USBController, self).__init__(joystick)


	def getUp(self):
		if self.js.get_axis(0) == -1:
			return  1
		else:
			return 0

	def getDown(self):
		if self.js.get_axis(0) > 0.9:
			return  1
		else:
			return 0

	def getLeft(self):
		if self.js.get_axis(1) == 1:
			return  1
		else:
			return 0

	def getRight(self):
		if self.js.get_axis(1) == -1:
			return  1
		else:
			return 0

	def getLeftTrigger(self):
		return self.js.get_button(10)

	def getRightTrigger(self):
		return self.js.get_button(9)

	def getFire1(self):
		if self.js.get_button(10) == 1:
			print ("fire 1")
		return self.js.get_button(10)

	def getFire2(self):
		if self.js.get_button(9) == 1:
			print ("fire 2")
		return self.js.get_button(9)



	
