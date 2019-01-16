#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''

LJ Laser Pong entities
v0.1

Sam Neurohack

'''


# STDLIB
import math
import itertools
import sys
import os
import lj

import time
import random



screen_size = [800,600]

top_left = [200,100]
bottom_left = [200,300]
top_right = [600,100]
bottom_right = [600,300]

score_pos = [550,40]
score2_pos = [259,40]

# X Y position on bottom left of each paddle (="flips")
ball_origin = [400,300,200]
text_pos = [300,500,200]
BALL_acc = 0.06
PADDLE_height = 100
PADDLE_width = 10
PADDLE3D_height = 100
PADDLE3D_width = 100
FACT3D = 2
FLIPS_lorigin = [10,300,0]
FLIPS_rorigin = [780,300,400]
flips_attraction = 0.007

xy_center = [screen_size[0]/2,screen_size[1]/2]

DEFAULT_SPOKES = range(0,359,60)
DEFAULT_PLAYER_EXPLODE_COLOR = 0xFFFF00
DEFAULT_SIDE_COUNT = 6
DREARRANGE_SIDES = .02


CRASH_SHAKE_MAX = 6
TDN_CRASH = 200

GAME_FS_QUIT = -1
GAME_FS_MENU = 0
GAME_FS_PLAY = 1
GAME_FS_LAUNCH = 2
GAME_FS_GAMEOVER = 3

BUMPERS_COLOR_YELLOW = 0xFFFF00
BUMPERS_COLOR_RED = 0xFF0000
BUMPERS_COLOR_BLACK = 0x000000
BUMPERS_SIZE_X = 60
BUMPERS_SIZE_Y = 110
BUMPERS_FORCE = 1.1


BALL_SPEED = 5
BALL_MAX = 4
BALL_SIZE_X = 3
BALL_SIZE_Y = 3
LASER_ANGLE = 0



GRAVITY = 0.0001

NO_BGM = False
#NO_BGM = True

def rgb2int(r,g,b):
	return int('0x%02x%02x%02x' % (r,g,b),0)

white = rgb2int(255,255,255)
red = rgb2int(255,0,0)
blue = rgb2int(0,0,255)
green = rgb2int(0,255,0)


LOGO = [
	# L/o
	[[(-140,-100),(-200,20),(40,20)],0xFF00],
	# aser
	[[(-140,-40),(-100,-40,),(-120,0),(-160,0),(-110,-20)],0xFFFF],
	[[(-40,-40),(-60,-40),(-90,-20),(-50,-20),(-80,0),(-100,0)],0xFFFF],
	[[(-30,-20),(10,-20),(0,-40),(-20,-40),(-30,-20),(-30,0),(-10,0)],0xFFFF],
	[[(20,0),(40,-40),(35,-30),(50,-40),(70,-40)],0xFFFF],
	# Pinball
	[[(-185,50),(-145,50),(-130,20),(-170,20),(-200,80)],0xFFFF00],  	#P
	[[(-80,40),(-120,40),(-140,80),(-100,80),(-80,40)],0xFFFF],			#O
	[[(-80,80),(-60,40),(-65,50),(-40,40),(-25,50),(-40,80)],0xFFFF],	#N
	[[(40,40),(0,40),(-20,80),(20,80),(30,60),(10,60)],0xFFFF],		#G
	]


LOGO_OFFSET_X = 460
LOGO_OFFSET_Y = 250

def LogoDraw():
	'''
	Dessine le logo
	'''
	for pl_color in LOGO:
		c = pl_color[1]
		xy_list = []
		for xy in pl_color[0]:
			xy_list.append((LOGO_OFFSET_X + xy[0], LOGO_OFFSET_Y + xy[1]))
		#print xy_list
		lj.PolyLineOneColor(xy_list, c,0, False)




FlipsLx, FlipsLy = FLIPS_lorigin[0], FLIPS_lorigin[1]
FlipsRx, FlipsRy = FLIPS_rorigin[0], FLIPS_rorigin[1]
FlipsSpeed = 7
	
	
def FlipsMove(left_key,right_key,up_key,down_key):
	global FlipsLx, FlipsLy, FlipsRx, FlipsRy 

	if left_key:
		FlipsLy -= FlipsSpeed
		if FlipsLy < 1:
			FlipsLy = 1
		
	if right_key:
		FlipsLy += FlipsSpeed
		if FlipsLy > screen_size[1] - PADDLE_height:
			FlipsLy = screen_size[1]  - PADDLE_height

	if up_key:
		FlipsRy -= FlipsSpeed
		if FlipsRy < 1:
			FlipsRy = 1			
			
	if down_key:
		FlipsRy += FlipsSpeed
		if FlipsRy > screen_size[1] - PADDLE_height:
			FlipsRy = screen_size[1]  - PADDLE_height

	return FlipsLy, FlipsRy
	
def FlipsMoveJoy(left_key,right_key,up_key,down_key,lvertax):

	if left_key:
		FlipsLy -= FlipsSpeed
		if FlipsLy < 1:
			FlipsLy = 1
		
	if right_key:
		FlipsLy += FlipsSpeed
		if FlipsLy > screen_size[1] - PADDLE_height:
			FlipsLy = screen_size[1]  - PADDLE_height

	if up_key:
		FlipsRy -= FlipsSpeed
		if FlipsRy < 1:
			FlipsRy = 1			
	if down_key > 0.01:
		FlipsRy += FlipsSpeed
		if FlipsRy > screen_size[1] - PADDLE_height:
			FlipsRy = screen_size[1]  - PADDLE_height
	
	if lvertax:
		print lvertax
		if lvertax < 0:
			FlipsLy -= FlipsSpeed
			if FlipsLy < 1:
				FlipsLy = 1
		elif lvertax > 0.01:
			FlipsLy += FlipsSpeed
			if FlipsLy > screen_size[1] - PADDLE_height:
				FlipsLy = screen_size[1]  - PADDLE_height
	return FlipsLy, FlipsRy

def FlipsDraw():

	lj.PolyLineOneColor([(FlipsLx,FlipsLy),(FlipsLx,FlipsLy + PADDLE_height),(FlipsLx + PADDLE_width , FlipsLy + PADDLE_height),(FlipsLx + PADDLE_width,FlipsLy)], white,0,True)
	lj.PolyLineOneColor([(FlipsRx,FlipsRy),(FlipsRx,FlipsRy + PADDLE_height),(FlipsRx + PADDLE_width , FlipsRy + PADDLE_height),(FlipsRx + PADDLE_width,FlipsRy)], white,0,True)


def FiletDraw():
	lj.PolyLineOneColor([(screen_size[0]/2,screen_size[1]),(screen_size[0]/2,0)], white, 0,True)


def Score1Draw(score):
	#print "score1",score
	lj.Text(str(score),white, 0, 350, 50, 1, 0, 0, 0)
	
def Score2Draw(score):
	#print "score2",score
	lj.Text(str(score),white, 0, 500, 50, 1, 0, 0, 0)
	
		
	
BallX, BallY = ball_origin[0], ball_origin[1]
BallZoom = 1
		
		
def BallMove(xcoord,ycoord):
	global BallX,BallY
		
	BallX = xcoord
	BallY = ycoord
	#print "ball move",xcoord,ycoord
	
	#BallZoom = ?
	
	if BallX < 0:
		BallX = 0
		
	elif BallX >= screen_size[0]:
		BallX = screen_size[0]
		
	if BallY < 0:
		BallY = 0
		
	elif BallY >= screen_size[1]:
		BallY = screen_size[1]

def BallDraw():
	global BallX,BallY

	xmin = 0
	xmax = BALL_SIZE_X * 2
	ymin = 0
	ymax = BALL_SIZE_Y * 2
		
	xmin = (xmin*BallZoom)
	ymin = (ymin*BallZoom) 		
	xmax = (xmax*BallZoom) 
	ymax = (ymax*BallZoom)

	xmin += BallX 
	xmax += BallX
	ymin += BallY 
	ymax += BallY

	#print "ball position",xmin,xmax,ymin,ymax
		
	lj.PolyLineOneColor([(xmin,ymin),(xmin,ymax),(xmax,ymax),(xmax,ymin)], white,0,True)

