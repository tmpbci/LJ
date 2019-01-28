# coding=UTF-8

'''
Multi Laser planetarium in python3

Remember : LJ will automatically warp geometry according to alignement data. See webUI.  

LICENCE : CC
'''

#import redis
import lj3
import numpy as np
import math,time

from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy import units as u
from astropy.time import Time

from skyfield.api import Star, load, Topos,Angle
from skyfield.data import hipparcos


'''
is_py2 = sys.version[0] == '2'
if is_py2:
	from Queue import Queue
else:
	from queue import Queue
'''

#
# Arguments handler
#	

import argparse

print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Planetarium for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-l","--laser",help="Laser number to be displayed (0 by default)",type=int)

args = argsparser.parse_args()


if args.client:
	ljclient = args.client
else:
	ljclient = 0

if args.laser:
	plnumber = args.laser
else:
	plnumber = 0

# Redis Computer IP
if args.redisIP  != None:
	redisIP  = args.redisIP
else:
	redisIP = '127.0.0.1'

lj3.Config(redisIP,ljclient)

#
# Inits Laser
#

fov = 256
viewer_distance = 2.2
width = 450
height = 450
centerX = width / 2
centerY = height / 2

samparray = [0] * 100
# (x,y,color in integer) 65280 is color #00FF00 
# Green rectangular shape :
pl0 =  [(100,300,65280),(200,300,65280),(200,200,65280),(100,200,65280),(100,300,65280)]

# If you want to use rgb for color :
def rgb2int(r,g,b):
    return int('0x%02x%02x%02x' % (r,g,b),0)

white = rgb2int(255,255,255)
red = rgb2int(255,0,0)
blue = rgb2int(0,0,255)
green = rgb2int(0,255,0)


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
# Objects in Planetarium Field of View 
#

# Compute Equatorial Right Ascension and Declinaison from given observator Altitude and Azimuth
def aa2radec(azimuth,altitude,lati,longi,elevation,t):
    Observer = EarthLocation(lat=lati * u.deg, lon=longi *u.deg, height= elevation*u.m,)
    ObjectCoord = SkyCoord(alt = altitude * u.deg, az = azimuth *u.deg, obstime = t, frame = 'altaz', location = Observer)
    print("icrs",ObjectCoord.icrs)
    print("ICRS Right Ascension", ObjectCoord.icrs.ra)
    print("ICRS Declination", ObjectCoord.icrs.dec)
    return ObjectCoord.icrs.ra.degree, ObjectCoord.icrs.dec.degree


# Compute given object apparent positions (ra,dec,alt,az) and distance from given gps earth position  (in decimal degrees) at UTC time (in skyfield format)
def EarthObjPosition(gpslat,gpslong,object,t):

     Observer = earth + Topos(gpslat, gpslong)
     astrometric = earth.at(t).observe(object)
     ra, dec, distance = astrometric.radec()
     print("Right ascencion",ra)
     print("RA in degree",ra._degrees)
     print("RA in radians",ra.radians)
     print("declinaison",dec)
     print (distance)
     ApparentPosition = Observer.at(t).observe(object).apparent()
     alt, az, distance = ApparentPosition.altaz('standard')
     print("UTC",t.utc_iso())
     print ("Altitude",alt)
     print("Altitude in radians",alt.radians)
     print("Altitude in degrees",alt.degrees)
     print("Altitude in dms",alt.dms(0))
     print("Altitude in signed_dms",alt.signed_dms(0))
     print("Azimuth", az.dstr())
     print ("Distance from position", distance)
     return ra._degrees, dec, alt.degrees, az, distance

def azimuth2scrX(leftAzi,rightAzi,s):
    a1, a2 = leftAzi,rightAzi  
    b1, b2 = -width/2, width/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))
	
def altitude2scrY(topAlti,botAlti,s):
    a1, a2 = botAlti, topAlti  
    b1, b2 = -heigth/2, heigth/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))
	
print("Loading hipparcos catalog...")
#hipparcosURL =  'ftp://cdsarc.u-strasbg.fr/cats/I/239/hip_main.dat.gz' 
hipparcosURL = 'data/hip_main.dat.gz'
with load.open(hipparcosURL) as f:
    hipdata = hipparcos.load_dataframe(f)
print("Loaded")

# Sky objects
ts = load.timescale()
hipparcos_epoch = ts.tt(1991.25)
barnards_star = Star.from_dataframe(hipdata.loc[87937])
polaris =  Star.from_dataframe(hipdata.loc[11767])
# de421.bps https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp
planets = load('data/de421.bsp')
print('de421 loaded.')
earth = planets['earth']
mars = planets['mars']

# On Earth Gps positions 

# https://github.com/lutangar/cities.json.git

#
# Main functions
#


def DrawPL():

	Shape = []
	counter =0

	while 1:
		t = ts.now()

		gpslat = '48.866669 N'  
		gpslong = '2.33333 E'
		'''
		for curve in np.arange(-1, 1, 0.2): 
			zsine = ssine(100,5,curve+counter)

			zfactor = 7
			Shape = []
			x = curve
			#x = 0
			y = -1
			for step in zsine:
				Shape.append( Proj(x,y,step/zfactor,0,0,0))
				y += 0.02
			lj3.rPolyLineOneColor(Shape,  c = white,    PL = 0, closed = False, xpos = -450, ypos = -350, resize = 2.5, rotx =0, roty =0 , rotz=0)

		lj3.DrawPL(0)
		'''
		counter += 0.001
		time.sleep(0.01)
print("Running...")
DrawPL()