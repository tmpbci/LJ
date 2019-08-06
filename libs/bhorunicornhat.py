#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Bhorunicornhat
v0.7.0

A library to replace unicornhat and unicorn_hat_sim to use
any unicorn hat python script with a bhoreal or a Launchpad mini.

2 things to do :

1/ Change import in a unicorn target python program 

import unicornhat as unicorn

by :

import bhorunicornhat as unicorn

2/ Set target (bhoreal or launchpad) by calling unicornhat.dest(device,rotation) 
or modify destination and rotation manually : see a few lines down.



by Sam Neurohack 
from /team/laser

CC NC BY

'''
import colorsys,time
import midi3,bhoreal,launchpad

# For Launchpad mini
mididest = "launchpad"
rotangle = 270

# For Bhoreal 
#mididest = "bhoreal"
#rotangle = 180

BhorLeds = [0] * 64
Bhuffer = [0] * 64
HAT = (8,8)
AUTO = (8,8)

# 'launchpad' with rotation 270
# 'bhoreal' with rotation 180
def dest(dest,rot):
	global mididest, rotangle

	mididest = dest
	rotangle = rot

def set_layout(x):
	pass


def rot90():
	
	for notes in range(0,64):
		Bhuffer[notes] = BhorLeds[notes]
		
	for y in range(1,9):
		for x in range(1,9):
			#print x,y,9-y,x,bhoreal.NoteXY(9-y,x),bhoreal.NoteXY(x,y),BhorLeds[bhoreal.NoteXY(9-y,x)],Bhuffer[bhoreal.NoteXY(x,y)]
			BhorLeds[bhoreal.NoteXY(9-y,x)]=Bhuffer[bhoreal.NoteXY(x,y)]
	
def rot180():

	for notes in range(0,64):
		Bhuffer[notes] = BhorLeds[notes]

	for y in range(8,0,-1):
		#print ""
		for x in range(1,9):
			#print x,y,9-y,bhoreal.NoteXY(x,9-y),bhoreal.NoteXY(x,y),BhorLeds[bhoreal.NoteXY(x,9-y)],Bhuffer[bhoreal.NoteXY(x,y)]
			BhorLeds[bhoreal.NoteXY(x,9-y)]=Bhuffer[bhoreal.NoteXY(x,y)]

def rotation(angle):
	if angle == 90:
		rot90()
	if angle == 180:
		rot180()
	if angle == 270:
		rot180()
		rot90()

def brightness(brightness):
	#like 0.5
	pass

def get_shape():
	return 8,8

def clear():
	off()

def hue(r,g,b):

	h = int(127*colorsys.rgb_to_hsv(r,g,b)[0])
	v = int(127*colorsys.rgb_to_hsv(r,g,b)[2])
	if h == 0 and v != 0:
		h=127
		#should be variation of grey (v,v,v)
		#v = int(127*colorsys.rgb_to_hsv(r,g,b)[2])
	#print r,g,b,h
	return h

def off():
	for note in range(1,64):
		BhorLeds[note] = 0
		show()

def set_all(r,g,b):

	for led in range(0,64):
		BhorLeds[led] = hue(r,g,b)

def set_pixel(x,y,r,g,b):

	#print x,y,r,g,b,colorsys.rgb_to_hsv(r,g,b)
	note = (x-1)+ (y-1) * 8 
	#print int(127*colorsys.rgb_to_hsv(r,g,b)[0])
	BhorLeds[note] = hue(r,g,b)

def set_pixels(pixels):
	led = 0
	for line in pixels:
		#print line
		for ledline in range(0,8):
			#print line[ledline]
			r,g,b = line[ledline][0],line[ledline][1],line[ledline][2]
			BhorLeds[led] = hue(r,g,b)
			led += 1
	
def clean_shutdown():
    pass

def show():

	# How turn off all leds 
	'''
	if bhoreal.Here != -1:
		bhoreal.Cls(0)

	if launchpad.Here != -1:
		launchpad.Cls()
	'''

	# Check if midi3 has been previously initiated
	if len(midi3.OutDevice) == 0:
		midi3.OutConfig()


	if (mididest == 'launchpad' and launchpad.Here != -1) or (mididest == 'bhoreal' and bhoreal.Here != -1):

		rotation(rotangle)
		for note in range(1,65):
			midi3.NoteOn(note-1,BhorLeds[note-1],mididest)
			time.sleep(0.0001)
	else:
		print(mididest,'is connected ?')
