#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''

Aurora Animations points generators

LICENCE : CC
Sam Neurohack

"ScanH", "ScanV", "Wave", "Circle", "Dot00", "Zero", "Maxwell", "Starfield", "Trckr", "Word"

'''

import time, math, sys, os
import numpy as np
from scipy import signal
from random import randrange, randint, random
import live

ljpath = r'%s' % os.getcwd().replace('\\','/')
# import from shell
sys.path.append(ljpath +'/../../libs3/')
sys.path.append(ljpath +'/../libs3/')

#import from LJ
sys.path.append(ljpath +'/libs3/')


sys.path.append('../libs3')
sys.path.append(ljpath +'/../../libs3')

import lj23layers as lj
import gstt

screen_size = [700,700]
xy_center = [screen_size[0]/2,screen_size[1]/2]

width = 700
height = 700
centerX = width / 2
centerY = height / 2

# 3D to 2D projection parameters
fov = 256
viewer_distance = 2.2

# Useful variables init.
white = lj.rgb2int(255,255,255)
red = lj.rgb2int(255,0,0)
blue = lj.rgb2int(0,0,255)
green = lj.rgb2int(0,255,0)
cyan = lj.rgb2int(255,0,255)
yellow = lj.rgb2int(255,255,0)

lifenb = 10

'''
# Animation parameters for each layer
X  = [{'coord': 0, 'rotspeed': 0, 'transpeed': 0, 'transmax': 0}] *3
Y  = [{'coord': 0, 'rotspeed': 0, 'transpeed': 0, 'transmax': 0}] *3
Z  = [{'coord': 0, 'rotspeed': 0, 'transpeed': 0, 'transmax': 0}] *3

Layer  = [{'scandots': 100, 'radius': 150, 'color': red, "run": True, "step":0, 'steps': 500, 'stepmax': 200, 'stepvals': [], 'lineSize': 300, 'intensity': 255}] * 3

Xacc = 0.01
Yacc = 0.01
Zacc = 0.00
'''


# 
# Useful functions
#

def remap(s,min1,max1, min2, max2):
    a1, a2 = min1, max1  
    b1, b2 = min2, max2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


minred = 0
mingreen = 0
minblue = 0

maxz=50
z = 20
col = (255,255,255)


def z2color(z, color):
    rgbcolor = int2rgb(color)
    #print()
    #print("z2color : z =", z, "color =",color,"rgb :", rgbcolor)
    newcolor = (z2range(z, rgbcolor[0], minred), z2range(z, rgbcolor[1], mingreen),  z2range(z, rgbcolor[2], minblue))
    #print("newcolor :", newcolor)
    return rgb2int(newcolor)

def rgb2int(rgb):
    return int('0x%02x%02x%02x' % tuple(rgb),0)

def int2rgb(intcode):
    #hexcode = hex(intcode)[2:]
    hexcode = '{0:06X}'.format(intcode)
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    #return tuple(map(ord,hexcode[1:].decode('hex')))

def z2range(z,color, mincolor):
    #print("z2range : z=", z, "maxz :",maxz,"component =",color, "mincolor =",mincolor)
    if color < mincolor:
        return mincolor
    a1, a2 = maxz,0
    b1, b2 = mincolor, color
    #print ("color component :", round(b1 + ((z - a1) * (b2 - b1) / (a2 - a1))))
    return  round(b1 + ((z - a1) * (b2 - b1) / (a2 - a1)))

def cc2range(s,min,max):
    a1, a2 = 0,127  
    b1, b2 = min, max
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

def range2cc(s,min,max):
    a1, a2 = min, max
    b1, b2 = 0,127
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def Proj(x, y, z, angleX, angleY, angleZ):

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


def ssawtooth(samples, freq, phase, scale = 1):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.sawtooth(2 * np.pi * freq * t[ww]) * scale
    return samparray

def ssquare(samples, freq, phase, scale = 1):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = signal.square(2 * np.pi * freq * t[ww]) * scale
    return samparray

def ssine(samples, freq, phase, scale = 1):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = np.sin(2 * np.pi * freq  * t[ww]) * scale
    return samparray

def scos(samples, freq, phase, scale = 1):

    samparray = [0] * samples
    t = np.linspace(0+phase, 1+phase, samples)
    for ww in range(samples):
        samparray[ww] = np.cos(2 * np.pi * freq  * t[ww]) * scale
    return samparray


def slinear(samples, min, max):

    return np.linspace(min, max, samples)

Range =0

def rangelinear(samples, min, max):
    global Range

    samparray = []
    samparray.append(min)
    for sample in range(samples-2):
        samparray.append(Range+sample)
    samparray.append(max)

    if Range + samples-2 > max:
        Range = min
    Range += 1

    return sorted(samparray)


def randlinear(samples, min, max):

    samparray = []
    for sample in range(samples):
        samparray.append(randrange(max))
    return sorted(samparray)

# as randlinear but first min and last is max
def randlinear2(samples, min, max):

    samparray = []
    samparray.append(min)
    for sample in range(samples-2):
        samparray.append(randrange(int(max)))
    samparray.append(max)
    return sorted(samparray)

'''
def slinear(samples, min, max):

    linearray = [0] * samples
    linearinc = (max-min)/samples
    for ww in range(samples):
        if ww == 0:
            linearray[ww] = min
        else:
            linearray[ww] = linearray[ww-1] + linearinc
    print ('linear :',linearray)
    return linearray
'''

def sbilinear(samples, min, max):

    samparray = [0] * samples
    half = round(samples/2)

    # UP : min -> max
    part = np.linspace(min,max, half)
    for ww in range(half):
        samparray[ww] = part[ww]

    # Down : max -> min
    part = np.linspace(max,min, half)
    for ww in range(half):
        samparray[half+ww] = part[ww]
    #print('linear min max', min, max)
    #print ('linear',samparray)
    return samparray


#
# FXs
# 

'''
Beatstep memory 2 Aurora simplex

'''

def ScanV(LAY):

    dots = []
    arr = randlinear2(LAY['scandots'],0, LAY['lineSize'])
    #arr =  slinear(LAY['scandots'], LAY['lineSize'], 0)
    #print(arr)
    for y in arr:
        #print(y, LAY['lineSize'] )
        dots.append((0 + LAY['lineSize']/2, y - LAY['lineSize']/2, 0))

    return dots


def ScanH(LAY):

    dots = []
    #print(slinear(LAY['scandots'], 0, LAY['lineSize']))
    for x in sbilinear(LAY['scandots']*2, LAY['lineSize'],0):
        dots.append((x , 0, 0))
    #print(dots)
    return dots


def Wave(LAY):

    dots = []
    x = slinear(round(LAY['lineSize']), 0, LAY['lineSize'])
    y = ssine(round(LAY['lineSize']), LAY['wavefreq'], 0)

    for ww in range(round(LAY['lineSize'])):
        dots.append((50+x[ww], 50+y[ww] * LAY['radius'], 0))

    return dots


def Circle(LAY):

    dots = []
    for angle in slinear(LAY['scandots'], 0, 360):

        rad = angle * math.pi / 180
        x = LAY['radius'] * math.cos(rad)
        y = LAY['radius'] * math.sin(rad)
        dots.append((x+LAY['lineSize']/2, y, 0))

    return dots


def Word(LAY):


    lj.Text(LAY['word'], c = LAY['color'], layer = LAY['number'], xpos = LAY['Xcoord']+LAY['lineSize']/2, ypos = LAY['Ycoord'], resize = LAY['scale']*10, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    #lj.rPolyLineOneColor([(x/2,y/2),((x+1)/2,(y+1)/2)], c = LAY['color'], layer = l, xpos = 0, ypos = 0, resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])


def Dot00(LAY):

    dots = []
    dots.append((0, 0, 0))
    return dots


def Zero(LAY):

    dots = []
    return dots



#
# Starfields
# 


def Onefield(LAY, Field, hori=0,verti=0):


    # starpoints = []
    #print(Field['displayedstars'], 'stars displayed')

    # Increase number of 
    if Field['displayedstars'] < Field['num_stars'] and Field['starfieldcount'] % 15 == 0:
        Field['displayedstars'] += 1

    #if displayedstars == num_stars and starfieldcount % 10 == 0:
    #    starspeed += 0.005

    #print starspeed

    for starnumber in range(0, Field['displayedstars']):
    
        # The Z component is decreased on each frame.
        Field['stars'][starnumber][2] -= Field['starspeed'] * 3


        # If the star has past the screen (I mean Z<=0) then we
        # reposition it far away from the screen (Z=max_depth)
        # with random X and Y coordinates.
        if Field['stars'][starnumber][2] <= 0:
            Field['stars'][starnumber][0] = randrange(-25,25)
            Field['stars'][starnumber][1] = randrange(-25,25)
            Field['stars'][starnumber][2] = Field['max_depth']


        # Convert the 3D coordinates to 2D using perspective projection.
        k = 128.0 / Field['stars'][starnumber][2]

        # Move Starfield origin.
        # if stars xpos/ypos is same sign (i.e left stars xpos is <0) than (joystick or code) acceleration (hori and verti moves the star field origin)
        if np.sign(Field['stars'][starnumber][0]) == np.sign(hori):
            x = int(Field['stars'][starnumber][0] * k + xy_center[0] + (hori*600))
        else:
            x = int(Field['stars'][starnumber][0] * k + xy_center[0] + (hori*500))

        if np.sign(Field['stars'][starnumber][1]) == np.sign(verti):
            y = int(Field['stars'][starnumber][1] * k + xy_center[1] + (verti*600))
        else:
            y = int(Field['stars'][starnumber][1] * k + xy_center[1] + (verti*500))


        # Add star to pointlist PL 0 if field display flag is true
        if 0 <= x < screen_size[0] - 2 and 0 <= y < screen_size[1] - 2:
            # print("adding star", str(x0)+","+str(y0), "to fields 0")
            #lj.PolyLineOneColor([(x0,y0),((x0+1),(y0+1))], c = Stars0Form.color, layer = Stars0Form.layer, closed = Stars0Form.closed)
            # print((x/2,y/2),((x+1)/2,(y+1)/2))
            #print( int2rgb(z2color(Field['stars'][starnumber][2], LAY['color'])))
            #lj.rPolyLineOneColor([(x/2,y/2),((x+1)/2,(y+1)/2)], c =LAY['color'], layer = LAY['number'], closed = False, xpos = 0, ypos = 0, resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
            lj.rPolyLineOneColor([(x/2,y/2,0),((x+1)/2,(y+1)/2,0)], c = z2color(Field['stars'][starnumber][2], LAY['color']), layer = LAY['number'], closed = False, xpos = -200, ypos = 0, resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])



#
# Maxwell
#

'''
Beatstep Encoders 3 :
LX freq amp phasemod transamt   RX freq amp phasemod rotdire
LY freq amp phasemod transamt   RL freq amp phasemod rotdire
'''

# sin:0/saw:33/squ:95/lin:127

def MaxOneSide(LAY, Cux, Cuy, Cuz):

    
    #sines =  ssine(LAY['scandots'], Cu['freq'], Cu['phasemod'], scale = Cu['amp'])
    #cosines = scos(LAY['scandots'], Cu['freq'], Cu['phasemod'], scale = Cu['amp'])
    #sines =  ssine(LAY['scandots'], Cux['freq'], Cux['phaseoffset'], scale = Cux['amp'])
    #cosines = ssine(LAY['scandots'], Cux['freq'], Cux['phaseoffset'], scale = Cux['amp'])

    '''
    cosines = scos(LAY['scandots'], Cu['freq'], Cu['phase'], scale = Cu['amp'])
    saws = ssawtooth(LAY['scandots'], Cu['freq'], Cu['phase'], scale = Cu['amp'])
    sqrs = ssquare(LAY['scandots'], Cu['freq'], Cu['phase'], scale = Cu['amp'])
    '''

    dots = []
    #print("X", Cux['type'], Cux['phaseoffset'], Cux['inv'], Cux['amp'])
    if Cux['type'] ==0:
        xsteps = ssine(LAY['scandots'],     Cux['freq'], Cux['phaseoffset'] + Cux['inv'], Cux['amp'])
    if Cux['type'] ==33:
        xsteps = ssawtooth(LAY['scandots'], Cux['freq'], Cux['phaseoffset'] + Cux['inv'], Cux['amp'])
    if Cux['type'] == 95:
        xsteps = ssquare(LAY['scandots'],   Cux['freq'], Cux['phaseoffset'] + Cux['inv'], Cux['amp'])
    if Cux['type'] == 127:
        xsteps = slinear(LAY['scandots'], 0, Cux['amp'])

    #print("Y", Cuy['type'], Cuy['phaseoffset'], Cuy['inv'], Cuy['amp'])
    if Cuy['type'] ==0:
        ysteps = ssine(LAY['scandots'],     Cuy['freq'], Cuy['phaseoffset'] + Cuy['inv'], Cuy['amp'])
    if Cuy['type'] ==33:
        ysteps = ssawtooth(LAY['scandots'], Cuy['freq'], Cuy['phaseoffset'] + Cuy['inv'], Cuy['amp'])
    if Cuy['type'] == 95:
        ysteps = ssquare(LAY['scandots'],   Cuy['freq'], Cuy['phaseoffset'] + Cuy['inv'], Cuy['amp'])
    if Cuy['type'] == 127:
        ysteps = slinear(LAY['scandots'], 0, Cuy['amp'])

    #print("xsteps", xsteps)
    #print("ysteps", ysteps)

    for step in range(LAY['scandots']):

        # Cu['type']  sin:0/saw:33/squ:95/lin:127
        x = xsteps[step]
        y = ysteps[step]
        #x = sines[step]
        #y = cosines[step]
        dots.append((x, y, 0))

    return dots

CurveLX = [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3
CurveLY = [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': np.pi/2}] * 3
CurveLZ = [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3

CurveRX = [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3
CurveRY = [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': np.pi/2}] * 3
CurveRZ = [{'type': 0, 'freq': 1, 'amp': 150, 'phasemod': 0, 'phaseoffset': 0, 'inv': 0}] * 3


def Maxwell(LAY):

    l =0
    mixer = 0

    dots = []
    dotsL = MaxOneSide(LAY, CurveLX[l], CurveLY[l], CurveLZ[l])
    dotsR = MaxOneSide(LAY, CurveRX[l], CurveRY[l], CurveRZ[l])

    for dot in range(LAY['scandots']):
        dotX = (dotsL[dot][0]*(100-mixer)/100) + (dotsR[dot][0]*mixer/100)   #+ transX.values[point]
        dotY = (dotsL[dot][1]*(100-mixer)/100) + (dotsR[dot][1]*mixer/100)   #+ transY.values[point]
        dotZ = (dotsL[dot][2]*(100-mixer)/100) + (dotsR[dot][2]*mixer/100)   #+ transZ.values[point]
        dots.append((dotX, dotY, dotZ))
    return dots
    '''
    for dot in range(LAY['scandots']):
        dotX = (dotsL[dot][0]*(100-LAY['mixer'])/100) + (dotsR[dot][0]*LAY['mixer']/100)                #+ transX.values[point]
        dotY = (dotsL[dot][1]*(100-LAY['mixer'])/100) + (dotsR[dot][1]*LAY['mixer']/100)   #+ transY.values[point]
        dotZ = (dotsL[dot][2]*(100-LAY['mixer'])/100) + (dotsR[dot][2]*LAY['mixer']/100)   #+ transZ.values[point]
        dots.append((dotX, dotY, dotZ))
    '''

#
# Trckr
#

# get absolute face position points 
def getPART(TrckrPts, pose_points):

    dots = []
    for dot in pose_points:

        dots.append((TrckrPts[dot][0], TrckrPts[dot][1],0))

    return dots


# Face keypoints
def face(TrckrPts):
    pose_points = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    return getPART(TrckrPts, pose_points)

def browL(TrckrPts):
    pose_points = [15,16,17,18]
    return getPART(TrckrPts, pose_points)

def browR(TrckrPts):
    pose_points = [22,21,20,19]
    return getPART(TrckrPts, pose_points)

def eyeR(TrckrPts):
    pose_points = [25,64,24,63,23,66,26,65,25]
    return getPART(TrckrPts, pose_points)

def eyeL(TrckrPts):
    pose_points = [28,67,29,68,30,69,31,28]
    return getPART(TrckrPts, pose_points)

def pupR(TrckrPts):
    pose_points = [27]
    return getPART(TrckrPts, pose_points)

def pupL(TrckrPts):
    pose_points = [32]
    return getPART(TrckrPts, pose_points)


def nose1(TrckrPts):
    pose_points = [62,41,33]
    return getPART(TrckrPts, pose_points)

def nose2(TrckrPts):
    pose_points = [40,39,38,43,37,42,36,35,34]
    return getPART(TrckrPts, pose_points)

def mouth(TrckrPts):
    pose_points = [50,49,48,47,46,45,44,55,54,53,52,51,50]
    return getPART(TrckrPts, pose_points)

def mouthfull(TrckrPts):
    pose_points = [50,49,48,47,46,45,44,55,54,53,52,51,50,59,60,61,44,56,57,58,50]
    return getPART(TrckrPts, pose_points)


def Trckr(LAY, TrckrPts):


    #lj.rPolyLineOneColor([(x/2,y/2),((x+1)/2,(y+1)/2)], c = LAY['color'], layer = l, closed = False, xpos = 0, ypos = 0, resize = LAY['scale'], rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    #print(LAY['scale'])
    #print("browL", browL(), "browR", browR(), "nose1", nose1(), "mouth", mouth())
    lj.rPolyLineOneColor(browL(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(eyeL(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(browR(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(eyeR(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(pupL(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(pupR(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(nose1(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(nose2(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])
    lj.rPolyLineOneColor(mouthfull(TrckrPts), c = LAY['color'], layer = LAY['number'], closed = False, xpos = -200 +LAY['Xcoord'], ypos = LAY['Ycoord'], resize = LAY['scale']*0.8, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])




#
# Butterfly
#



entities = []

for lifes in range(0,lifenb,1):

    # 0: random posX, 1: random posY, 2: wing position, 3: Color, 4: XDirection
    entities.append([randint(100,width-100), randint(100,height-100), random(), randint(45,16700000), randint(-2,2)])
    

print("entities", entities)
wingpos = random()


# One wing vertices
vertices = [
( 0.0 , 0.3603683 , 0.7174169 ), #1
( 0.0 , -4.39773 , 0.09228338 ), #2 
( wingpos , 0.3603683 , 0.3174169 ), #3
( 0.0 , 0.3603683 , 0.7174169 ), #4
( -wingpos , 0.4115218 , 0.1858825 ), #7
( 0.0 , -4.39773 , 0.09228338 ) #2  
    ]
'''

vertices = [
( 0.0 , -4.39773  , 0.7174169 ), # 1
( 0.0 , 4.39773 , 0.09228338 ), # 2 
( wingpos , 0.3603683 , 0.3174169 ), # 3
( 0.0 , 0.3603683 , 0.7174169 ), # 4
( wingpos ,  -4.39773, 0.7174169 ), # 5
( 0.0 , -4.39773  , 0.7174169 ), # 6 = 1
( -wingpos ,-4.39773 , 0.1858825 ), #7
( 0.0 , 0.3603683 , 0.7174169 ), # 8
( -wingpos , 0.3603683 , 0.3174169 ), # 9
( 0.0 , 4.39773 , 0.09228338 ), # 10
    ]
'''
fov = 256
viewer_distance = 70.2

angleX = 0
angleY = 120
angleZ = 0

color = 0x101010
speed = 0

def Butterfly(LAY):
    global angleX, angleY, angleZ
    #angleX += 0.0
    #angleY += 0.0
    #angleZ += 0.0
    
    for entity in entities:
        #print(entity)
        entity[0] += entity[4] + randint(-1,1)          # change X/Y pos (Xdirection and little chaos)
        if randint(0,20) > 15:
            entity[1] += randint(-2,2)
        
        centerX = entity[0]
        centerY  = entity[1]
                                                        # remember : z position is overall zoom         
        entity[2] += 1                                  # wings animation                                           
        if entity[2] > 10:
            entity[2] = 0.0
        wingpos = entity[2]
        
        angleX = angleX                                 # entity rotated in Z to follow Xdirection          
        angleY = angleY

        if entity[4] > 0:
            angleZ = (angleZ + entity[4]*18)
        else:
            angleZ = -(angleZ + entity[4]*18)
        
        color = entity[3]  
        dots = []
        verticecounter = 0
        
        for v in vertices:
        
            x = v[0]
            y = v[1]
            z = v[2]
            if  verticecounter == 2:
                x = wingpos 
            if  verticecounter == 4:
                x = - wingpos 
            #print(x,y,z)

            dots.append(Proj(x+entity[0], y+entity[1], z, angleX, angleY, angleZ))
            verticecounter +=1
        #print(dots)

        lj.rPolyLineOneColor(dots, c = LAY['color'], layer = LAY['number'], closed = False, xpos = -300 +LAY['Xcoord'], ypos = -300+LAY['Ycoord'], resize = LAY['scale']*1.3, rotx = LAY['Xrotdirec'], roty = LAY['Yrotdirec'], rotz = LAY['Zrotdirec'])

'''

OBJECT Style

            name, scandots, radius, color, run, step, steps, stepmax, stepvals, lineSize, intensity
L0 = LAYERobject("0", "saw", 100, 150, red, True, 0, 500, 200, [], 300, 255)

L0.name = name
L0.scandots = 100
L0.radius = 150
L0.color = red
L0.run = True
L0.step = 0, 
L0.steps = 500, 
L0.stepmax = 200
L0.stepvals =[]
L0.lineSize = 300
L0.intensity = 255


class LAYERobject:

    def __init__(self, name, scandots, radius, color, run, step, steps, stepmax, stepvals, lineSize, intensity)

        self.name = name
        self.scandots = scandots
        self.radius = radius
        self.color = color
        self.run = run
        self.step = step 
        self.steps = steps 
        self.stepmax = stepmax
        self.stepvals = stepvals
        self.lineSize = lineSize
        self.intensity = intensity




    name, coord, rotspeed, ranspeed, transmax
X0 = COORDobject("X0",0, 0, 0, 0)

X0.name = "0"
X0.coord = 0
X0.rotspeed = 0
X0.transpeed = 0
X0.transmax = 0

class COORDobject:

    def __init__(self, name, coord, rotspeed, ranspeed, transmax)

        self.name = name
        self.coord =  coord,
        self.rotspeed = rotspeed
        self.transpeed = transpeed
        self.transmax = transmax


#
# OLD STUFF not used
#


def AudioLissa():
    global Xrot, Yrot, Zrot

    levels = lj.fromRedis('/audiogen/levels')
    # levels = r.get('/audiogen/levels')
    #PL = 0
    dots = []
    amp = 200
    nb_point = 60

    Xrot += Xacc * 25
    Yrot += Yacc * 25
    Zrot += Zacc * 0

    # scale = (380-viewgenbands2scrY(levels[0]))/300
    #scale = (380 - (levels[0] * 4))/300
    LissaObj.scale = float(levels[0]) / 55
    print(type(float(levels[0])),levels[0], LissaObj.scale)
    #print ("scale",scale)
    #print ("scale",scale)

    for t in range(0, nb_point+1):
        y = 1 - amp*math.sin(2*math.pi*2*(float(t)/float(nb_point)))
        x = 1 - amp*math.cos(2*math.pi*3*(float(t)/float(nb_point))) 
        #y = 1 - amp*math.sin(2*PI*cc2range(gstt.cc[5],0,24)*(float(t)/float(nb_point)))
        #x = 1 - amp*math.cos(2*PI*cc2range(gstt.cc[6],0,24)*(float(t)/float(nb_point))) 

        dots.append((x,y))

    # These points are generated in pygame coordinates space (0,0 is top left) defined by screen_size in globalVars.py
    #lj23.PolyLineOneColor( dots, c = white, PL = PL, closed = False )
    lj.rPolyLineOneColor(dots, c = LissaObj.color, PL = LissaObj.PL, closed = False , xpos = LissaObj.xpos, ypos = LissaObj.ypos, scale = LissaObj.scale, rotx = LissaObj.rotx, roty = LissaObj.roty , rotz = LissaObj.rotz)
    



# /X/0/coord
# /Layer/0/color


if path.find('/X') == 0:
        command = path.split("/")
        eval(command[0]+'['+str(command[1])+']['+command[2]+']='+args[0])



# increase/decrease a CC. Value can be positive or negative
def changeCC(value, path):

    MaxwellCC = FindCC(path)

    print(MaxwellCC, "CC :", FindCC(path),"was", gstt.ccs[gstt.lasernumber][MaxwellCC])
    if gstt.ccs[gstt.lasernumber][MaxwellCC] + value > 127:
        gstt.ccs[gstt.lasernumber][MaxwellCC] = 127
    if gstt.ccs[gstt.lasernumber][MaxwellCC] + value < 0:
        gstt.ccs[gstt.lasernumber][MaxwellCC] = 0
    if gstt.ccs[gstt.lasernumber][MaxwellCC] + value < 127 and gstt.ccs[gstt.lasernumber][MaxwellCC] + value >0:
        gstt.ccs[gstt.lasernumber][MaxwellCC] += value

    print("maxwellccs changeCC in maxwellccs : path =", path, "CC :", FindCC(path), "is now ", gstt.ccs[gstt.lasernumber][MaxwellCC], "for laser", gstt.lasernumber)
    cc(MaxwellCC, gstt.ccs[gstt.lasernumber][MaxwellCC] , dest ='to Maxwell 1')
    


def EncoderPlusOne(value, path =  current["path"]):
    if value < 50:
        changeCC(1, path)

def EncoderMinusOne(value, path =  current["path"]):
    if value > 90:
        changeCC(-1, path)


def EncoderPlusTen(value, path =  current["path"]):
    if value < 50:
        changeCC(10, path)

def EncoderMinusTen(value, path =  current["path"]):
    if value > 90:
        changeCC(-10, path)


'''
