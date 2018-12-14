# coding=UTF-8
'''
Etat global (anciennement singleton de la classe GameState + autres VARIABLES nécessaires partout)"
'''

#from globalVars import *

#ConfigName = "setexample.conf"
ConfigName = "mainy.conf"

debug = 2

anims= [[],[],[],[]]

# How many lasers are connected. Different that "currentlaser" used by bhorosc
LaserNumber = 2
screen_size = [800,600]
xy_center = [screen_size[0]/2,screen_size[1]/2]

# Will be overriden by mainy.conf file data
LjayServerIP = '192.168.1.13'
oscIPin = '192.168.1.15'
nozoscip = '192.168.1.15'

# gstt.Laser select to what laser modifcation will occur.
# Can be changed with /noteon 16-23
Laser = 2

# gstt.simuPL select what point list number to display in pygame simulator
# Can be changed with /noteon 24-31
simuPL = 1

# gstt.laserIPS. Will be overridden by the ConfigName (see below) file values
lasersIPS = ['192.168.1.5','192.168.1.6','192.168.1.3','192.168.1.4']


# gstt.laserPLS : What point list is sent to what laser. 
# ** Will be overridden by the ConfigName (see below) file values **
lasersPLS = [0,1,2,0]


# gstt.kpps stores kpps for each laser.
# ** Will be overridden by the ConfigName (see below) file values **
kpps = [25000,25000,25000,25000]

# gstt.GridDisplay : if = 1 Curve points actually sent to PL are replaced by a grid
GridDisplay = [0,0,0,0]

# with 4 laser available, 4 PL only are necessary
PL = [[],[],[],[]]


# Transformation Matrix for each laser 
EDH = [[], [], [], []]

# Laser states
# ipconn is initial newdac to its etherdream
lstt_ipconn = [[-1], [-1], [-1], [-1]]
# dacstt is dac light engine state
lstt_dacstt = [[-1], [-1], [-1], [-1]]
# store last dac answers ACK, not ACK 
lstt_dacanswers = [[-1], [-1], [-1], [-1]]
# store last number of points sent to etherdreams buffer 
lstt_points = [[0], [0], [0], [0]]

swapX = [1,1,1,-1]
swapY = [1,1,1,-1]

maxCurvesByLaser = 4


# For glitch art : change position and decrease number of points added by newdac.py
# shortline for lines shorter than 4000 (in etherdream coordinates) 
# i.e (0.25,3) means add 3 points at 25% on the line.
stepshortline = [ (1.0, 8)]
stepslongline = [ (0.25, 3), (0.75, 3), (1.0, 10)]


#curveColor = [255,0,0] * maxCurvesByLaser
#curveColor = [[0 for _ in range(3)] for _ in range(maxCurvesByLaser)]
curveColor = [[255 for _ in range(3)] for _ in range(maxCurvesByLaser)]
colorX = [[255 for _ in range(3)] for _ in range(maxCurvesByLaser)]
colorY = [[255 for _ in range(3)] for _ in range(maxCurvesByLaser)]
offsetX = [0] * maxCurvesByLaser
offsetY = [0] * maxCurvesByLaser
curveNumber = 0
Curve = curveNumber
XTimeAxe=30000
YTimeAxe=30000

#curveX = [255,255,255] * maxCurvesByLaser
#curveY = [255,255,255] * maxCurvesByLaser

Mode = 5

point = [0,0,0]

# gstt.colormode select what to display. Can be changed with /noteon 57-64
colormode = 0
color = [255,255,255]
newcolor = 0

surpriseoff = 10
surpriseon = 50
surprisey = -10
surprisex = -10


cc = [0] * 256
lfo = [0] * 10
osc = [0] * 255
oscInUse = [0] * 255
knob = [0] * 33

stars0=[]
stars1=[]
stars2=[]
#stars3=[]
# Viewer distance (cc 21)
cc[21]=60
viewer_distance = cc[21] * 8

# fov (cc 22) 
cc[22]= 60
fov = 4 * cc[22]



'''
Also vailable with args : -v Value 

if debug = 1 you get :


if debug = 2 you get :
- dac errors

'''


JumpFlag =0


# nice X (cc 5) Y (cc 6) curve at first
cc[5] = cc[6] = 60

# Dot mode start at middle screen
cc[1] = cc[2] = 63

note = 0
velocity = 0

WingHere = -1
BhorealHere = -1
LaunchHere = -1
BhorLeds = [0] * 64

oscx = 0
oscy = 0
oscz = 0


# Ai Parameters

aivelocity = 0.5
aiexpressivity = 0.5
aisensibility = 0.5
aibeauty =  0.5


# OSC ports
#temporaray fix hack : iport=nozoport
iport = 8001 #LJay (bhorosc) input port
oport = 8002 #LJay (bhorosc) output port
noziport=8003 #nozosc.py receiving commands port
nozoport=8001 #nozosc.py sending port to LJay (main.py)
nozuport=0 #linux serial usb port connecting nozoid devices ACM0 by default


X = [0] * maxCurvesByLaser
Y = [0] * maxCurvesByLaser

# No rotation X (cc 29) Y (cc 30) Z (cc 31)  at first
cc[29] = cc[30] = cc[31] = prev_cc29 = 0
prev_cc29 = prev_cc30 = prev_cc31 = -1

angleX = 0 
angleY = 0
angleZ = 0

tomidi = False   # currently tomidi bypass all other directions
todmx = False
toled = False
tolaser = True
tosynth = False

sernozoid = ""
nozoid = ""
serdmx = ""
newnumber = ""
oldnumber = ""

'''
# will be overrided but settings.conf values.
# legacy one laser only values
centerx = LASER_CENTER_X
centery = LASER_CENTER_Y
zoomx = LASER_ZOOM_X
zoomy = LASER_ZOOM_Y
sizex = LASER_SIZE_X
sizey = LASER_SIZE_Y
finangle = LASER_ANGLE
'''

# multilasers arrays
# will be overrided but settings.conf values.
centerX = [0,0,0,0]
centerY = [0,0,0,0]
zoomX = [0,0,0,0]
zoomY = [0,0,0,0]
sizeX = [0,0,0,0]
sizeY = [0,0,0,0]
finANGLE = [0,0,0,0]

warpdest = [[[ 1. , 0. , 0.],[ 0. , 1. , 0.],[ 0. , 0. , 1.]],
[[ 1. , 0. , 0.],[ 0. , 1. , 0.],[ 0. , 0. , 1.]],
[[ 1. , 0. , 0.],[ 0. , 1. , 0.],[ 0. , 0. , 1.]],
[[ 1. , 0. , 0.],[ 0. , 1. , 0.],[ 0. , 0. , 1.]]
]

