#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
Laser Jaying

LICENCE : CC
Sam Neurohack, Loloster, 

Openpose json files animations

Set for amiral castle :

Curve 0 : Mapping
Curve 1 : Pose align on Laser 0 for the moment
Curve 2 : Faces
Curve 3 : Dancers

'''


import math
import gstt
from globalVars import *
import bhoroscp
import colorify
import numpy as np
import pdb
import time
from datetime import datetime
import settings


# For Mapping()
# dedicated settings handler is in settings.py
import pygame

f_sine = 0



# Curve 0
# Edit shape mode / Run Mode

def MappingConf(section):
    global mouse_prev, sections

    print ""
    print "For Mapping(), reading Architecture Points"
    gstt.EditStep = 0
    gstt.CurrentWindow = -1
    gstt.CurrentCorner = 0
    gstt.CurrentSection = section
    mouse_prev = ((405, 325), (0, 0, 0))

    # Get all shapes points (="corners") for the given section of the conf file -> gstt.Windows 
    gstt.Windows = [] 
    sections = settings.MappingSections()

    print "" 
    #print "Sections : ", sections
    print "Reading Section : ", sections[gstt.CurrentSection]

    gstt.Laser = settings.MappingRead([sections[gstt.CurrentSection],'laser'])
    print "Laser : ", gstt.Laser
    gstt.simuPL = gstt.Laser

    for Window in xrange(settings.Mapping(sections[gstt.CurrentSection])-1):
        print "Reading option :  ", str(Window)
        shape = [sections[gstt.CurrentSection], str(Window)]
        WindowPoints = settings.MappingRead(shape)
        gstt.Windows.append(WindowPoints)

    print "Section points : " ,gstt.Windows




# section 0 is "General", then first screen shapes in section 1
# Todo : Should search automatically first screen in settings file sections.
# MappingConf(1) should be call only if curve 0 is selected 


def Mapping(fwork, keystates, keystates_prev):
    global mouse_prev, sections

    PL = gstt.Laser
    dots = []

    #switch to edit mode Key E ?
    if keystates[pygame.K_e] and not keystates_prev[pygame.K_e] and gstt.EditStep == 0:
            print "Switching to Edit Mode"
            gstt.EditStep = 1
            gstt.CurrentWindow = 0
            gstt.CurrentCorner = 0

    # Back to normal if ENTER key is pressed ?
    if keystates[pygame.K_RETURN] and gstt.EditStep == 1:    
            
            print "Switching to Run Mode"
            gstt.EditStep =0



    # EDIT MODE : cycle windows if press e key to adjust corner position 
    # Escape edit mode with enter key
    if gstt.EditStep >0:

        dots = []
        CurrentWindowPoints = gstt.Windows[gstt.CurrentWindow]

        # Draw all windows points or "corners"
        for corner in xrange(len(CurrentWindowPoints)):   
            dots.append(proj(int(CurrentWindowPoints[corner][0]),int(CurrentWindowPoints[corner][1]),0))
        fwork.PolyLineOneColor( dots, c=colorify.rgb2hex(gstt.color), PL = PL, closed = False )

        # Left mouse is clicked, modify current Corner coordinate
        if gstt.mouse[1][0] == mouse_prev[1][0] and mouse_prev[1][0] == 1:
            deltax = gstt.mouse[0][0]-mouse_prev[0][0]
            deltay = gstt.mouse[0][1]-mouse_prev[0][1]
            CurrentWindowPoints[gstt.CurrentCorner][0] += (deltax *2)
            CurrentWindowPoints[gstt.CurrentCorner][1] -= (deltay * 2)

        # Change corner if Z key is pressed.
        if keystates[pygame.K_z] and not keystates_prev[pygame.K_z]:
            if gstt.CurrentCorner < settings.Mapping(sections[gstt.CurrentSection]) - 1:
                gstt.CurrentCorner += 1
                print "Corner : ", gstt.CurrentCorner

        # Press E inside Edit mode : Next window 
        if keystates[pygame.K_e] and not keystates_prev[pygame.K_e]:

            # Save current Window and switch to the next one.
            if gstt.CurrentWindow < settings.Mapping(sections[gstt.CurrentSection]) -1:
                print "saving "
                settings.MappingWrite(sections,str(gstt.CurrentWindow),CurrentWindowPoints)
                gstt.CurrentWindow += 1
                gstt.CurrentCorner = -1
                if gstt.CurrentWindow == settings.Mapping(sections[gstt.CurrentSection]) -1:
                    gstt.EditStep == 0
                    gstt.CurrentWindow = 0              
                print "Now Editing window ", gstt.CurrentWindow

        mouse_prev = gstt.mouse
        gstt.PL[PL] = fwork.LinesPL(PL)

    # Press A : Next section ?
    if keystates[pygame.K_a] and not keystates_prev[pygame.K_a]: 
            
        print "current section : ", gstt.CurrentSection
        if gstt.CurrentSection < len(sections)-1:
            gstt.CurrentSection += 1
            print "Next section name is ", sections[gstt.CurrentSection]
            if "screen" in sections[gstt.CurrentSection]:
                print ""
                print "switching to section ", gstt.CurrentSection, " ", sections[gstt.CurrentSection]
                MappingConf(gstt.CurrentSection)
        else:
             gstt.CurrentSection = -1
        

    # RUN MODE
    if gstt.EditStep == 0:
        
        # Add all windows to PL for display
        for Window in gstt.Windows:  

            dots = []
            for corner in xrange(len(Window)):   
                #print "Editing : ", WindowPoints[corner]
                #print Window[corner][0]
                dots.append(proj(int(Window[corner][0]),int(Window[corner][1]),0))
            
            fwork.PolyLineOneColor( dots, c=colorify.rgb2hex(gstt.color), PL = PL, closed = False  )
    
        gstt.PL[PL] = fwork.LinesPL(PL)



# Curve 1 : generic pose animations
import json
gstt.CurrentPose = 1
'''
# get absolute body position points
def getCOCO(pose_json,pose_points):
    
    dots = []
    for dot in pose_points:
        if len(pose_json['part_candidates'][0][str(dot)]) != 0:
            dots.append((pose_json['part_candidates'][0][str(dot)][0], pose_json['part_candidates'][0][str(dot)][1]))
    return dots


# get relative (-1 0 1) body position points. a position -1, -1 means doesn't exist
def getBODY(pose_json,pose_points):

    dots = []
    for dot in pose_points:
        #print pose_points
        if len(pose_json['people'][0]['pose_keypoints_2d']) != 0:
            #print "people 0"
            if pose_json['people'][0]['pose_keypoints_2d'][dot * 3] != -1 and  pose_json['people'][0]['pose_keypoints_2d'][(dot * 3)+1] != -1:
                dots.append((pose_json['people'][0]['pose_keypoints_2d'][dot * 3], pose_json['people'][0]['pose_keypoints_2d'][(dot * 3)+1]))

        #if len(pose_json['people']) != 1:
            #print "people1"
            #print "people 1", pose_json['people'][1]['pose_keypoints_2d']
        #print len(pose_json['people'])

    return dots


# get absolute face position points 
def getFACE(pose_json,pose_points):

    dots = []
    for dot in pose_points:

        if len(pose_json['people'][0]['face_keypoints_2d']) != 0:
            print "people 0"
            if pose_json['people'][0]['face_keypoints_2d'][dot * 3] != -1 and  pose_json['people'][0]['face_keypoints_2d'][(dot * 3)+1] != -1:
                dots.append((pose_json['people'][0]['face_keypoints_2d'][dot * 3], pose_json['people'][0]['face_keypoints_2d'][(dot * 3)+1]))

        if len(pose_json['people']) != 1:
            print "people 1"
            #print "people 1", pose_json['people'][1]['face_keypoints_2d']
    return dots


# Body parts
def bodyCOCO(pose_json):
    pose_points = [10,9,8,1,11,12,13]
    return getBODY(pose_json,pose_points)

def armCOCO(pose_json):
    pose_points = [7,6,5,1,2,3,4]
    return getBODY(pose_json,pose_points)

def headCOCO(pose_json):
    pose_points = [1,0]
    return getBODY(pose_json,pose_points)


# Face keypoints
def face(pose_json):
    pose_points = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    return getFACE(pose_json,pose_points)

def browL(pose_json):
    pose_points = [26,25,24,23,22]
    return getFACE(pose_json,pose_points)

def browR(pose_json):
    pose_points = [21,20,19,18,17]
    return getFACE(pose_json,pose_points)

def eyeR(pose_json):
    pose_points = [36,37,38,39,40,41,36]
    return getFACE(pose_json,pose_points)

def eyeL(pose_json):
    pose_points = [42,43,44,45,46,47,42]
    return getFACE(pose_json,pose_points)

def nose(pose_json):
    pose_points = [27,28,29,30]
    return getFACE(pose_json,pose_points)

def mouth(pose_json):
    pose_points = [48,59,58,57,56,55,54,53,52,51,50,49,48,60,67,66,65,64,63,62,61,60]
    return getFACE(pose_json,pose_points)


# best order face : face browL browr eyeR eyeL nose mouth
'''


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
        '''
        if len(pose_json['people']) > 1:
            print len(pose_json['people']) 
            print "people 1 face ", pose_json['people'][1]['face_keypoints_2d']
        '''

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


# Get frame number for pose path describe in gstt.PoseDir 
def lengthPOSE(pose_dir):


    if gstt.debug > 0:
      print "Check directory ",'poses/' + pose_dir + '/'
    numfiles = sum(1 for f in os.listdir('poses/' + pose_dir + '/') if os.path.isfile(os.path.join('poses/' + pose_dir + '/', f)) and f[0] != '.')
    if gstt.debug > 0:
      print "Pose : ", pose_dir, numfiles, "images"
    return numfiles


def preparePOSE():

    # anim format (name, xpos,ypos, resize, currentframe, totalframe, count, speed)
    # total frames is fetched from directory file count
    
    anims1 = [['sky',50,100,300,0,0,0,1],['2dancer1', 400,100, 300,0,0,0,1],['1dancer', 400,100, 300,0,0,0,1],['window1',100,100,300,0,0,0,1]]
    anims2 = [['window1', 400,200, 300,0,0,0,1],['2dancer1',100,200,300,0,0,0,1]]
    
    for anim in anims1:
        anim[5]= lengthPOSE(anim[0])
    gstt.anims0 = anims1


# display n pose animations on Laser 0
def Pose(fwork):
   
    for anim in gstt.anims0:
        PL = 0
        dots = []
        print anim, anim[5]
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

            fwork.rPolyLineOneColor(bodyCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(armCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(headCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color),  PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])

            # Face
            '''
            #fwork.rPolyLineOneColor(face(pose_json, people), c=colorify.rgb2hex(gstt.color),  PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(browL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(browR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(eyeR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(eyeL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(nose(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])  
            fwork.rPolyLineOneColor(mouth(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            '''

        gstt.PL[PL] = fwork.LinesPL(PL)
        time.sleep(0.02)

    
    # decrease current frame 
    if gstt.keystates[pygame.K_w]: # and not gstt.keystates_prev[pygame.K_w]:
        gstt.CurrentPose -= 1
        if gstt.CurrentPose < 2:
            gstt.CurrentPose = gstt.numfiles -1
        #time.sleep(0.033) 
        print "Frame : ",gstt.CurrentPose 

    # increaser current frame
    if gstt.keystates[pygame.K_x]: # and not gstt.keystates_prev[pygame.K_x]:
        gstt.CurrentPose += 1
        if gstt.CurrentPose > gstt.numfiles -1:
            gstt.CurrentPose = 1
        #time.sleep(0.033)
        print "Frame : ",gstt.CurrentPose 
    


# Curve 2 Faces
import json
gstt.CurrentPose = 1

def prepareFACES():


    # anim format (name, xpos,ypos, resize, currentframe, totalframe, count, speed)
    # total frame is fetched from directory file count
    
    gstt.anims[0] = [['detroit1', 300,300, 100,0,0,0,1]]
    gstt.anims[1] = [['detroit1', 400,200, 200,0,0,0,1]]
    gstt.anims[2] = [['detroit1', 500,200, 300,0,0,0,1]]

    '''
    # read anims number of frames from disk.
    for anim in range(len(gstt.anims0)):
        gstt.anims0[anim][5]= lengthPOSE(gstt.anims0[anim][0])
    for anim in range(len(gstt.anims1)):
        gstt.anims1[anim][5]= lengthPOSE(gstt.anims1[anim][0])
    for anim in range(len(gstt.anims2)):
        gstt.anims2[anim][5]= lengthPOSE(gstt.anims2[anim][0])
    '''

    for laseranims in range(3):
        print laseranims
        for anim in range(len(gstt.anims[laseranims])):
            gstt.anims[laseranims][anim][5]= lengthPOSE(gstt.anims[laseranims][anim][0])

# display the face animation describe in gstt.PoseDir
def Faces(fwork):

  for laseranims in range(3):
    for anim in gstt.anims[laseranims]:
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

            #fwork.rPolyLineOneColor(face(pose), c=colorify.rgb2hex(gstt.color),  PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(browL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(browR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(eyeR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(eyeL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(nose(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])  
            fwork.rPolyLineOneColor(mouth(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
        
        gstt.PL[PL] = fwork.LinesPL(PL)
        time.sleep(0.02)
    
# Curve 3
# Dancers
import json
gstt.CurrentPose = 1

def prepareDANCERS():

    # anim format (name, xpos,ypos, resize, currentframe, totalframe, count, speed)
    # total frame is fetched from directory file count

    gstt.anims[0] = [['1dancer',500,200,300,0,0,0,10]]
    gstt.anims[1] = [['2dancer1',500,200,300,0,0,0,10]]
    gstt.anims[2] = [['window1',500,200,300,0,0,0,10]]    
    #gstt.anims[1] = [['2dancer1',100,200,300,0,0,0,10]]
    #gstt.anims[2] = [['window1',400,200, 300,0,0,0,10]]
    # read anims number of frames from disk.
    print gstt.anims

    for laseranims in range(3):
        print laseranims
        for anim in range(len(gstt.anims[laseranims])):
            gstt.anims[laseranims][anim][5]= lengthPOSE(gstt.anims[laseranims][anim][0])

# display the pose animation describe in gstt.PoseDir
def Dancers(fwork):
   
    for laseranims in range(3):
        for anim in gstt.anims[laseranims]:
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
                fwork.rPolyLineOneColor(bodyCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                fwork.rPolyLineOneColor(armCOCO(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])

                fwork.rPolyLineOneColor(browL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                fwork.rPolyLineOneColor(browR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                fwork.rPolyLineOneColor(eyeR(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                fwork.rPolyLineOneColor(eyeL(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
                fwork.rPolyLineOneColor(nose(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])  
                fwork.rPolyLineOneColor(mouth(pose_json, people), c=colorify.rgb2hex(gstt.color), PL = laseranims, closed = False,xpos = anim[1], ypos = anim[2], resize = anim[3])

            
            gstt.PL[PL] = fwork.LinesPL(PL)

            '''
            fwork.rPolyLineOneColor(bodyCOCO(pose_json), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(armCOCO(pose_json), c=colorify.rgb2hex(gstt.color), PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])
            fwork.rPolyLineOneColor(headCOCO(pose_json), c=colorify.rgb2hex(gstt.color),  PL = 0, closed = False, xpos = anim[1], ypos = anim[2], resize = anim[3])


            gstt.PL[PL] = fwork.LinesPL(PL)
             '''
