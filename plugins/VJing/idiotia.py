#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
LJ v0.8.1

IdiotIA for THSF 10

Include IdiotIA and Starfields

 /pose/ljclient

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
import sys,time,traceback
import os

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
#from osc4py3 import oscmethod as osm
from osc4py3.oscmethod import * 
import argparse

# 0.25 : each frame will be repeated 4 times.
animspeed = 0.25

screen_size = [700,700]
xy_center = [screen_size[0]/2,screen_size[1]/2]

message = "LO"
OSCinPort = 8011

ljclient = 0

idiotiaDisplay = [True,True,False,False]
#idiotiaDisplay = [False,False,False,False]
liveDisplay = [False,False,False,False]

fieldsDisplay = [False,False,True,True]
#fieldsDisplay = [True,True,True,True]
currentIdiotia = 0

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Pose bank for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)
argsparser.add_argument("-a","--anim",help="IdiotIA anim (0 by default)",type=int)
argsparser.add_argument("-L","--Lasers",help="Number of lasers connected (4 by default).",type=int)

args = argsparser.parse_args()


if args.verbose:
    debug = args.verbose
else:
    debug = 0

if args.client:
    ljclient = args.client
else:
    ljclient = 0

if args.anim:
    currentIdiotia = args.anim
else:
    currentIdiotia = 0

# Redis Computer IP
if args.redisIP  != None:
    redisIP  = args.redisIP
else:
    redisIP = '127.0.0.1'

# myIP
if args.myIP  != None:
    myIP  = args.myIP
else:
    myIP = '127.0.0.1'

# Lasers = number of laser connected
if args.Lasers  != None:
    LaserNumber = args.Lasers
else:
    LaserNumber = 4


lj3.Config(redisIP,ljclient)



def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))


def rgb2hex(rgb):
    return int('0x%02x%02x%02x' % tuple(rgb),0)


# IdiotIA
import json
#CurrentPose = 1

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


def prepareIdiotIA(currentAnim):
    
    WebStatus("Checking anims...")
    print()
    print("Reading available IdiotIA anims...")
    # anim format (name, xpos, ypos, resize, currentframe, totalframe, count, speed)
    #               0     1     2      3           4           5         6      7
    # total frames is fetched from directory by lengthPOSE()
    
    anims[0] = ['boredhh' , xy_center[0] - 100, xy_center[1] + 30, 550, 0, 0, 0, animspeed]
    anims[1] = ['belka4'  , xy_center[0] - 70, xy_center[1] + 380, 680, 0, 0, 0, animspeed]
    anims[2] = ['belka3' , xy_center[0] - 100, xy_center[1] + 360, 700, 0, 0, 0, animspeed]
    anims[3] = ['hhhead' , xy_center[0] - 100, xy_center[1] + 300, 600, 0, 0, 0, animspeed]
    anims[4] = ['hhhead2', xy_center[0] - 100, xy_center[1] + 300, 600, 0, 0, 0, animspeed]
    anims[5] = ['hhhead4', xy_center[0] - 100, xy_center[1] + 280, 600, 0, 0, 0, animspeed]
    anims[6] = ['hhred'  , xy_center[0] - 250, xy_center[1] + 220, 550, 0, 0, 0, animspeed]
    anims[7] = ['hhred2' , xy_center[0] - 200, xy_center[1] + 200, 550, 0, 0, 0, animspeed]
    anims[8] = ['lady1'  , xy_center[0] - 100, xy_center[1] + 300, 600, 0, 0, 0, animspeed]
    anims[9] = ['lady1'  , xy_center[0] - 100, xy_center[1] + 280, 600, 0, 0, 0, animspeed]
    anims[10] = ['lady2' , xy_center[0] - 100, xy_center[1] + 280, 600, 0, 0, 0, animspeed]
    anims[11] = ['lady3' , xy_center[0] - 100, xy_center[1] + 300, 600, 0, 0, 0, animspeed]
    anims[12] = ['lady4' , xy_center[0] - 100, xy_center[1] + 300, 600, 0, 0, 0, animspeed]
    anims[13] = ['mila6' , xy_center[0] - 100, xy_center[1] + 280, 600, 0, 0, 0, animspeed]
    anims[14] = ['mila5' , xy_center[0] - 100, xy_center[1] + 280, 600, 0, 0, 0, animspeed]
    anims[15] = ['idiotia1', xy_center[0] - 100, xy_center[1] + 300, 600, 0, 0, 0, animspeed]
    anims[16] = ['idiotia1', xy_center[0] - 100, xy_center[1] + 300, 600, 0, 0, 0, animspeed]
    anims[17] = ['belka4', xy_center[0] - 100, xy_center[1] + 280, 600, 0, 0, 0, animspeed]
    anims[18] = ['belka3', xy_center[0] - 100, xy_center[1] + 280, 600, 0, 0, 0, animspeed]
    
    #for laseranims in anims:
        
    for anim in anims:
            #print(anim)
            anim[5] = lengthPOSE(anim[0])
            WebStatus("Checking "+ anim[0] +"...")
            if debug > 0:
              print('poses/' + anim[0], "length :", anim[5], "frames")

    print("Current IdiotIA anim is",anims[currentIdiotia][0],"("+str(currentIdiotia)+")")


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

def pupR(pose_json, people):
    pose_points = [68,68]
    print(getFACE(pose_json,pose_points, people))
    return getFACE(pose_json,pose_points, people)

def pupL(pose_json, people):
    pose_points = [69,69]
    return getFACE(pose_json,pose_points, people)


def nose(pose_json, people):
    pose_points = [27,28,29,30]
    return getFACE(pose_json,pose_points, people)

def mouth(pose_json, people):
    pose_points = [48,59,58,57,56,55,54,53,52,51,50,49,48,60,67,66,65,64,63,62,61,60]
    return getFACE(pose_json,pose_points, people)




# display the currentIdiotia animation on all lasers according to display flag
def IdiotIA():

  # All laser loop
  for laser in range(LaserNumber):
    # for anim in anims[laseranims]:

    # if display flag is True, send the face points.
    if idiotiaDisplay[laser]:

        anim = anims[currentIdiotia]
        #print(anim)

        PL = laser
        #print PL, anim

        dots = []

        # increase current frame [4] of speed [7] frames
        #print(anim[4],anim[7],anim[4]+anim[7])

        anim[4] = anim[4]+anim[7]

        # compare to total frame [5]
        if anim[4] >= anim[5]:
            anim[4] = 0

        posename = 'poses/' + anim[0] + '/' + anim[0] +'-'+str("%05d"%int(anim[4]))+'.json'
        posefile = open(posename , 'r') 
        posedatas = posefile.read()
        pose_json = json.loads(posedatas)
        #WebStatus("Frame : "+str("%05d"%int(anim[4])))

        # Draw Face

        for people in range(len(pose_json['people'])):

            #lj3.rPolyLineOneColor(face(pose_json, people), c = white, PL = laser closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(browL(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(browR(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(eyeR(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            #lj3.rPolyLineOneColor(pupR(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(eyeL(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            #lj3.rPolyLineOneColor(pupL(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(nose(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])  
            lj3.rPolyLineOneColor(mouth(pose_json, people), c = white, PL = laser, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
        
        lj3.DrawPL(PL)


# Init Starfields
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


# Todo : Currently compute all starfields even if field display flag is False. 

def Starfield(hori=0,verti=0):
    global star, stars0, stars1, stars2, starfieldcount, starspeed, displayedstars, displayedstars, num_stars, max_depth

    starfieldcount += 1
    #print starfieldcount
    starpoints = []
    #print displayedstars, 'stars displayed'

    # Increase number of 
    if displayedstars < num_stars and starfieldcount % 15 == 0:
        displayedstars += 1

    #if displayedstars == num_stars and starfieldcount % 10 == 0:
    #    starspeed += 0.005

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


        # Add star to pointlist PL 0 if field display flag is true
        if fieldsDisplay[0] and 0 <= x0 < screen_size[0] - 2 and 0 <= y0 < screen_size[1] - 2:
            lj3.PolyLineOneColor([(x0,y0),((x0+1),(y0+1))], c = white, PL = 0, closed = False)
        
        # Add star to pointlist PL 1 if field display flag is true
        if fieldsDisplay[1] and 0 <= x1 < screen_size[0] - 2 and 0 <= y1 < screen_size[1] - 2:
            lj3.PolyLineOneColor([(x1,y1),((x1+1),(y1+1))], c = white, PL = 1, closed = False)
          
        # Add star to pointlist PL 2 if field display flag is true
        if fieldsDisplay[2] and 0 <= x2 < screen_size[0] - 2 and 0 <= y2 < screen_size[1] - 2:
            lj3.PolyLineOneColor([(x2,y2),((x2+1),(y2+1))], c= white, PL = 2, closed = False)

    '''
    if starfieldcount < 200:
     
        if 0 <= x3 < screen_size[0] - 2 and 0 <= y3 < screen_size[1] - 2:
            fwork.PolyLineOneColor([(x3,y3),((x3+2),(y3+2))], c=colorify.rgb2hex([255,255,255]), PL = 3, closed = False)
    '''            

    # Laser 3 Display a word.
    if fieldsDisplay[3]:
        lj3.Text(message, white, PL = 3, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)



    # If field display is True for each laser
    for laser in range(LaserNumber):
        
        # Actually send the field point list.
        if fieldsDisplay[laser]:
            lj3.DrawPL(laser)


# display the Realtime open pose face according to flag.
def LiveFace():

  # All laser loop
  for laser in range(LaserNumber):
    # for anim in anims[laseranims]:

    # if display flag is True, send the face points.
    if liveDisplay[laser]:
        pass



# /pose/idiotia/lasernumber 1 
def OSCidiotia(address, value):
    
    print("pose idiotia got ",address,value)
    laser = int(address[14:])
    print("laser", laser, value)
    
    if value == "1" or value == 1:
    
        idiotiaDisplay[laser] = True
        liveDisplay[laser] = False
        fieldsDisplay[laser] = False
        print(idiotiaDisplay,liveDisplay,fieldsDisplay)
    
    else:
    
        idiotiaDisplay[laser] = False
        print(idiotiaDisplay,liveDisplay,fieldsDisplay)

    UpdatePoseUI()

# /pose/anim/animnumber 1
def OSCanim(address, value):
    global currentIdiotia
    
    print("pose anim got :", address, type(value), value)
    anim = int(address[11:])
    print("anim", anim)

    if value == "1" or value == 1:
        currentIdiotia = anim
        UpdatePoseUI()
        WebStatus("Running "+ anims[currentIdiotia][0]+"...")


# /pose/live/lasernumber value
def OSClive(address, value):
    
    print("live",address,value)
    laser = int(address[11:])
    #print("laser", laser, value)
    
    if value == "1" or value == 1:
        idiotiaDisplay[laser] = False
        liveDisplay[laser] = True
        fieldsDisplay[laser] = False
        UpdatePoseUI()

# /pose/field/lasernumber value
def OSCfield(address, value):

    print("Pose field got", address, "with value", type(value), value)
    laser = int(address[12:])
    #print("laser", laser, value)
    
    if value == "1" or value == 1:
        print("field",laser,"true")
        idiotiaDisplay[laser] = False
        liveDisplay[laser] = False
        fieldsDisplay[laser] = True
        UpdatePoseUI()


# /pose/ljclient
def OSCljclient(value):
    print("Pose bank got /pose/ljclient with value", value)
    ljclient = value
    lj3.LjClient(ljclient)


# /pose/ping value
def OSCping(value):
    lj3.OSCping("pose")

'''
# Starfield, idiotia
def OSCrun(value):
    # Will receive message address, and message data flattened in s, x, y
    print("Pose bank got /run with value", value)
    doit = value
'''

# /quit
def OSCquit():

    WebStatus("Pose bank stopping")
    print("Stopping OSC...")
    lj3.OSCstop()
    sys.exit()

def WebStatus(message):
    lj3.SendLJ("/status",message)


# Update Pose webUI
def UpdatePoseUI():

    WebStatus("Updating Pose UI...")
    for laser in range(LaserNumber):

        if idiotiaDisplay[laser]:
            lj3.SendLJ("/pose/idiotia/" + str(laser) + " 1")
        else:
            lj3.SendLJ("/pose/idiotia/" + str(laser) + " 0")

        if liveDisplay[laser]:
            lj3.SendLJ("/pose/live/" + str(laser) + " 1")
        else:
            lj3.SendLJ("/pose/live/" + str(laser) + " 0")

        if fieldsDisplay[laser]:
            lj3.SendLJ("/pose/field/" + str(laser) + " 1")
        else:
            lj3.SendLJ("/pose/field/" + str(laser) + " 0")


    for anim in range(19):
        if anim == currentIdiotia:
            lj3.SendLJ("/pose/anim/" + str(anim) + " 1")
        else:
            lj3.SendLJ("/pose/anim/" + str(anim) + " 0")



print('Loading Pose bank...')
WebStatus("Loading Pose bank...")

# OSC Server callbacks
print("Starting OSC server at", myIP, ":", OSCinPort, "...")
osc_startup()
osc_udp_server(myIP, OSCinPort, "InPort")

#osc_method("/pose/run*", OSCrun)
osc_method("/ping*", OSCping)
osc_method("/pose/ljclient", OSCljclient)
osc_method("/quit", OSCquit)
osc_method("/pose/idiotia/*", OSCidiotia, argscheme=OSCARG_ADDRESS + OSCARG_DATAUNPACK)
osc_method("/pose/field/*", OSCfield,argscheme=OSCARG_ADDRESS + OSCARG_DATAUNPACK)
osc_method("/pose/live/*", OSClive, argscheme=OSCARG_ADDRESS + OSCARG_DATAUNPACK)
osc_method("/pose/anim/*", OSCanim, argscheme=OSCARG_ADDRESS + OSCARG_DATAUNPACK)


anims =[[]]*19


prepareIdiotIA(0)
prepareSTARFIELD()

#doit = Starfield
#doit = IdiotIA

white = lj3.rgb2int(255,255,255)
red = lj3.rgb2int(255,0,0)
blue = lj3.rgb2int(0,0,255)
green = lj3.rgb2int(0,255,0)

print("Updating Pose UI...")
UpdatePoseUI()

WebStatus("Running "+ anims[currentIdiotia][0]+"...")
#WebStatus("Pose bank running.")
#print("Pose bank running")
print("Running "+ anims[currentIdiotia][0]+" on " + str(LaserNumber) +" lasers.")

def Run():
    
    try:
        while 1:

            lj3.OSCframe()
            # If you want an idea 
            # t0 = time.time()
            Starfield(hori=0,verti=0)
            IdiotIA()
            #LiveFace()
            time.sleep(0.002)
            #t1 = time.time()
            # looptime = t1 - t0
            # 25 frames/sec -> 1 frame is 0.04 sec long
            # if looptime is 0.01 sec
            # 0.04/0.01 = 4 loops with the same anim
            # so speedanim is 1 / 4 = 0.25
            # speedanim = 1 / (0.04 / looptime)


            #print("Took %f" % (t1 - t0, ))

    #except KeyboardInterrupt:
    #    pass

    except Exception:
        traceback.print_exc()

    # Gently stop on CTRL C

    finally:

        WebStatus("Pose bank Exit")
        print("Stopping OSC...")
        lj3.OSCstop()

    print ("Pose bank Stopped.")

Run()
