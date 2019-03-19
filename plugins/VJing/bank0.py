#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
VJing Bank 0

was Franken for compo laser at coockie 2018 demoparty

0 : Starfields
1 : generic pose animations
2 : Faces
3 : Dancers
4 : IdiotIA

LICENCE : CC
Sam Neurohack, Loloster, 

'''


import math
#import gstt
#from globalVars import *
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

#f_sine = 0


screen_size = [400,400]
xy_center = [screen_size[0]/2,screen_size[1]/2]

message = "Hello"
OSCinPort = 8010

redisIP = '127.0.0.1'
ljclient = 0

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="VJ Bank 0 for LJ")
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



# Curve 0 many starfields
def prepareSTARFIELD():
    global star, stars0, stars1, stars2, starfieldcount, starspeed, displayedstars, displayedstars, num_stars, max_depth

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

    # Move starfield according to joypads. Not used in the demo
    '''
    # Tflight joystick : 
    # y axis 1 top -1 bottom 1
    # x axis 0 left -1 right 1
    # Main fire button 5
    # hat (x,y)  x -1 left x 1 right y -1 bottom y 1 top 
    # speed axis 3 backward 1 forward -1 

    if Nbpads > 0:
        # Move center on X axis according to pad
        if pad1.get_axis(0)<-0.1 or pad1.get_axis(0)>0.1:
            hori = pad1.get_axis(0)
            #print hori
        # Move center on Y axis according to pad
        if pad1.get_axis(1)<-0.1 or pad1.get_axis(1)>0.1:
            verti= pad1.get_axis(1)
            #print verti
    '''

    #print displayedstars, 'stars displayed'

    # Increase number of 
    if displayedstars < num_stars and starfieldcount % 15 == 0:
        displayedstars += 1

    if displayedstars == num_stars and starfieldcount % 10 == 0:
        starspeed += 0.005

    #if Nbpads > 0:
    #   starspeed = (1-pad1.get_axis(3))

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
            x0 = int(stars0[starnumber][0] * k0 + xy_center[0] + (hori*300))

        if np.sign(stars0[starnumber][1]) == np.sign(verti):
            y0 = int(stars0[starnumber][1] * k0 + xy_center[1] + (verti*600))
        else:
            y0 = int(stars0[starnumber][1] * k0 + xy_center[1] + (verti*300))


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
            #f.LineTo((x,y), 0x80000000)
            lj3.PolyLineOneColor([(x0,y0),((x0+1),(y0+1))],  c = rgb2hex([255,255,255]),    PL = 0, closed = False)
            #fwork.PolyLineOneColor([(x0,y0),((x0+1),(y0+1))], c=rgb2hex([255,255,255]), PL = 0, closed = False)
        
        # Add star to pointlist PL 1
        if 0 <= x1 < screen_size[0] - 2 and 0 <= y1 < screen_size[1] - 2:
            lj3.PolyLineOneColor([(x1,y1),((x1+1),(y1+1))],  c = rgb2hex([255,255,255]),    PL = 0, closed = False)

            #fwork.PolyLineOneColor([(x1,y1),((x1+1),(y1+1))], c=rgb2hex([255,255,255]), PL = 1, closed = False)
          
        # Add star to pointlist PL 2
        #if 0 <= x2 < screen_size[0] - 2 and 0 <= y2 < screen_size[1] - 2:
        #    fwork.PolyLineOneColor([(x2,y2),((x2+1),(y2+1))], c=colorify.rgb2hex([255,255,255]), PL = 2, closed = False)
        #    #f.PolyLineOneColor([(x,y),((x+2),(y+2))], COLOR_WHITE)

    '''
    if starfieldcount < 200:
     
        if 0 <= x3 < screen_size[0] - 2 and 0 <= y3 < screen_size[1] - 2:
            fwork.PolyLineOneColor([(x3,y3),((x3+2),(y3+2))], c=colorify.rgb2hex([255,255,255]), PL = 3, closed = False)
    '''            


    lj3.Text(message, color, PL = 2, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
    lj3.DrawPL(0)
    lj3.DrawPL(1)
    lj3.DrawPL(2)
    #lj3.DrawPL(3)


# Curve 1 : generic pose animations
import json
CurrentPose = 1

# get absolute body position points
def getCOCO(pose_json,pose_points, people):
    
    dots = []
    for dot in pose_points:
        if len(pose_json['part_candidates'][people][str(dot)]) != 0:
            dots.append((pose_json['part_candidates'][people][str(dot)][0], pose_json['part_candidates'][people][str(dot)][1]))
    return dots


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

def nose(pose_json, people):
    pose_points = [27,28,29,30]
    return getFACE(pose_json,pose_points, people)

def mouth(pose_json, people):
    pose_points = [48,59,58,57,56,55,54,53,52,51,50,49,48,60,67,66,65,64,63,62,61,60]
    return getFACE(pose_json,pose_points, people)

import os 


# Get frame number for pose path describe in PoseDir 
def lengthPOSE(pose_dir):

    if debug > 0:
      print("Check directory",'poses/' + pose_dir)
    if os.path.exists('poses/' + pose_dir):
      numfiles = sum(1 for f in os.listdir('poses/' + pose_dir) if os.path.isfile(os.path.join('poses/' + pose_dir + '/', f)) and f[0] != '.')
      if debug > 0:
        print(numfiles,"images")
      return numfiles
    else:
      if debug > 0:
        print("but it doesn't even exist!")
      return 0

def preparePOSE():
    global anims0, anims1, anims2

    # anim format (name, xpos,ypos, resize, currentframe, totalframe, count, speed)
    # total frames is fetched from directory file count
    
    anims1 = [['sky',50,100,300,0,0,0,1],['2dancer1', 400,100, 300,0,0,0,1],['1dancer', 400,100, 300,0,0,0,1],['window1',100,100,300,0,0,0,1]]
    anims2 = [['window1', 400,200, 300,0,0,0,1],['2dancer1',100,200,300,0,0,0,1]]
    
    for anim in anims1:
        anim[5]= lengthPOSE(anim[0])
    anims0 = anims1


# display n pose animations on Laser 0
def Pose():
    global anims0, anims1, anims2
   
    for anim in anims0:
        PL = 0
        dots = []
        print(anim, anim[5])
        # repeat anim[7] time the same frame
        anim[6] +=1
        if anim[6] == anim[7]:

            anim[6] = 0
            # increase current frame and compare to total frame 
            anim[4] += 1
            if anim[4] == anim[5]:
                anim[4] = 0


        posename = 'poses/' + anim[0] + '/' + anim[0] +'-'+str("%05d"%anim[4])+'.json'
        posefile = open(posename , 'r') 
        posedatas = posefile.read()
        pose_json = json.loads(posedatas)

        for people in range(len(pose_json['people'])):

            lj3.rPolyLineOneColor(bodyCOCO(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(armCOCO(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(headCOCO(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])

            # Face
            '''
            #lj3.rPolyLineOneColor(face(pose_json, people), c=color,  PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(browL(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(browR(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(eyeR(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(eyeL(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.rPolyLineOneColor(nose(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])  
            lj3.rPolyLineOneColor(mouth(pose_json, people), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            '''

        lj3.DrawPL(PL)
        time.sleep(0.02)

    
    # decrease current frame 
    if keystates[pygame.K_w]: # and not keystates_prev[pygame.K_w]:
        CurrentPose -= 1
        if CurrentPose < 2:
            CurrentPose = numfiles -1
        #time.sleep(0.033) 
        print("Frame : ",CurrentPose) 

    # increaser current frame
    if keystates[pygame.K_x]: # and not keystates_prev[pygame.K_x]:
        CurrentPose += 1
        if CurrentPose > numfiles -1:
            CurrentPose = 1
        #time.sleep(0.033)
        print("Frame : ",CurrentPose)
    


# Curve 2 Faces
import json
CurrentPose = 1

def prepareFACES():


    # anim format (name, xpos, ypos, resize, currentframe, totalframe, count, frame repeat)
    #               0     1     2      3           4           5         6         7
    # total frame is fetched from directory file count
    
    anims[0] = [['detroit1', 300,300, 100,0,0,0,1]]
    anims[1] = [['detroit1', 400,200, 200,0,0,0,1]]
    anims[2] = [['detroit1', 500,200, 300,0,0,0,1]]

    '''
    # read anims number of frames from disk.
    for anim in range(len(anims0)):
        anims0[anim][5]= lengthPOSE(anims0[anim][0])
    for anim in range(len(anims1)):
        anims1[anim][5]= lengthPOSE(anims1[anim][0])
    for anim in range(len(anims2)):
        anims2[anim][5]= lengthPOSE(anims2[anim][0])
    '''

    #replace code below
    ''' 
    for laseranims in range(3):
	if debug > 0:
	        print "anims:",anims[laseranims],
        for anim in range(len(anims[laseranims])):
            anims[laseranims][anim][5]= lengthPOSE(anims[laseranims][anim][0])
	    if debug > 1:
		print anims[laseranims][anim][5]
    '''
    #by this one
    #thanks to https://stackoverflow.com/questions/19184335/is-there-a-need-for-rangelena


    for laseranims in anims:

        for anim in laseranims:
            anim[5] = lengthPOSE(anim[0])

            if debug > 0:
              print("anim :", anim)
              print("length :", anim[5])
    


# display the face animation describe in PoseDir
def Faces():
    
  for laseranims in range(3):
    for anim in anims[laseranims]:
        PL = laseranims
        #print PL, anim

        dots = []

        # increase counter [6] 
        # compare to repeat [7] time the same frame
        anim[6] +=1
        if anim[6] == anim[7]:

            # reset repeat
            anim[6] = 0

            # increase current frame [4]
            anim[4] += 1

            # compare to total frame [5]
            if anim[4] == anim[5]:
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
    
# Curve 3
# Dancers
import json
CurrentPose = 1

def prepareDANCERS():

    # anim format (name, xpos,ypos, resize, currentframe, totalframe, count, speed)
    # total frame is fetched from directory file count

    anims[0] = [['1dancer',500,200,300,0,0,0,10]]
    anims[1] = [['2dancer1',500,200,300,0,0,0,10]]
    anims[2] = [['window1',500,200,300,0,0,0,10]]   
    #anims[1] = [['2dancer1',100,200,300,0,0,0,10]]
    #anims[2] = [['window1',400,200, 300,0,0,0,10]]
    # read anims number of frames from disk.

    for laseranims in range(3):
        for anim in range(len(anims[laseranims])):
            anims[laseranims][anim][5]= lengthPOSE(anims[laseranims][anim][0])

# display the pose animation describe in PoseDir
def Dancers():
   
    for laseranims in range(3):

        for anim in anims[laseranims]:
            PL = laseranims
            #print PL, anim
            dots = []
            #print anim, anim[5]
            # repeat anim[7] time the same frame
            anim[6] +=1
            if anim[6] == anim[7]:

                anim[6] = 0
                # increase current frame and compare to total frame 
                anim[4] += 1
                if anim[4] == anim[5]:
                    anim[4] = 0


            #bhorosc.sendresol("/layer1/clip1/connect",1)
            #bhorosc.sendresol("/layer1/clip1/connect",0)

            posename = 'poses/' + anim[0] + '/' + anim[0] +'-'+str("%05d"%anim[4])+'.json'
            posefile = open(posename , 'r') 
            posedatas = posefile.read()
            pose_json = json.loads(posedatas)


            for people in range(len(pose_json['people'])):
                lj3.rPolyLineOneColor(bodyCOCO(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                lj3.rPolyLineOneColor(armCOCO(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])

                lj3.rPolyLineOneColor(browL(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                lj3.rPolyLineOneColor(browR(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                lj3.rPolyLineOneColor(eyeR(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                lj3.rPolyLineOneColor(eyeL(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                lj3.rPolyLineOneColor(nose(pose_json, people), c=color, PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])  
                lj3.rPolyLineOneColor(mouth(pose_json, people), c=color, PL = laseranims, closed = False,xpos = anim[1], ypos = anim[2], resize = anim[3])

            
            lj3.DrawPL(PL)

            '''
            lj3.PolyLineOneColor(bodyCOCO(pose_json), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.PolyLineOneColor(armCOCO(pose_json), c=color, PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            lj3.PolyLineOneColor(headCOCO(pose_json), c=color,  PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])


            PL[PL] = fwork.LinesPL(PL)
             '''


# Curve 4 IdiotIA
import json
CurrentPose = 1

def prepareIdiotIA():


    # anim format (name, xpos,ypos, resize, currentframe, totalframe, count, speed)
    # total frame is fetched from directory file count
    
    anims[0] = [['detroit1', 300,300, 100,0,0,0,1]]
    anims[1] = [['detroit1', 400,200, 200,0,0,0,1]]
    anims[2] = [['detroit1', 500,200, 300,0,0,0,1]]

    '''
    # read anims number of frames from disk.
    for anim in range(len(anims0)):
        anims0[anim][5]= lengthPOSE(anims0[anim][0])
    for anim in range(len(anims1)):
        anims1[anim][5]= lengthPOSE(anims1[anim][0])
    for anim in range(len(anims2)):
        anims2[anim][5]= lengthPOSE(anims2[anim][0])
    '''

    #replace code below
    ''' 
    for laseranims in range(3):
    if debug > 0:
            print "anims:",anims[laseranims],
        for anim in range(len(anims[laseranims])):
            anims[laseranims][anim][5]= lengthPOSE(anims[laseranims][anim][0])
        if debug > 1:
        print anims[laseranims][anim][5]
    '''
    #by this one
    #thanks to https://stackoverflow.com/questions/19184335/is-there-a-need-for-rangelena

    for laseranims in anims:
      if debug > 1:
          print("anims:",laseranims)
          for anim in laseranims:
            anim[5]=lengthPOSE(anim[0])
          if debug > 1:
            print(anim[5])
    


# display the face animation describe in PoseDir
def Faces():

  for laseranims in range(3):
    for anim in anims[laseranims]:
        PL = laseranims
        #print PL, anim
        dots = []
        #print anim, anim[5]
        # repeat anim[7] time the same frame
        anim[6] +=1
        if anim[6] == anim[7]:

            anim[6] = 0
            # increase current frame and compare to total frame 
            anim[4] += 1
            if anim[4] == anim[5]:
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


def OSCljclient(value):
    # Will receive message address, and message data flattened in s, x, y
    print("Bank0 got /bank0/ljclient with value", value)
    ljclient = value
    lj3.LjClient(ljclient)

def OSCpl(value):

    print("Bank0 got /bank0/pl with value", value)
    lj3.WebStatus("Bank0 to pl "+ str(value))
    lj3.LjPl(value)


# Dancers, Starfield, Pose, Face
def OSCrun(value):
    # Will receive message address, and message data flattened in s, x, y
    print("I got /run with value", value)
    doit = value

# /quit
def OSCquit():

    WebStatus("Bank0 stopping")
    print("Stopping OSC...")
    lj3.OSCstop()
    sys.exit()

def WebStatus(message):
    lj3.SendLJ("/status",message)



print('Loading Bank0...')

WebStatus("Load Bank0")

# OSC Server callbacks
print("Starting OSC at 127.0.0.1 port",OSCinPort,"...")
osc_startup()
osc_udp_server("127.0.0.1", OSCinPort, "InPort")

osc_method("/bank0/run*", OSCrun)
osc_method("/bank0/ping*", lj3.OSCping)
osc_method("/bank0/ljclient", OSCljclient)
osc_method("/bank0/ljpl", OSCpl)
osc_method("/quit", OSCquit)

'''
import pygame
pygame.init()
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
    print ("Pad2 :", pad2.get_name())
    numButtons = pad2.get_numbuttons()
    #print ("Axis Pad 2 :", str(pad2.get_numaxes()))
    #print ("Buttons Pad 2 :" , str(numButtons))
    
    # joy is pad abstraction to handle many different devices.
    joy2 = lj3.setup_controls(pad2)

if Nbpads > 0:

    pad1 = pygame.joystick.Joystick(0)
    pad1.init()
    print ("Pad1 :",pad1.get_name())
    numButtons = pad1.get_numbuttons()
    joy1 = lj3.setup_controls(pad1)
    #print ("Axis Pad 1 :", str(pad1.get_numaxes()))
    #print ("Buttons Pad 1 :" , str(numButtons))


'''

anims =[[],[],[],[]]
color = lj3.rgb2int(255,255,255)

#prepareSTARFIELD()
#preparePOSE()
#prepareDANCERS()
prepareFACES()


#doit = Starfield
#doit = Pose
doit = Faces
#doit = Dancers

WebStatus("Bank0 ready.")
print("Bank0 ready")

def Run():
    
    try:
        while 1:
            #Starfield(hori=0,verti=0)
            doit()

    except KeyboardInterrupt:
        pass

    # Gently stop on CTRL C

    finally:

        WebStatus("Bank0 Exit")
        print("Stopping OSC...")
        lj3.OSCstop()

    print ("Bank0 Stopped.")

Run()
