# coding=UTF-8
'''

LJ Global state
v0.8.0

**
Almost all values here Will be overriden by data in LJ.conf at startup
**

LICENCE : CC BY
by Sam Neurohack, Loloster, pclf
from /team/laser

'''

#ConfigName = "setexample.conf"
ConfigName = "LJ.conf"

debug = 0
ljpath=''

anims= [[],[],[],[]]

# How many lasers are connected. Different that "currentlaser" and "dacnumber" (=autodetected)
LaserNumber = -1

# What laser client to listen at launch
SceneNumber = 0
MaxScenes = 3

screen_size = [400,400]
xy_center = [screen_size[0]/2,screen_size[1]/2]

LjayServerIP = '192.168.1.13'
oscIPin = '192.168.1.15'
nozoscip = '192.168.1.15'
wwwIP = '192.168.1.15'

# gstt.Laser select to what laser modifcation will occur.
# Can be changed with /noteon 16-23
Laser = 0

# gstt.simuPL select what point list number to display in webUI simulator
# Can be changed with /noteon 24-31
simuPL = 1

# gstt.laserIPS. 
lasersIPS = ['192.168.1.5','192.168.1.6','192.168.1.3','192.168.1.4']

maxdacs = 4

# Autodetected by DAChecks() in main3 :
# Store connected dacs. Maybe laser 1 in LJ.conf is not connected but Laser 2 is. 
dacs = [-1, -1, -1, -1]
# Actual number of connected DACs
dacnumber = 0

# gstt.kpps stores kpps for each laser.
# ** Will be overridden by LJ.conf file values **
kpps = [25000,25000,25000,25000]
lasertype = ["LOCAL","LOCAL","LOCAL","LOCAL"] 
intensity = [-1,-1,-1,-1]


# gstt.GridDisplay : if = 1 Curve points actually sent to PL are replaced by a grid
GridDisplay = [0,0,0,0]

# Transformation Matrix for each laser 
EDH = [[], [], [], []]

# Etherdreams reports 
# ipconn is initial newdac to its etherdream
lstt_ipconn = [[-1], [-1], [-1], [-1]]
# dacstt is dac light engine state
lstt_dacstt = [[-1], [-1], [-1], [-1]]
# store last dac answers : ACK, not ACK,... 
lstt_dacanswers = [[-1], [-1], [-1], [-1]]
# store last number of points sent to etherdreams buffer 
lstt_points = [[0], [0], [0], [0]]

swapX = [1,1,1,-1]
swapY = [1,1,1,-1]

lsteps = [[],[],[],[]]

# For glitch art : change position and number of points added by tracer.py
# shortline is for distance with next point, shorter than 4000 (in etherdream coordinates) 
# i.e (0.25,3) means add 3 points at 25% on the line.
stepshortline = [(1.0, 8)]
stepslongline = [(0.25, 3), (0.75, 3), (1.0, 10)]

#stepslongline = [(0.25,1), (0.75, 1), (1.0, 1)]
#stepshortline = [(1.0, 8)]
#stepslongline = [(1.0, 1)]
#stepshortline = [(1.0, 1)]

point = [0,0,0]

cc = [0] * 256
lfo = [0] * 10
osc = [0] * 255
oscInUse = [0] * 255
knob = [0] * 33
# Viewer distance (cc 21)
cc[21]=60
viewer_distance = cc[21] * 8

# fov (cc 22) 
cc[22]= 60
fov = 4 * cc[22]


JumpFlag =0

# OSC ports
#temporaray fix hack : iport=nozoport
iport = 8002 # LJ input port
oport = 8001 # LJ output port
noziport=8003 #nozosc.py receiving commands port
nozoport=8001 #nozosc.py sending port to LJay (main.py)
nozuport=0 #linux serial usb port connecting nozoid devices ACM0 by default


angleX = 0 
angleY = 0
angleZ = 0

# multilasers arrays
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

BeatstepLayer = 1
BeatstepLayers = ['XY','Live',"Align","Zregulators"]

TouchOSCPort = 8101
TouchOSCIP = '192.168.2.67' 	# iPad 1
#TouchOSCIP = '192.168.2.156' 	# iPad mini
#TouchOSCIP = '192.168.43.146' 	# iPad mini @ fuzz
#TouchOSCIP = '192.168.151.213' # CCN
#TouchOSCIP = '127.0.0.1'		# Localhost
