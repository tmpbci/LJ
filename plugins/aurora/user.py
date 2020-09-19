#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''

Aurora tutorial generator

Square

LICENCE : CC
Sam Neurohack


2 Cases : 

1/ You generate one points position (x,y,z) list, like a one color square and send it back to Aurora that will add color, move your points,...
    cf code Case 1

2/ You need several points positions lists with different parameters like colors,...
    cf code Case 2

    You need to use as much as primitive drawing functions you need :

        - PolyLineOneColor, rPolyLineOneColor, LineTo, Line
        - PolyLineRGB, rPolyLineRGB, LineRGBTo, LineRGB 
        - Text(word, integercolor, layer , xpos, ypos, resize, rotx, roty, rotz) : Display a word
        - TextRGB(word, red, green, blue, ...)

Your function get a LAY argument 

Layer properties from current UI. But you can use your numbers

    'number': 0
    'FX': "anim.Maxwell"
    'scandots': 10
    'scale': 2
    'color': red
    "run": True
    'Xcoord': 0
    'Ycoord': 250
    'Zcoord': 0
    'Xtransamt': 0
    'Ytransamt': 0
    'Ztransamt': 0
    'Xtranspeed': 0
    'Ytranspeed': 0
    'Ztranspeed': 0
    'Xrotdirec': 0
    'Yrotdirec': 0
    'Zrotdirec': 0
    'Xrotspeed': 0
    'Yrotspeed': 0
    'Zrotspeed': 0
    'rotspeed': 0
    'lineSize': 300
    'radius': 150
    'wavefreq': 3
    'step':0
    'steps': 500
    'stepmax': 200
    'stepvals': []
    'intensity': 255
    'closed': False
    'word': "hello"

'''

import numpy as np

#
# Code Case 1
# 

def slinear(samples, min, max):

    return np.linspace(min, max, samples)

# draw a square
def User1(LAY):

    dots = []
    size = LAY['lineSize']
    number = LAY['scandots']

    for x in slinear(number, 0, size):
        dots.append((x , 0, 0))

    for y in slinear(number, 0, size):
        dots.append((size , y, 0))

    for x in slinear(number, size, 0):
        dots.append((x , size, 0))

    for y in slinear(number, size, 0):
        dots.append((0 , y, 0))
    
    #print(dots)
    return dots

#
# Code Case 2
# 

import os, sys
import math
ljpath = r'%s' % os.getcwd().replace('\\','/')

#import from LJ
#sys.path.append(ljpath +'/libs/')
sys.path.append('../libs3')
#sys.path.append(ljpath +'/../../libs')

import lj23layers as lj

width = 800
height = 600
centerX = width / 2
centerY = height / 2


# colors examples
white = lj.rgb2int(255,255,255)
red = lj.rgb2int(255,0,0)
blue = lj.rgb2int(0,0,255)
green = lj.rgb2int(0,255,0)
cyan = lj.rgb2int(255,0,255)
yellow = lj.rgb2int(255,255,0)



def User2(LAY):
    
    for y in range(0, 300):

        dots = []
        lj.rLine((100 , y, 0), (150 , y, 0), c= red,  layer = LAY['number'], xpos = LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
        lj.rLineTo((200, y, 0), c= green,  layer = LAY['number'], xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
        lj.rLineTo((300, y, 0), c= red,  layer = LAY['number'], xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
        lj.rLineTo((350, y, 0), c= green,  layer = LAY['number'], xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
        lj.rLineTo((400,y, 0), c= red,  layer = LAY['number'], xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])


        '''
        for x in slinear(number, 0, 300):
            dots = []
            if  50 < x < 60:
                dots.append((x , y, 0))
                rLineTo(xy, c, layer , xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0)

            else:

            lj.rPolyLineOneColor(dots, c = LAY['color'], layer = LAY['number'], closed = False, xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
        for x in slinear(number, size, 0):
            dots.append((x , size, 0))
        '''

    #lj.rPolyLineRGBr(dots, c = white, layer = LAY['number'], closed = False, xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    #lj.rPolyLineOneColor(dots, c = LAY['color'], layer = LAY['number'], closed = False, xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])



def User3(LAY, data):

    dots = []
    for angle in slinear(LAY['scandots'], 0, 360):

        rad = angle * math.pi / 180
        x = LAY['radius'] * math.cos(rad)
        y = LAY['radius'] * math.sin(rad)
        dots.append((x+LAY['lineSize']/2, y, 0))

    lj.rPolyLineOneColor(dots, c = white, layer = LAY['number'], closed = False, xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(dots, c = LAY['color'], layer = LAY['number'], closed = False, xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])


# draw an helix
def User4(LAY):

    dots = []
    for angle in slinear(LAY['scandots'], 0, 360*LAY['wavefreq']):

        rad = angle * math.pi / 180
        x = LAY['radius'] * math.cos(rad)
        y =  LAY['radius'] * math.sin(rad)
        z = angle * 2
        
        dots.append((x+LAY['lineSize']/2, y, z))

    #print(dots)
    return dots

# draw a point
def User4(LAY):

    dots = []
    dots.append((centerX,centerY, 0))
    dots.append((centerX +2,centerY+2, 0))

    lj.rPolyLineOneColor(dots, c = red, layer = LAY['number'], closed = False, xpos = LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])


    #print(dots)
    return dots
