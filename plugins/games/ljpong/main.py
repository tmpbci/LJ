#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''
LJ Laser Pong v0.8

Sam Neurohack

'''

import pygame
import math
import itertools
import sys
import os
import types
sys.path.append('../../../libs')
import lj


'''
is_py2 = sys.version[0] == '2'
if is_py2:
	from Queue import Queue
else:
	from queue import Queue
'''

import thread
import time
import random
import lj23 as lj
import entities
from controller import setup_controls
import argparse

from OSC import OSCServer, OSCClient, OSCMessage
OSCIP = "127.0.0.1"
OSCPort = 8020

score = None

screen_size = [800,600]

top_left = [200,100]
bottom_left = [200,300]
top_right = [600,100]
bottom_right = [600,300]

score_pos = [550,40]
score2_pos = [259,40]
text_pos = [300,500,200]

ball_origin = [400,300,200]
BALL_SPEED = 5
BALL_SIZE_X = 3
BALL_SIZE_Y = 3
BALL_acc = 0.06

PADDLE_height = 100
PADDLE_width = 10

FlipsSpeed = 7
FLIPS_lorigin = [10,300,0]
FLIPS_rorigin = [780,300,400]
FlipsLx, FlipsLy = FLIPS_lorigin[0], FLIPS_lorigin[1]
FlipsRx, FlipsRy = FLIPS_rorigin[0], FLIPS_rorigin[1]


xy_center = [screen_size[0]/2,screen_size[1]/2]

GAME_FS_QUIT = -1
GAME_FS_MENU = 0
GAME_FS_PLAY = 1
GAME_FS_GAMEOVER = 2
GAME_FS_LAUNCH = 2

SCORE_ZOOM_PLAYING = 1.6
SCORE_ZOOM_GAMEOVER = 5.0
SCORE_DZOOM_PLAYING = -0.4
SCORE_DZOOM_GAMEOVER = 0.1

Score1Zoom = SCORE_ZOOM_PLAYING

GRAVITY = 0.0001

fs = GAME_FS_MENU

def rgb2int(r,g,b):
	return int('0x%02x%02x%02x' % (r,g,b),0)

white = rgb2int(255,255,255)
red = rgb2int(255,0,0)
blue = rgb2int(0,0,255)
green = rgb2int(0,255,0)

#
# Arguments handling
#

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Laserpong")

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

entities.plnumber = plnumber

# Redis Computer IP
if args.redisIP  != None:
	redisIP  = args.redisIP
else:
	redisIP = '127.0.0.1'

lj.Config(redisIP,ljclient,"ljpong")


def StartPlaying(first_time = False):
	global fs

	lscore = 0
	rscore = 0
	fs = GAME_FS_LAUNCH
	x = ball_origin[0]
	y = ball_origin[1]

app_path = os.path.dirname(os.path.realpath(__file__))

# 
# Pads via pygame
#

print "Pygame init..."
pygame.init()
#sounds.InitSounds()

clock = pygame.time.Clock()


Nbpads = pygame.joystick.get_count()
print ("Joypads : ", str(Nbpads))

if Nbpads != 2:

	print ('')
	print ('')
	print ("THIS VERSION NEEDS 2 PADS. PLEASE CONNECT THEM.")
	print ('')
	sys.exit()
	


if Nbpads > 1:

	pad2 = pygame.joystick.Joystick(1)
	pad2.init()
	print "Pad2 :", pad2.get_name()
	numButtons = pad2.get_numbuttons()
	#print ("Axis Pad 2 :", str(pad2.get_numaxes()))
	#print ("Buttons Pad 2 :" , str(numButtons))
	
	# joy is pad abstraction to handle many different devices.
	joy2 = setup_controls(pad2)

if Nbpads > 0:

	pad1 = pygame.joystick.Joystick(0)
	pad1.init()
	print "Pad1 :",pad1.get_name()
	numButtons = pad1.get_numbuttons()
	joy1 = setup_controls(pad1)
	#print ("Axis Pad 1 :", str(pad1.get_numaxes()))
	#print ("Buttons Pad 1 :" , str(numButtons))

update_screen = False

xvel = - 1
yvel = 0
lscore = 0
rscore = 0
ly = FLIPS_lorigin[1]
ry = FLIPS_rorigin[1]
flipsy = [ly, ry]
stick = 0
x = ball_origin[0]
y = ball_origin[1]

keystates = pygame.key.get_pressed()

#
# OSC
# 

oscserver = OSCServer( (OSCIP, OSCPort) )
oscserver.timeout = 0
OSCRunning = True


def OSCljclient(path, tags, args, source):


	print("LJPong got /ljpong/ljclient with value", args[0])
	lj.WebStatus("LJPong to virtual "+ str(args[0]))
	ljclient = args[0]
	lj.LjClient(ljclient)

def OSCpl(path, tags, args, source):
	global plnumber

	print("LJ Pong got /ljpong/pl with value", args[0])
	lj.WebStatus("LJPong to pl "+ str(args[0]))
	plnumber = int(args[0])
	lj.LjPl(plnumber)
'''
# /ping
def OSCping(path, tags, args, source):

	print("LJ Pong got /ping")
	lj.SendLJ("/pong","ljpong")
	lj.SendLJ("/ljpong/start",1)
'''

def OSC_frame():
    # clear timed_out flag
    oscserver.timed_out = False
    # handle all pending requests then return
    while not oscserver.timed_out:
		oscserver.handle_request()


def handle_timeout(self):
    self.timed_out = True

print ""
print "Launching OSC server..."
print "at", OSCIP, "port",str(OSCPort)

oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)

# OSC callbacks
lj.addOSCdefaults(oscserver)
oscserver.addMsgHandler( "/ljpong/ljclient", OSCljclient )
oscserver.addMsgHandler("/ljpong/pl", OSCpl)
#oscserver.addMsgHandler("/ping", lj.OSCping)

print "Running..."

#
# Game main loop
#


while fs != GAME_FS_QUIT:


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			fs = GAME_FS_QUIT
	
	OSC_frame()

	keystates_prev = keystates[:]
	keystates = pygame.key.get_pressed()[:]


	# Etats du jeu
	
	if fs == GAME_FS_MENU:

		if keystates[pygame.K_ESCAPE] and not keystates_prev[pygame.K_ESCAPE]:
			fs = GAME_FS_QUIT
		elif keystates[pygame.K_SPACE] and not keystates_prev[pygame.K_SPACE]:
			StartPlaying(True)
			lscore = 0
			rscore = 0

		if joy1.getFire1() or joy2.getFire1():
			StartPlaying(False)
			lscore =0
			rscore = 0
		


	elif fs == GAME_FS_PLAY:

		if keystates[pygame.K_ESCAPE] and not keystates_prev[pygame.K_ESCAPE]:
			fs = GAME_FS_MENU

		'''
		if Nbpads > 0:
			print "pad 1 :", joy1.getUp(), joy1.getDown(), joy1.getLeftTrigger(),joy1.getRightTrigger()
			print "pad 2 :", joy2.getUp(), joy2.getDown(), joy2.getLeftTrigger(),joy2.getRightTrigger()
		'''

		# Lost ball / first to ten points ?
		#print " ball : " , x, y, " left : ", ly, " right : ", ry
		
		if x < FLIPS_lorigin[0] + PADDLE_width:

			print ("ball.y : ", y, " ly : ", ly)
			if y > (ly + PADDLE_height + 1) or y < (ly - BALL_SIZE_Y - 1):
				rscore += 1
				xvel = random.uniform(-1,-0.6)
				if rscore == 11:
					fs = GAME_FS_MENU
				else: 
					fs = GAME_FS_LAUNCH
			else:
				x = FLIPS_lorigin[0] + PADDLE_width
				xvel *= -1
			
				
		if x > FLIPS_rorigin[0] - PADDLE_width:
		
			print ("ball.y : ", y, " ry : ", ry)

			if y < (ry - BALL_SIZE_Y - 1) or y > (ry + PADDLE_height + 1):
				lscore += 1
				xvel = random.uniform(1,0.6)
				if lscore == 11:
					fs = GAME_FS_MENU
				else: 
					fs = GAME_FS_LAUNCH
			else:
				xvel *= -1
				x = FLIPS_rorigin[0] - PADDLE_width	
				
		# wall detect
		
		if y < 0:
			y = 1
			yvel *= -1
			
		if y > screen_size[1]:
			y = screen_size[1] - 1
			yvel *= -1
			
		# Anim 
		
		x += BALL_SPEED * xvel 
		y += BALL_SPEED * yvel
		yvel += GRAVITY
		entities.BallMove(x,y)

		if  Nbpads > 0:
			flipsy =  entities.FlipsMove(joy1.getUp(),joy1.getDown(),joy2.getUp(),joy2.getDown())

		else:
			flipsy =  entities.FlipsMove(keystates[pygame.K_a],keystates[pygame.K_q],keystates[pygame.K_UP],keystates[pygame.K_DOWN])
		
		ly = flipsy[0]
		ry = flipsy[1]

	

	elif fs == GAME_FS_LAUNCH:
	
		'''
		if Nbpads > 0:
			print "pad 1 :", joy1.getUp(), joy1.getDown(), joy1.getLeftTrigger(),joy1.getRightTrigger()
			print "pad 2 :", joy2.getUp(), joy2.getDown(), joy2.getLeftTrigger(),joy2.getRightTrigger()
			print pad1.get_axis(0),pad2.get_axis(0)
		'''

		if keystates[pygame.K_ESCAPE] and not keystates_prev[pygame.K_ESCAPE]:
			fs = GAME_FS_MENU

		if keystates[pygame.K_SPACE] and not keystates_prev[pygame.K_SPACE]:
			fs = GAME_FS_PLAY
			yvel = 0
			while math.fabs(xvel + yvel) < 1:
				#xvel = random.uniform(-1,1)
				yvel = random.uniform(-1,1)
			
		if joy1.getFire1() or joy2.getFire1():
			fs = GAME_FS_PLAY
			yvel = 0
			while math.fabs(xvel + yvel) < 1:
				#xvel = random.uniform(-1,1)
				yvel = random.uniform(-1,1)
			
		x = ball_origin[0]
		y = ball_origin[1]
		entities.BallMove(x,y)

		if  Nbpads > 0:
			flipsy =  entities.FlipsMove(joy1.getUp(),joy1.getDown(),joy2.getUp(),joy2.getDown())
		
		else:
			flipsy =  entities.FlipsMove(keystates[pygame.K_a],keystates[pygame.K_q],keystates[pygame.K_UP],keystates[pygame.K_DOWN])
		ly = flipsy[0]
		ry = flipsy[1]



	elif fs == GAME_FS_GAMEOVER:

		#TODO : MODE GAME OVER, autres opérations d'animation
		# Remarque : on peut supprimer le mode GAME OVER et le gérer dans le mode jeu
		# si les traitements sont les mêmes
		'''
		if keystates[pygame.K_SPACE] and not keystates_prev[pygame.K_SPACE]:
			StartPlaying(False)
		'''

		if joy1.getFire1() or joy2.getFire1():
			StartPlaying(False)

		elif keystates[pygame.K_ESCAPE] and not keystates_prev[pygame.K_ESCAPE]:
			fs = GAME_FS_MENU
			# Peut-être aussi réinitialiser l'état dans le mode menu
	
		
	if fs == GAME_FS_PLAY or fs == GAME_FS_GAMEOVER or fs == GAME_FS_LAUNCH:

		entities.Score1Draw(lscore, plnumber)
		entities.Score2Draw(rscore, plnumber)
		entities.FlipsDraw(plnumber)
		entities.BallDraw(plnumber)
		entities.FiletDraw(plnumber)
		lj.DrawPL(plnumber)

	if fs == GAME_FS_MENU:
		
		entities.LogoDraw(plnumber)
		lj.DrawPL(plnumber)

	
	clock.tick(100)

pygame.quit()

