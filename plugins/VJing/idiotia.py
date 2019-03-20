#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
LJ v0.8.1

IdiotIA for THSF 10

Include IdiotIA and Starfields


LICENCE : CC
Sam Neurohack, Loloster, 

'''


import math

import numpy as np
import pdb
from datetime import datetime
from random import randrange
import redis
import lj3
import sys,time
import os

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
#from osc4py3 import oscmethod as osm
from osc4py3.oscmethod import * 
import argparse



screen_size = [700,700]
xy_center = [screen_size[0]/2,screen_size[1]/2]

message = "LO"
OSCinPort = 8011

redisIP = '127.0.0.1'
ljclient = 0

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Pose bank for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)

args = argsparser.parse_args()


if args.verbose:
    debug = args.verbose
else:
    debug = 0

if args.client:
    ljclient = args.client
else:
    ljclient = 0

# Redis Computer IP
if args.redisIP  != None:
    redisIP  = args.redisIP
else:
    redisIP = '127.0.0.1'


lj3.Config(redisIP,ljclient)


def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))


def rgb2hex(rgb):
    return int('0x%02x%02x%02x' % tuple(rgb),0)


# IdiotIA
import json
CurrentPose = 1

# Get frame number for pose path describe in PoseDir 
def lengthPOSE(pose_dir):

    #if debug > 0:
    #  print("Check directory",'poses/' + pose_dir)
    if os.path.exists('poses/' + pose_dir):
      numfiles = sum(1 for f in os.listdir('poses/' + pose_dir) if os.path.isfile(os.path.join('poses/' + pose_dir + '/', f)) and f[0] != '.')
      return numfiles
    else:
      if debug > 0:
        print("but it doesn't even exist!")
      return 0


# get absolute face position points 
def getFACE(pose_json,pose_points, people):

    dots = []
    for dot in pose_points:

        if len(pose_json['people'][people]['face_keypoints_2d']) != 0:
            #print "people 0"
            if pose_json['people'][people]['face_keypoints_2d'][dot * 3] != -1 and  pose_json['people'][people]['face_keypoints_2d'][(dot * 3)+1] != -1:
                dots.append((pose_json['people'][people]['face_keypoints_2d'][dot * 3], pose_json['people'][people]['face_keypoints_2d'][(dot * 3)+1]))

    return dots


# Face keypoints
def face(pose_json, people):
    pose_points = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    return getFACE(pose_json,pose_points, people)

def browL(pose_json, people):
    pose_points = [26,25,24,23,22]
    return getFACE(pose_json,pose_points, people)

def browR(pose_json, people):
    pose_points = [21,20,19,18,17]
    return getFACE(pose_json,pose_points, people)

def eyeR(pose_json, people):
    pose_points = [36,37,38,39,40,41,36]
    return getFACE(pose_json,pose_points, people)

def eyeL(pose_json, people):
    pose_points = [42,43,44,45,46,47,42]
    return getFACE(pose_json,pose_points, people)

def nose(pose_json, people):
    pose_points = [27,28,29,30]
    return getFACE(pose_json,pose_points, people)

def mouth(pose_json, people):
    pose_points = [48,59,58,57,56,55,54,53,52,51,50,49,48,60,67,66,65,64,63,62,61,60]
    return getFACE(pose_json,pose_points, people)



def prepareIdiotIA():

    WebStatus("Init IdiotIA...")

    # anim format (name, xpos, ypos, resize, currentframe, totalframe, count, speed)
    #               0     1     2      3           4           5         6      7
    # total frames is fetched from directory by lengthPOSE()
    
    anims[0] = [['idiotia1', xy_center[0], xy_center[1], 300,0,0,0,5]]
    anims[1] = [['idiotia1', xy_center[0], xy_center[1] + 50, 400,0,0,0,15]]
    anims[2] = [['idiotia1', xy_center[0], xy_center[1] + 50, 500,0,0,0,25]]
    anims[3] = [['idiotia1', xy_center[0], xy_center[1], 500,0,0,0,25]]

    for laseranims in anims:

        for anim in laseranims:
            anim[5] = lengthPOSE(anim[0])

            if debug > 0:
              print("anim :", 'poses/' + anim[0], "length :", anim[5], "frames")


# display the face animation describe in PoseDir
def IdiotIA():

  for laseranims in range(3):
    for anim in anims[laseranims]:
        PL = laseranims
        #print PL, anim

        dots = []

        # increase current frame [4] of speed [7] frames
        anim[4] += 1

        # compare to total frame [5]
        if anim[4] >= anim[5]:
            anim[4] = 0

        posename = 'poses/' + anim[0] + '/' + anim[0] +'-'+str("%05d"%anim[4])+'.json'
        posefile = open(posename , 'r') 
        posedatas = posefile.read()
        pose_json = json.loads(posedatas)

        # Face

        for people in range(len(pose_json['people'])):

            #lj3.rPolyLineOneColor(face(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(browL(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(browR(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(eyeR(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(eyeL(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(nose(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])  
            lj3.rPolyLineOneColor(mouth(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
        
        lj3.DrawPL(PL)
        time.sleep(0.02)


# many starfields
def prepareSTARFIELD():
    global star, stars0, stars1, stars2, starfieldcount, starspeed, displayedstars, displayedstars, num_stars, max_depth

    WebStatus("Init starfields...")
    stars0=[]
    stars1=[]
    stars2=[]
    #stars3=[]
    num_stars = 50
    max_depth = 20
    stars = []
    starfieldcount = 0
    displayedstars = 5
    starspeed = 0.05

    for i in range(num_stars):
        # A star is represented as a list with this format: [X,Y,Z]
        star = [randrange(-25,25), randrange(-25,25), randrange(1, max_depth)]
        stars0.append(star)
        star = [randrange(-25,25), randrange(-25,25), randrange(1, max_depth)]
        stars1.append(star)
        star = [randrange(-25,25), randrange(-25,25), randrange(1, max_depth)]
        stars2.append(star)

def Starfield(hori=0,verti=0):
    global star, stars0, stars1, stars2, starfieldcount, starspeed, displayedstars, displayedstars, num_stars, max_depth

    starfieldcount += 1
    #print starfieldcount
    starpoints = []
    #print displayedstars, 'stars displayed'

    # Increase number of 
    if displayedstars < num_stars and starfieldcount % 15 == 0:
        displayedstars += 1

    if displayedstars == num_stars and starfieldcount % 10 == 0:
        starspeed += 0.005

    #print starspeed

    for starnumber in range(0,displayedstars):
    
        # The Z component is decreased on each frame.
        stars0[starnumber][2] -= starspeed * 3
        stars1[starnumber][2] -= starspeed * 3
        stars2[starnumber][2] -= starspeed * 3

        # If the star has past the screen (I mean Z<=0) then we
        # reposition it far away from the screen (Z=max_depth)
        # with random X and Y coordinates.
        if stars0[starnumber][2] <= 0:
            stars0[starnumber][0] = randrange(-25,25)
            stars0[starnumber][1] = randrange(-25,25)
            stars0[starnumber][2] = max_depth

        if stars1[starnumber][2] <= 0:
            stars1[starnumber][0] = randrange(-25,25)
            stars1[starnumber][1] = randrange(-25,25)
            stars1[starnumber][2] = max_depth

        if stars2[starnumber][2] <= 0:
            stars2[starnumber][0] = randrange(-25,25)
            stars2[starnumber][1] = randrange(-25,25)
            stars2[starnumber][2] = max_depth


        # Convert the 3D coordinates to 2D using perspective projection.
        k0 = 128.0 / stars0[starnumber][2]
        k1 = 128.0 / stars1[starnumber][2]
        k2 = 128.0 / stars2[starnumber][2]

        # Move Starfield origin.
        # if stars xpos/ypos is same sign (i.e left stars xpos is <0) than (joystick or code) acceleration (hori and verti moves the star field origin)
        if np.sign(stars0[starnumber][0]) == np.sign(hori):
            x0 = int(stars0[starnumber][0] * k0 + xy_center[0] + (hori*600))
        else:
            x0 = int(stars0[starnumber][0] * k0 + xy_center[0] + (hori*500))

        if np.sign(stars0[starnumber][1]) == np.sign(verti):
            y0 = int(stars0[starnumber][1] * k0 + xy_center[1] + (verti*600))
        else:
            y0 = int(stars0[starnumber][1] * k0 + xy_center[1] + (verti*500))


        if np.sign(stars1[starnumber][0]) == np.sign(hori):
            x1 = int(stars1[starnumber][0] * k1 + xy_center[0] + (hori*600))
        else:
            x1 = int(stars1[starnumber][0] * k1 + xy_center[0] + (hori*300))

        if np.sign(stars1[starnumber][1]) == np.sign(verti):
            y1 = int(stars1[starnumber][1] * k1 + xy_center[1] + (verti*600))
        else:
            y1 = int(stars1[starnumber][1] * k1 + xy_center[1] + (verti*300))


        if np.sign(stars2[starnumber][0]) == np.sign(hori):
            x2 = int(stars2[starnumber][0] * k2 + xy_center[0] + (hori*600))
        else:
            x2 = int(stars2[starnumber][0] * k2 + xy_center[0] + (hori*300))

        if np.sign(stars2[starnumber][1]) == np.sign(verti):
            y2 = int(stars2[starnumber][1] * k2 + xy_center[1] + (verti*600))
        else:
            y2 = int(stars2[starnumber][1] * k2 + xy_center[1] + (verti*300))


        # Add star to pointlist PL 0
        if 0 <= x0 < screen_size[0] - 2 and 0 <= y0 < screen_size[1] - 2:
            lj3.PolyLineOneColor([(x0,y0),((x0+1),(y0+1))], c = white, PL = 0, closed = False)
        
        # Add star to pointlist PL 1
        if 0 <= x1 < screen_size[0] - 2 and 0 <= y1 < screen_size[1] - 2:
            lj3.PolyLineOneColor([(x1,y1),((x1+1),(y1+1))], c = white, PL = 1, closed = False)
          
        # Add star to pointlist PL 2
        if 0 <= x2 < screen_size[0] - 2 and 0 <= y2 < screen_size[1] - 2:
            lj3.PolyLineOneColor([(x2,y2),((x2+1),(y2+1))], c= white, PL = 2, closed = False)

    '''
    if starfieldcount < 200:
     
        if 0 <= x3 < screen_size[0] - 2 and 0 <= y3 < screen_size[1] - 2:
            fwork.PolyLineOneColor([(x3,y3),((x3+2),(y3+2))], c=colorify.rgb2hex([255,255,255]), PL = 3, closed = False)
    '''            


    lj3.Text(message, white, PL = 3, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
    lj3.DrawPL(0)
    lj3.DrawPL(1)
    lj3.DrawPL(2)
    lj3.DrawPL(3)


def OSCidiotia(address,value):
        print("idiotia",address,value)



def OSCfield(address, value):
    print("Pose bank field got", address, "with value", value)


def OSCljclient(value):
    print("Pose bank got /pose/ljclient with value", value)
    ljclient = value
    lj3.LjClient(ljclient)


def OSCpl(value):

    print("Pose bank got /pose/pl with value", value)
    lj3.WebStatus("Pose bank to pl "+ str(value))
    lj3.LjPl(value)


# Starfield, idiotia
def OSCrun(value):
    # Will receive message address, and message data flattened in s, x, y
    print("Pose bank got /run with value", value)
    doit = value

# /quit
def OSCquit():

    WebStatus("Pose bank stopping")
    print("Stopping OSC...")
    lj3.OSCstop()
    sys.exit()

def WebStatus(message):
    lj3.SendLJ("/status",message)



print('Loading Pose bank...')

WebStatus("Loading Pose bank...")

# OSC Server callbacks
print("Starting OSC at 127.0.0.1 port",OSCinPort,"...")
osc_startup()
osc_udp_server("127.0.0.1", OSCinPort, "InPort")

osc_method("/pose/run*", OSCrun)
osc_method("/pose/ping*", lj3.OSCping)
osc_method("/pose/ljclient", OSCljclient)
osc_method("/pose/ljpl", OSCpl)
osc_method("/quit", OSCquit)
osc_method("/pose/idiotia*", OSCidiotia, argscheme=OSCARG_ADDRESS + OSCARG_DATA)
osc_method("/pose/field*", OSCfield, argscheme=OSCARG_ADDRESS + OSCARG_DATA)

anims =[[],[],[],[]]
color = lj3.rgb2int(255,255,255)






prepareIdiotIA()
#prepareSTARFIELD()


#doit = Starfield
doit = IdiotIA

white = lj3.rgb2int(255,255,255)
red = lj3.rgb2int(255,0,0)
blue = lj3.rgb2int(0,0,255)
green = lj3.rgb2int(0,255,0)

WebStatus("Pose bank running.")
print("Pose bank running")

def Run():
    
    try:
        while 1:
            #Starfield(hori=0,verti=0)
            doit()

    except KeyboardInterrupt:
        pass

    # Gently stop on CTRL C

    finally:

        WebStatus("Pose bank Exit")
        print("Stopping OSC...")
        lj3.OSCstop()

    print ("Pose bank Stopped.")

Run()
