# coding=UTF-8

'''
Multi Laser planetarium in python3

Remember : LJ will automatically warp geometry according to alignement data. See webUI.  

Todo:

- Validate aa2radec() with online calculator. Rewrite it to remove need for Astropy.
- Findout how to use OSC in python 3.
- Code WebUI page.
- UpdateStars() in each laser sky. Get magnitude. See UpdateSolar for example.
- Draw operations should also check visibility in the given laser altitude range.
- Rewrite CityPosition() with proper search in a python dictionnary.
- Better python code. Better varuable to understand easily Update() methods. 

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

import json

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
#argsparser.add_argument("-n","--name",help="City Name of the observer",type=str)
#argsparser.add_argument("-r","--redisIP",help="Country code of the observer ",type=str)

args = argsparser.parse_args()


if args.client:
	ljclient = args.client
else:
	ljclient = 0

if args.laser:
	lasernumber = args.laser
else:
	lasernumber = 0

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
# All the coordinates base functions 
#

'''
 To minize number of sky objects coordinates conversion : Change planetarium FOV in Ra Dec to select objects 
 (planets, hipparcos,..). Then get those objects in AltAz coordinates.
 aa2radec compute Equatorial Right Ascension and Declinaison coordinates from given observator Altitude and Azimuth.
 Example ra,dec = aa2radec( azimuth =  0, altitude = 90, lati = 48.85341, longi = 2.3488, elevation = 100, t =AstroPyNow )
 with AstroPyNow = Time.now()
'''
def aa2radec(azimuth,altitude,lati,longi,elevation,t):
    #print ("az",azimuth,"alt",altitude,"lati",lati,"long",longi,"elev",elevation,"time",t)
    Observer = EarthLocation(lat=lati * u.deg, lon=longi *u.deg, height= elevation*u.m,)
    ObjectCoord = SkyCoord(alt = altitude * u.deg, az = azimuth *u.deg, obstime = t, frame = 'altaz', location = Observer)
    #print("icrs",ObjectCoord.icrs)
    #print("ICRS Right Ascension", ObjectCoord.icrs.ra)
    #print("ICRS Declination", ObjectCoord.icrs.dec)
    return ObjectCoord.icrs.ra.degree, ObjectCoord.icrs.dec.degree



# Compute given object apparent positions (ra,dec,alt,az) and distance from given gps earth position (in decimal degrees) at UTC time (in skyfield format)
def EarthObjPosition(gpslat,gpslong,object,t):


    #print (object, 'at', t.utc_iso())
    Observer = earth + Topos(gpslat, gpslong)
    astrometric = earth.at(t).observe(object)
    ra, dec, distance = astrometric.radec()
    '''
    print("Right ascencion",ra)
    print("RA in degree",ra._degrees)
    print("RA in radians",ra.radians)
    print("declinaison",dec)
    print (distance)
    '''
    ApparentPosition = Observer.at(t).observe(object).apparent()
    alt, az, distance = ApparentPosition.altaz('standard')
    '''
    print("UTC",t.utc_iso())
    print ("Altitude",alt)
    print("Altitude in radians",alt.radians)
    print("Altitude in degrees",alt.degrees)
    print("Altitude in dms",alt.dms(0))
    print("Altitude in signed_dms",alt.signed_dms(0))
    print("Azimuth", az.dstr())
    print ("Distance from position", distance)
    '''
    #return ra._degrees, dec, alt.degrees, az, distance
    return alt.degrees, az.degrees


# Add Radec coordinates for all lasers from user defined Altaz coordinates in LaserSkies variable at given earth position and time.
# LaserSkies : [LeftAzi, RightAzi, TopAlt, BotAlt, LeftRa, RightRa, TopDec, BottomDec]
#                 0          1       2       3       4        5       6        7
def RadecSkies(LaserSkies,Skylat,Skylong,Skyelevation,AstroSkyTime):

	print()
	print("Converting", lasernumber, "LaserSkies limits in Right Ascension & Declination (radec) coordinates ")
	for laser in range(lasernumber):
		# Left top point
		LaserSkies[laser][4],LaserSkies[laser][6] = aa2radec(azimuth = LaserSkies[laser][0], altitude =LaserSkies[laser][2], lati = Skylat, longi = Skylong, elevation = Skyelevation, t =AstroSkyTime)
		# Right Bottom point
		LaserSkies[laser][5],LaserSkies[laser][7] = aa2radec(azimuth = LaserSkies[laser][1], altitude =LaserSkies[laser][3], lati = Skylat, longi = Skylong, elevation = Skyelevation, t =AstroSkyTime)
	print(LaserSkies)
	print ("Done.")


def azimuth2scrX(leftAzi,rightAzi,s):
    a1, a2 = leftAzi,rightAzi  
    b1, b2 = -width/2, width/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

	

def altitude2scrY(topAlti,botAlti,s):
    a1, a2 = botAlti, topAlti  
    b1, b2 = -heigth/2, heigth/2
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))




#
# Solar System 
#


def LoadSolar():
	global planets, SolarObjects, earth

	print("Loading Solar System (de421)...")
	# de421.bps https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp
	planets = load('data/de421.bsp')
	earth = planets['earth']
	print('Loaded.')

	# de421 objects
	# [Object name, object altitude, object azimuth]
	SolarObjects = [['MERCURY',0.0, 0.0], ['VENUS', 0.0, 0.0], ['JUPITER BARYCENTER', 0.0, 0.0], ['SATURN BARYCENTER', 0.0, 0.0], ['URANUS BARYCENTER', 0.0, 0.0], ['NEPTUNE BARYCENTER', 0.0, 0.0], ['PLUTO BARYCENTER', 0.0, 0.0], ['SUN', 0.0, 0.0], ['MOON', 0.0, 0.0], ['MARS', 0.0, 0.0]]

def UpdateSolar():
	global SolarObjects

	print()
	print("Updating solar system (de421) objects position for observer at", Skylat, Skylong, "time", SkyfieldTime.utc_iso())
	# Compute Alt Az coordinates for all solar objects for observer.
	for number,object in enumerate(SolarObjects):
		
		#print(object[0],number)
		SolarObjects[number][1],SolarObjects[number][2] = EarthObjPosition(Skylat,Skylong,planets[object[0]],SkyfieldTime)
	print (SolarObjects)
	print ("Done.")

# Draw the SolarShapeObject for any Solar object is in the laser Sky
def DrawSolar(LaserSkies, laser):

	for number,object in enumerate(SolarObjects):

		# Solar object is in given laser sky aeimuth range ?
		# Need to add an altitude check.

		if LaserSkies[laser][0] < SolarObjects[number][2] <  LaserSkies[laser][1]:
			lj3.rPolyLineOneColor(SolarObjectShape, c = white, PL = laser, closed = False, xpos = azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],SolarObjects[number][2]), ypos = azimuth2scrY(LaserSkies[laser][2],LaserSkies[laser][3],SolarObjects[number][0]), resize = 2.5, rotx =0, roty =0 , rotz=0)




# 
# Stars Objects
#

def LoadHipparcos(ts):
	global hipdata

	print("Loading hipparcos catalog...")
	#hipparcosURL =  'ftp://cdsarc.u-strasbg.fr/cats/I/239/hip_main.dat.gz' 
	hipparcosURL = 'data/hip_main.dat.gz'
	with load.open(hipparcosURL) as f:
	    hipdata = hipparcos.load_dataframe(f)
	print("Loaded.")
	hipparcos_epoch = ts.tt(1991.25)


# CODE IMPORTED HERE FROM TESTS. NEEDS TO ADAPT
# Star selection 
def StarSelect():

	hipparcos_epoch = ts.tt(1991.25)
	barnards_star = Star.from_dataframe(hipdata.loc[87937])
	polaris =  Star.from_dataframe(hipdata.loc[11767])
	print()
	print ("Selecting sky portion")

	hipdatafilt = hipdata[hipdata['magnitude'] <= 2.5]
	print(('After filtering, there are {} stars with magnitude <= 2.5'.format(len(hipdatafilt))))
	bright_stars = Star.from_dataframe(hipdatafilt)
	print (hipdatafilt)
	#print (bright_stars)

	t = ts.utc(2018, 9, 3)

	'''
	Observer = earth + Topos(gpslat, gpslong)
	ApparentPosition = Observer.at(t).observe(bright_stars).apparent()
	alt, az, distance = ApparentPosition.altaz('standard')
	print(('Now there are {} azimuth'.format(len(az))))
	print(('and {} altitute'.format(len(alt))))
	'''
	
	astrometric = earth.at(t).observe(bright_stars)
	ra, dec, distance = astrometric.radec()
	print(('Now there are {} right ascensions'.format(len(ra.hours))))
	print(('and {} declinations'.format(len(dec.degrees))))
	
	Observer = earth + Topos(gpslat, gpslong)
	AP = Observer.at(t).observe(bright_stars)
	print ("AP",AP.apparent())




# WORK IN PROGRESS
# On Earth Gps positions 
# https://github.com/lutangar/cities.json.git
# 
def LoadCities():
	global cities

	print("Loading World Cities GPS position...")
	f=open("data/cities.json","r")
	s = f.read()
	cities = json.loads(s)
	print("Loaded.")


# search a city to get longitude and latitude. Need to understand python dictionnaries. 
def CityPositiion(cityname, countrycode):

	for city in range(len(cities['cities'])):
		if cities['cities'][city]['name']==cityname and cities['cities'][city]['country']==countrycode:
			'''
			print (cities['cities'][city]['country'])
			print (cities['cities'][city]['name'])
			print (cities['cities'][city]['lat'])
			print (cities['cities'][city]['lng'])
			'''
			return float(cities['cities'][city]['lat']), float(cities['cities'][city]['lng'])



	




# Add Kompass letter to given laser point list if it is in laser sky at Y axis 300
def DrawOrientation(LaserSkies, laser):

	# North direction is in given laser sky azimuth range?
	if LaserSkies[laser][0] < 0 <  LaserSkies[laser][1]:
		lj3.Text("N",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],0),300)

	# East direction is in given laser sky azimuth range ?
	if LaserSkies[laser][0] < 90 < LaserSkies[laser][1]:	
		lj3.Text("E",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],90),300)

	# South direction is in given laser sky azimuth range ?
	if LaserSkies[laser][0] < 180 <  LaserSkies[laser][1]:
		lj3.Text("S",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],180),300)

	# West direction is in given laser sky azimuth range ?
	if LaserSkies[laser][0] < 270 < LaserSkies[laser][1]:
		lj3.Text("W",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],270),300)




# Compute LaserSkies Coordinates
def UpdateObserver(SkyCity, SkyCountryCode, time,ts):
	global LaserSkies, Skylat, Skylong, SkyfieldTime
	
	# Observer position i.e : Paris FR
	#Skylat = 48.85341  		# decimal degree
	#Skylong = 2.3488			# decimal degree
	print()
	print("Observer GPS position and time...")
	Skylat, Skylong = CityPositiion(SkyCity,SkyCountryCode)
	print ("GPS Position of",SkyCity, "in", SkyCountryCode, ":",Skylat,Skylong)
	# City GPS altitude not in Cities database... Let's say it's :
	Skyelevation = 100			# meters

	# Observer Time : Now
	# Other time in Astropy style 
	# times = '1999-01-01T00:00:00.123456789'
	# t = Time(times, format='isot', scale='utc')
	print()
	AstroSkyTime = time
	print ("AstroPyNow", AstroSkyTime)
	SkyfieldTime = ts.from_astropy(AstroSkyTime)
	print("Time from AstropyUTC",SkyfieldTime.utc_iso())
	print("Skyfield UTC",SkyfieldTime.utc_iso())


	# Computer for all Laser "skies" their Right Ascension/Declinaison coordinates from their Altitude/azimuth Coordinates.
	# to later select their visible objects in radec catalogs like hipparcos. 
	# LaserSky definition for one laser (in decimal degrees) : [LeftAzi, RightAzi, TopAlt, BotAlt, LeftRa, RightRa, TopDec, BottomDec]
	# With 4 lasers with each one a quarter of the 360 ° real sky, there is 4 LaserSky :
	LaserSkies = [[0.0,90.0,90.0,0.0,0.0,0.0,0.0,0.0],[90,180,90,0,0,0,0,0],[180,270,90,0,0,0,0,0],[270,360,90,0,0,0,0,0]]
	RadecSkies(LaserSkies, Skylat, Skylong, Skyelevation, AstroSkyTime)



#
# Main functions
#


def Planetarium():

	ts = load.timescale()
	LoadHipparcos(ts)
	LoadSolar()
	LoadCities()

	SkyCity = 'Paris'
	SkyCountryCode = 'FR'
	UpdateObserver(SkyCity, SkyCountryCode, Time.now(),ts)

	print()
	print ("Updating Sky Objects for current observer...")

	UpdateSolar()
	# UpdateStars()    Todo

	DisplayStars = False
	DisplaySolar = True
	DisplayOrientation = True


	while 1:

		for laser in range(lasernumber):

			if DisplayOrientation:
				DrawOrientation(LaserSkies, laser)
			if DisplaySolar:
				DrawSolar()
			if DisplayStars:
				pass

			lj3.DrawPL(laser)
			time.sleep(0.01)



Planetarium()



