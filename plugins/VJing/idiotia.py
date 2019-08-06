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
import sys
import ast
import os

import time,traceback


ljpath = r'%s' % os.getcwd().replace('\\','/')

# import from shell

sys.path.append(ljpath +'/../../libs/')
print(ljpath +'/../../libs/')
#import from LJ
sys.path.append(ljpath +'/libs/')
print (ljpath +'/libs/')


is_py2 = sys.version[0] == '2'
if is_py2:
    from OSC import OSCServer, OSCClient, OSCMessage
else:
    from OSC3 import OSCServer, OSCClient, OSCMessage

import lj23 as lj3

'''
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
#from osc4py3 import oscmethod as osm
from osc4py3.oscmethod import * 
'''

import argparse

# 0.25 : each frame will be repeated 4 times.
animspeed = 0.1

screen_size = [700,700]
xy_center = [screen_size[0]/2,screen_size[1]/2]

message = "TEAMLASER"
OSCinPort = 8011

ljclient = 0

#liveDisplay = [False,False,False,False]

liveDisplay = [True, True, True, True]
#fieldsDisplay = [True,True,True,True]
idiotiaDisplay = [False, False, False, False]
fieldsDisplay = [False, False, False, False]



'''
fieldsDisplay = [False,False,True,True]
'''

#idiotiaDisplay = [True,True,False,False]

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
    LaserNumber = 1


r = lj3.Config(redisIP,ljclient,"pose")


#
# OSC
#

oscserver = OSCServer( (myIP, OSCinPort) )
oscserver.timeout = 0
#oscrun = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
    self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)



def hex2rgb(hexcode):
    return tuple(map(ord,hexcode[1:].decode('hex')))


def rgb2hex(rgb):
    return int('0x%02x%02x%02x' % tuple(rgb),0)


# IdiotIA
import json
#CurrentPose = 1

# Get frame number for pose path describe in PoseDir 
def lengthPOSE(pose_dir):

    if debug > 0:
        print("Checking directory",'plugins/VJing/poses/' + pose_dir)
    if os.path.exists('plugins/VJing/poses/' + pose_dir):
        
        numfiles = sum(1 for f in os.listdir('plugins/VJing/poses/' + pose_dir) if os.path.isfile(os.path.join('plugins/VJing/poses/' + pose_dir + '/', f)) and f[0] != '.')
        if debug > 0:
            print(numfiles, 'frames')
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
              print('plugins/VJing/poses/' + anim[0], "length :", anim[5], "frames")

    print("Current IdiotIA anim is",anims[currentIdiotia][0],"("+str(currentIdiotia)+")")


'''
pose_keypoints_2d
face_keypoints_2d
hand_left_keypoints_2d
hand_right_keypoints_2d
pose_keypoints_3d
face_keypoints_3d
hand_left_keypoints_3d
hand_right_keypoints_3d

"/0/face_keypoints_2d"
"[-0.0946419, -0.521328, 0.675269, -0.0883931, -0.413923, 0.69358, -0.0758954, -0.302815, 0.73599, -0.059232, -0.191707, 0.640398, -0.0384026, -0.0917102, 0.683398, -0.00507569, -0.00652742, 0.643006, 0.0428318, 0.0601374, 0.558626, 0.0844904, 0.108284, 0.576597, 0.142813, 0.108284, 0.621916, 0.178223, 0.0749518, 0.546389, 0.207384, 0.0193979, 0.556877, 0.22613, -0.0361562, 0.660514, 0.244876, -0.102821, 0.713871, 0.267789, -0.1843, 0.706604, 0.290701, -0.265779, 0.680418, 0.307364, -0.347258, 0.617497, 0.31153, -0.428738, 0.53877, -0.0446514, -0.547253, 0.784288, -0.00715858, -0.569474, 0.873856, 0.0303342, -0.558364, 0.835336, 0.0740758, -0.543549, 0.827985, 0.111569, -0.525031, 0.809191, 0.213632, -0.543549, 0.819012, 0.242794, -0.569474, 0.884373, 0.265706, -0.5954, 0.842317, 0.292784, -0.613918, 0.804365, 0.313613, -0.625028, 0.740405, 0.163642, -0.443552, 0.805348, 0.169891, -0.362073, 0.837128, 0.169891, -0.280594, 0.839031, 0.174057, -0.213929, 0.68711, 0.111569, -0.162078, 0.725528, 0.134481, -0.154671, 0.837339, 0.159476, -0.150968, 0.887387, 0.178223, -0.158375, 0.835752, 0.196969, -0.180597, 0.698174, 0.00950491, -0.432441, 0.864517, 0.0345001, -0.458366, 0.859197, 0.0636612, -0.46207, 0.867471, 0.0907393, -0.432441, 0.852409, 0.0636612, -0.417627, 0.876186, 0.0324172, -0.413923, 0.834265, 0.21155, -0.454663, 0.875569, 0.232379, -0.491699, 0.816674, 0.26154, -0.50281, 0.878064, 0.282369, -0.476884, 0.839634, 0.263623, -0.450959, 0.912212, 0.24071, -0.450959, 0.896937, 0.0719929, -0.047267, 0.761505, 0.101154, -0.065785, 0.864081, 0.130315, -0.0694886, 0.910774, 0.159476, -0.065785, 0.895222, 0.17614, -0.0731922, 0.846551, 0.194886, -0.0731922, 0.74389, 0.209467, -0.0731922, 0.573107, 0.194886, -0.0213418, 0.677465, 0.17614, 0.0156941, 0.755373, 0.15531, 0.0231014, 0.765641, 0.124066, 0.0231014, 0.863117, 0.0928223, -0.00282377, 0.823042, 0.0928223, -0.0398598, 0.743914, 0.128232, -0.0361562, 0.932259, 0.157393, -0.0361562, 0.877732, 0.17614, -0.0398598, 0.853163, 0.196969, -0.0620813, 0.645926, 0.17614, -0.0398598, 0.80738, 0.157393, -0.0324526, 0.872388, 0.128232, -0.0361562, 0.924673, 0.0511636, -0.450959, 0.801577, 0.244876, -0.480588, 0.915322]"

"/peopleCount"
"2"
'''

def bodyREDIS(people):

    dots = []
    pose = []
    redispose = []

    pose_points = [10,9,8,1,11,12,13]
    print ("people body", people)
    
    print ("/"+str(people)+"/pose_keypoints_2d")
    #pose = np.array(ast.literal_eval(r.get("/"+str(people)+"/pose_keypoints_2d")))
    redispose = r.get("/"+str(people)+"/pose_keypoints_2d")
    #print ("redispose",redispose)
    poseast = ast.literal_eval(redispose)
    #print ("poseast",poseast)
    #print (poseast[0])
    pose = np.array(poseast)
    #print (np.array((ast.literal_eval(strg))))
    #print pose
    #print(pose[0], pose[1])
    #print("len pose", len(pose))
    '''
    for dot in range(len(pose)/3):
        #print dot
        dots.append(((pose[dot * 3], pose[(dot * 3)+1])))
        #print((pose[dot * 3], pose[(dot * 3)+1]))
    '''
    for dot in range(len(pose_points)):
        bodypoint =  pose_points[dot]
        if pose[bodypoint * 3] != -1 and  pose[(bodypoint * 3)+1] != -1:

            dots.append(((pose[bodypoint * 3], pose[(bodypoint * 3)+1])))
        #print((pose[dot * 3], pose[(dot * 3)+1]))
        #print "body point ", pose_points[dot],dot, (pose[bodypoint * 3], pose[(bodypoint * 3)+1])
    print dots
    return dots

# display the Realtime open pose face according to flag.
def LivePose():


    laser = 0
    # Old style : if display flag is True for given laser, send the face points.
    # New style : should send the people points in a PL, then use the PL's dest object to describe 
    # what to do with it
    
    if liveDisplay[0]:
        peoplenumber = int(r.get("/peopleCount"))
        print peoplenumber
        for currentnumber in range(peoplenumber):
            PL = 0
            #print PL, anim
            # Draw Pose
            
            x_offset = 26 * (- (0.9*peoplenumber) + 3*currentnumber)
            for people in range(peoplenumber):

                print("people", people)
                x_offset = 26 * (- (0.9*peoplenumber) + 3*currentnumber)
                print x_offset
                lj3.rPolyLineOneColor(bodyREDIS(people), c= white, PL = PL, closed = False, xpos = xy_center[0]+ x_offset, ypos = xy_center[1], resize = 250)

            lj3.DrawPL(PL)



# get relative (-1 0 1) body position points. a position -1, -1 means doesn't exist
def getBODY(pose_json,pose_points, people):

    dots = []
    for dot in pose_points:
        #print pose_points
        if len(pose_json['people'][people]['pose_keypoints_2d']) != 0:
            #print "people 0"
            if pose_json['people'][people]['pose_keypoints_2d'][dot * 3] != -1 and  pose_json['people'][people]['pose_keypoints_2d'][(dot * 3)+1] != -1:
                dots.append((pose_json['people'][people]['pose_keypoints_2d'][dot * 3], pose_json['people'][people]['pose_keypoints_2d'][(dot * 3)+1]))


    return dots

# get absolute face position points 
def getFACE(pose_json,pose_points, people):

    dots = []
    for dot in pose_points:

        if len(pose_json['people'][people]['face_keypoints_2d']) != 0:
            #print "people 0"
            if pose_json['people'][people]['face_keypoints_2d'][dot * 3] != -1 and  pose_json['people'][people]['face_keypoints_2d'][(dot * 3)+1] != -1:
                dots.append((pose_json['people'][people]['face_keypoints_2d'][dot * 3], pose_json['people'][people]['face_keypoints_2d'][(dot * 3)+1]))

    return dots



# Body parts
def bodyCOCO(pose_json, people):
    pose_points = [10,9,8,1,11,12,13]
    return getBODY(pose_json,pose_points, people)

def armCOCO(pose_json, people):
    pose_points = [7,6,5,1,2,3,4]
    return getBODY(pose_json,pose_points, people)

def headCOCO(pose_json, people):
    pose_points = [1,0]
    return getBODY(pose_json,pose_points, people)


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
        dots = []

        # increase current frame [4] of speed [7] frames
        # print(anim[4],anim[7],anim[4]+anim[7])
        # print("frame", anim[4])
        anim[4] = anim[4]+anim[7]
        # print("animspeed",anim[7], "newframe", anim[4], "maximum frame", anim[5] )
        # compare to total frame [5]
        if anim[4] >= anim[5]:
            anim[4] = 0

        posename = 'plugins/VJing/poses/' + anim[0] + '/' + anim[0] +'-'+str("%05d"%int(anim[4]))+'.json'
        # print(posename)
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
    print ("laser", laser)

    # if display flag is True, send the face points.
    if liveDisplay[laser]:

        PL = laser
        #print PL, anim
        dots = []
        pose_json = json.loads(posedatas)

        # Draw Face

        for people in range(len(pose_json['people'])):

            r.get(n)
            lj3.rPolyLineOneColor(bodyCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(armCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(headCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color),  PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])

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


    # if display flag is True, send the face points.
    if liveDisplay[laser]:
        pass



# /pose/idiotia/lasernumber 1 
def OSCidiotia(path, tags, args, source):
    
    print("pose idiotia got",path, args)
    laser = int(args[0])
    value = int(args[1])
    
    
    if value == 1:
    
        print("switch on idiotia for laser", laser, value)
        idiotiaDisplay[laser] = True
        liveDisplay[laser] = False
        fieldsDisplay[laser] = False
        #print(idiotiaDisplay,liveDisplay,fieldsDisplay)
    
    else:
    
        idiotiaDisplay[laser] = False
        print(idiotiaDisplay,liveDisplay,fieldsDisplay)

    UpdatePoseUI()



# /pose/anim
def OSCanim(path, tags, args, source):
    
    print("pose anim got",path, args)
    anim = int(args[0])
    state = int(args[1])
    
    #print(anim, state)

    if state == 1:
        print("/pose/anim switch to",anim)
        currentIdiotia = anim
        UpdatePoseUI()
        WebStatus("Ruuning "+ anims[currentIdiotia][0]+"...")


# /pose/live/lasernumber value
def OSClive(path, tags, args, source):
    
    print("pose live got",path, args)
    laser = int(args[0])
    value = int(args[1])
    
    
    if value == "1":
        print("live for laser", laser)
        idiotiaDisplay[value] = False
        liveDisplay[value] = True
        fieldsDisplay[value] = False
        UpdatePoseUI()

# /pose/field/lasernumber value
def OSCfield(path, tags, args, source):

    print("pose field got",path, args)
    laser = int(args[0])
    value = int(args[1])
    
    
    if value == "1":
        print("field for laser", laser)
        idiotiaDisplay[value] = False
        liveDisplay[value] = False
        fieldsDisplay[value] = True
        UpdatePoseUI()


# /pose/ljclient
def OSCljclient(path, tags, args, source):

    print("pose got /viewgen/ljclient with value", args[0])
    lj.WebStatus("viewgen to virtual "+ str(args[0]))
    ljclient = args[0]
    lj.LjClient(ljclient)




'''
# Starfield, idiotia
def OSCrun(value):
    # Will receive message address, and message data flattened in s, x, y
    print("Pose bank got /run with value", value)
    doit = value
'''
'''
# /quit
def OSCquit():

    WebStatus("Pose bank stopping")
    print("Stopping OSC...")
    lj3.OSCstop()
    sys.exit()
'''

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

oscserver.addMsgHandler("/pose/ljclient", OSCljclient)
oscserver.addMsgHandler("/pose/idiotia", OSCidiotia)
oscserver.addMsgHandler("/pose/field", OSCfield)
oscserver.addMsgHandler("/pose/live", OSClive)
oscserver.addMsgHandler("/pose/anim", OSCanim)
# Add OSC generic plugins commands : 'default", /ping, /quit, /pluginame/obj, /pluginame/var, /pluginame/adddest, /pluginame/deldest
lj3.addOSCdefaults(oscserver)

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

WebStatus("Pose "+ anims[currentIdiotia][0]+".")
#WebStatus("Pose bank running.")
#print("Pose bank running")
print("Pose "+ anims[currentIdiotia][0]+" ready on " + str(LaserNumber) +" lasers.")

def Run():
    
    try:
        while lj3.oscrun:

            # If you want an idea 
            # t0 = time.time()
            lj3.OSCframe()
            #Starfield(hori=0,verti=0)
            #IdiotIA()
            LivePose()
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
