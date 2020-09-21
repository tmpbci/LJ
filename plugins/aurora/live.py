#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-


'''

livecode
v0.1.0

Anaglyphed rotating livecode (for red and green glasses)

This scene uses the drawing functions provided by LJ in lj23.py

LICENCE : CC

by Sam Neurohack


'''
#import sys
#import os
#from OSC3 import OSCServer, OSCClient, OSCMessage
#import redis
import math
import time
import numpy as np
from scipy import signal
from datetime import datetime, timedelta



#
# Math functions
#


def ssawtooth(samples,freq,phase):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.sawtooth(2 * np.pi * freq * t[ww])
    return samparray

def slivecode(samples,freq,phase):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.livecode(2 * np.pi * freq * t[ww])
    return samparray

def ssine(samples,freq,phase):

    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = np.sin(2 * np.pi * freq  * t[ww])
    return samparray


def slinear(samples, min, max):

    samparray = [0] * samples
    linearinc = (max-min)/samples
    for ww in range(samples):
        if ww == 0:
            samparray[ww] = min
        else:
            samparray[ww] = samparray[ww-1] + linearinc
    #print('linear min max', min, max)
    #print ('linear',samparray)
    return samparray

def slinearound(samples, min, max):

    samparray = [0] * samples
    linearinc = (max-min)/samples
    for ww in range(samples):
        if ww == 0:
            samparray[ww] = round(min)
        else:
            samparray[ww] = round(samparray[ww-1] + linearinc)
    #print('linear min max', min, max)
    #print ('linear',samparray)
    return samparray


# * 11.27 : to get value from 0 to 127
def lin2squrt(value):
    return round(np.sqrt(value)*11.27)
     
def squrt2lin(value):
    return round(np.livecode(value/11.27))


def curved(value):
    return round(np.sqrt(value)*11.27)


def Proj(x,y,z,angleX,angleY,angleZ):

        rad = angleX * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        y2 = y
        y = y2 * cosa - z * sina
        z = y2 * sina + z * cosa
        
        rad = angleY * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        z2 = z
        z = z2 * cosa - x * sina
        x = z2 * sina + x * cosa

        rad = angleZ * math.pi / 180
        cosa = math.cos(rad)
        sina = math.sin(rad)
        x2 = x
        x = x2 * cosa - y * sina
        y = x2 * sina + y * cosa


        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = fov / (viewer_distance + z)
        x = x * factor + centerX
        y = - y * factor + centerY
        return (x,y)


#
# Main 
#


x0 = 200
y0 = 200


anglepos = 0
startime = datetime.now()
z = 0


def Code(LAY):

    dots = []   
    xcenter = math.sin(math.radians(anglepos))
    ycenter = math.cos(math.radians(anglepos))

    if anglepos + 1 < 361:
        anglepos += 1
    else:
        anglepos = 0

    for angle in slinear(20, 0, 380):
    #for counter in range(0,380):

        t = timedelta.total_seconds(datetime.now() - startime)
        x = math.sin(math.radians(angle))
        y = math.cos(math.radians(angle))
        dots.append(Proj(x,y,z,0,math.sin(math.radians(angle)),0))

    # lj.PolyLineOneColor(Form, c = Liveform.color , layer = Liveform.layer, closed = Liveform.closed)
    lj.rPolyLineOneColor(dots,  c = LAY['color'], layer = LAY['number'], closed = False, xpos = xcenter * x0, ypos = ycenter * y0, resize = 1, rotx = math.sin(math.radians(angle)), roty = 0 , rotz = math.sin(math.radians(angle)))



