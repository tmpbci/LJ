# coding=UTF-8

'''
Multi Laser planetarium in python3 for LJ.
v0.01
Sam Neurohack

Accuracy tested against apparent data and starchart at https://www.calsky.com/cs.cgi?cha=7&sec=3&sub=2
Remember to set the same observer position and time. 

See Readme for more information


Todo:

- Validate aa2radec() with online calculator. Rewrite it to remove need for Astropy.
- Findout how to use OSC in python 3.
- Code WebUI page.
- UpdateStars() in each laser sky. Get magnitude. See UpdateSolar for example.
- All Draw operations should also check visibility in the given laser altitude range.
- Rewrite CityPosition() with proper search in a python dictionnary.
- Better python code. Better varuable to understand easily Update() methods. 

LICENCE : CC
Remember : LJ will automatically warp geometry according to alignement data. See webUI.  
'''

import redis
import lj3
import numpy as np
import math,time

from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy import units as u
from astropy.time import Time

from skyfield.api import Star, load, Topos,Angle
from skyfield.data import hipparcos

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
from osc4py3 import oscmethod as osm


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
argsparser.add_argument("-d","--debug",help="Verbosity level (0 by default)",type=int)
argsparser.add_argument("-i","--input",help="inputs OSC Port (8005 by default)",type=int)
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

if args.debug:
	debug = args.laser
else:
	debug = 0

if args.input:
	OSCinPort = args.input
else:
	OSCinPort = 8005

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
width = 750
height = 750
centerX = width / 2
centerY = height / 2

samparray = [0] * 100


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
 (planets, hipparcos,..). Then get only those objects in AltAz coordinates.
 aa2radec use Astropy to compute Equatorial Right Ascension and Declinaison coordinates from given observator Altitude and Azimuth.
 Example ra,dec = aa2radec( azimuth =  0, altitude = 90, lati = 48.85341, longi = 2.3488, elevation = 100, t =AstroPyNow )
 with AstroPyNow = Time.now()
'''
def aa2radec(azimuth, altitude, t):

    #AstrObserver = EarthLocation(lat=lati * u.deg, lon=longi *u.deg, height= elevation*u.m,)
    ObjectCoord = SkyCoord(alt = altitude * u.deg, az = azimuth *u.deg, obstime = t, frame = 'altaz', location = AstrObserver)
    #print("icrs",ObjectCoord.icrs)
    #print("ICRS Right Ascension", ObjectCoord.icrs.ra)
    #print("ICRS Declination", ObjectCoord.icrs.dec)
    return ObjectCoord.icrs.ra.degree, ObjectCoord.icrs.dec.degree



# Use Skyfield to compute given object apparent positions (ra,dec,alt,az) and distance from given gps earth position (in decimal degrees) at UTC time (in skyfield format)
def EarthObjPosition(object, t):


    #print (object, 'at', t.utc_iso())
    #SkyObserver = earth + Topos(gpslat, gpslong)
    astrometric = earth.at(t).observe(object)
    ra, dec, distance = astrometric.radec()
    '''
    print("Right ascencion",ra)
    print("RA in degree",ra._degrees)
    print("RA in radians",ra.radians)
    print("declinaison",dec)
    print (distance)
    '''
    ApparentPosition = SkyObserver.at(t).observe(object).apparent()
    #alt, az, distance = ApparentPosition.altaz('standard')
    alt, az, distance = ApparentPosition.altaz()
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
    # If you want degree hours min : print (object,alt,az)
    # or you can do return ra._degrees, dec, alt.degrees, az, distance
    return alt.degrees, az.degrees, distance


# Add Radec coordinates for all lasers from user defined Altaz coordinates in LaserSkies variable at given earth position and time.
# LaserSkies : [LeftAzi, RightAzi, TopAlt, BotAlt, LeftRa, RightRa, TopDec, BottomDec]
#                 0          1       2       3       4        5       6        7
def RadecSkies(LaserSkies, AstroSkyTime):

	print()
	print("Converting", lasernumber, "LaserSkies limits in Right Ascension & Declination (radec) coordinates ")
	for laser in range(lasernumber):
		if debug > 0:
			print("Laser",laser)
		# Left top point
		LaserSkies[laser][4],LaserSkies[laser][6] = aa2radec(azimuth = LaserSkies[laser][0], altitude =LaserSkies[laser][2], t =AstroSkyTime)
		if debug > 0:
		 print(LaserSkies[laser][4],LaserSkies[laser][6])
		# Right Bottom point
		LaserSkies[laser][5],LaserSkies[laser][7] = aa2radec(azimuth = LaserSkies[laser][1], altitude =LaserSkies[laser][3], t =AstroSkyTime)
		if debug > 0:
			print(LaserSkies[laser][5],LaserSkies[laser][7])
	if debug > 0:
		print(LaserSkies)
	print ("Done.")


def azimuth2scrX(leftAzi,rightAzi,s):

    a1, a2 = leftAzi, rightAzi  
    b1, b2 = 0, width
    #if debug > 0:
    #    print(leftAzi, rightAzi, s, b1 + ((s - a1) * (b2 - b1) / (a2 - a1)))
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

	

def altitude2scrY(topAlti,botAlti,s):
    a1, a2 = topAlti, botAlti  
    b1, b2 = 0, height
    #if debug > 0:
    #	print(topAlti,botAlti,s,  b1 + ((s - a1) * (b2 - b1) / (a2 - a1)))
    return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


  
#
# Solar System 
#

SolarObjectShape = [(-50,30), (-30,-30), (30,-30), (10,30), (-50,30)]

# Planets Radius in km
SolarObjectradius = [
    ('Sun', 695500.0),
    ('Mercury', 2440.0),
    ('Venus', 6051.8),
    ('Earth', 6371.01),
    ('Mars', 3389.9),
    ('Jupiter', 69911.0),
    ('Saturn', 58232.0),
    ('Uranus', 25362.0),
    ('Neptune', 24624.0),
    ('134340 Pluto', 1195.0),
    ]

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

	# Compute Alt Az coordinates for all solar objects for obsehttps://www.startpage.com/do/searchrver.
	for number,object in enumerate(SolarObjects):
		
		#print(object[0],number)
		SolarObjects[number][1], SolarObjects[number][2], distance = EarthObjPosition(planets[object[0]],SkyfieldTime)
	if debug > 0:
		PrintSolar()
	

def PrintSolar():

	for number,object in enumerate(SolarObjects):
		print (SolarObjects[number][0],"is at (alt,az)",SolarObjects[number][1],SolarObjects[number][2])


# Draw the SolarShapeObject for any Solar object is in the laser Sky
def DrawSolar(laser):

	for number,object in enumerate(SolarObjects):

		# Solar object is in given laser sky azimuth and altitude range ?
		if LaserSkies[laser][0] < SolarObjects[number][2] <  LaserSkies[laser][1] and LaserSkies[laser][3] < SolarObjects[number][1] <  LaserSkies[laser][2]:
			#print ("drawing",SolarObjects[number][0],SolarObjects[number][1],SolarObjects[number][2],"on laser",laser)
			lj3.rPolyLineOneColor(SolarObjectShape, c = white, PL = laser, closed = False, xpos = azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],SolarObjects[number][2]), ypos = altitude2scrY(LaserSkies[laser][2],LaserSkies[laser][3],SolarObjects[number][1]), resize = 2, rotx =0, roty =0 , rotz=0)




# 
# Stars 
#

StarsObjectShape = [(-50,30), (-30,-30), (30,-30), (10,30), (-50,30)]

def LoadHipparcos(ts):
	global hipdata

	print("Loading hipparcos catalog...")
	#hipparcosURL =  'ftp://cdsarc.u-strasbg.fr/cats/I/239/hip_main.dat.gz' 
	hipparcosURL = 'data/hip_main.dat.gz'
	with load.open(hipparcosURL) as f:
	    hipdata = hipparcos.load_dataframe(f)
	#print("Loaded.")
	hipparcos_epoch = ts.tt(1991.25)


# CODE IMPORTED HERE FROM TESTS. NEEDS TO ADAPT
# Star selection 
def StarSelect():
	global StarsObjects, hipdatafilt

	StarsObjects = [[]]
	#hipparcos_epoch = ts.tt(1991.25)
	#barnards_star = Star.from_dataframe(hipdata.loc[87937])
	#polaris =  Star.from_dataframe(hipdata.loc[11767])
	print()
	print ("Stars selection...")

	hipdatafilt = hipdata[hipdata['magnitude'] <= 3.5]
	print(('{} stars with magnitude <= 3.5'.format(len(hipdatafilt))))
	Starnames = hipdatafilt.index

	StarsObjects[0] = [Starnames[0],0,0]
	for index in range(len(Starnames)-1):
		StarsObjects.append([Starnames[index+1],0,0])


def UpdateStars(ts):
	global StarsObjects

	hipparcos_epoch = ts.tt(1991.25)
	# Compute Alt Az coordinates for all solar objects for obsehttps://www.startpage.com/do/searchrver.
	for number,object in enumerate(StarsObjects):
		
		#print(object[0],number)
		StarsObjects[number][1], StarsObjects[number][2], distance = EarthObjPosition(Star.from_dataframe(hipdatafilt.loc[StarsObjects[number][0]]),SkyfieldTime)
	
	if debug > 0:
		PrintStars()

def PrintStars():

	for number,object in enumerate(StarsObjects):
		print (StarsObjects[number][0],"is at (alt,az)",StarsObjects[number][1],StarsObjects[number][2])

def DrawStars(laser):

	for number,object in enumerate(StarsObjects):

		# Star object is in given lasersky altitude range ?
		if LaserSkies[laser][3] < StarsObjects[number][1] <  LaserSkies[laser][2]:
		
			# Star object is in given lasersky azimuth range ?
			if LaserSkies[laser][0] < StarsObjects[number][2] <  LaserSkies[laser][1] :

				#print ("drawing",StarsObjects[number][0],StarsObjects[number][1],StarsObjects[number][2],"on laser",laser)
				lj3.rPolyLineOneColor(StarsObjectShape, c = white, PL = laser, closed = False, xpos = azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],StarsObjects[number][2]), ypos = altitude2scrY(LaserSkies[laser][2],LaserSkies[laser][3],StarsObjects[number][1]), resize = 0.05, rotx =0, roty =0 , rotz=0)
			
			# Star object is in given lasersky North azimuth ?
			if LaserSkies[laser][0] >  LaserSkies[laser][1] and StarsObjects[number][2] < LaserSkies[laser][1] :

				#print ("drawing",StarsObjects[number][0],StarsObjects[number][1],StarsObjects[number][2],"on laser",laser)
				lj3.rPolyLineOneColor(StarsObjectShape, c = white, PL = laser, closed = False, xpos = azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],StarsObjects[number][2]), ypos = altitude2scrY(LaserSkies[laser][2],LaserSkies[laser][3],StarsObjects[number][1]), resize = 0.05, rotx =0, roty =0 , rotz=0)




#
# Anything system. Say you want 
#

AnythingObjectShape = [(-50,30), (-30,-30), (30,-30), (10,30), (-50,30)]

def LoadAnything():
	global planets, AnythingObjects, earth

	print("Loading Anything System...")
	# de421.bps https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp
	# planets = load('data/de421.bsp')
	earth = planets['earth']
	print('Loaded.')

	# [Object name, object altitude, object azimuth]
	AnythingObjects = [['MERCURY',0.0, 0.0], ['VENUS', 0.0, 0.0], ['JUPITER BARYCENTER', 0.0, 0.0], ['SATURN BARYCENTER', 0.0, 0.0], ['URANUS BARYCENTER', 0.0, 0.0], ['NEPTUNE BARYCENTER', 0.0, 0.0], ['PLUTO BARYCENTER', 0.0, 0.0], ['SUN', 0.0, 0.0], ['MOON', 0.0, 0.0], ['MARS', 0.0, 0.0]]

def UpdateAnything():
	global AnythingObjects

	# Compute Alt Az coordinates for all Anything objects for obsehttps://www.startpage.com/do/searchrver.
	for number,object in enumerate(AnythingObjects):
		
		#print(object[0],number)
		AnythingObjects[number][1], AnythingObjects[number][2], distance = EarthObjPosition(planets[object[0]],SkyfieldTime)
	if debug > 0:
		PrintAnything()
	

def PrintAnything():

	for number,object in enumerate(AnythingObjects):
		print (AnythingObjects[number][0],"is at (alt,az)",AnythingObjects[number][1],AnythingObjects[number][2])


# Draw the AnythingShapeObject for any Anything object is in the laser Sky
def DrawAnything(laser):

	for number,object in enumerate(AnythingObjects):

		# Anything object is in given laser sky azimuth and altitude range ?
		if LaserSkies[laser][0] < AnythingObjects[number][2] <  LaserSkies[laser][1] and LaserSkies[laser][3] < AnythingObjects[number][1] <  LaserSkies[laser][2]:
			#print ("drawing",AnythingObjects[number][0],AnythingObjects[number][1],AnythingObjects[number][2],"on laser",laser)
			lj3.rPolyLineOneColor(AnythingObjectShape, c = white, PL = laser, closed = False, xpos = azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],AnythingObjects[number][2]), ypos = altitude2scrY(LaserSkies[laser][2],LaserSkies[laser][3],AnythingObjects[number][1]), resize = 2, rotx =0, roty =0 , rotz=0)






# 
# On Earth Gps positions 
# from https://github.com/lutangar/cities.json
# 
def LoadCities():
	global world

	print("Loading World Cities GPS position...")
	f=open("data/cities.json","r")
	s = f.read()
	world = json.loads(s)
	#print("Loaded.")


# Get longitude and latitude of given City in given country. Need to better understand python dictionnaries. 
def CityPositiion(cityname, countrycode):

	for city in range(len(world['cities'])):
		if world['cities'][city]['name']==cityname and world['cities'][city]['country']==countrycode:
			'''
			print (world['cities'][city]['country'])
			print (world['cities'][city]['name'])
			print (world['cities'][city]['lat'])
			print (world['cities'][city]['lng'])
			'''
			return float(world['cities'][city]['lat']), float(world['cities'][city]['lng'])




# Add Kompass orientation to given laser point list if it is in laser sky at Y axis 300
# point lasers to
def DrawOrientation(laser):

	#print("LaserSkies 0",LaserSkies[laser][0],"LaserSkies 1",LaserSkies[laser][1])
	# North direction is in given laser sky azimuth range?
	if LaserSkies[laser][1] <  LaserSkies[laser][0]:
		#print ("N az",azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],0))
		lj3.Text("NORTH",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],359), 770, resize = 0.5, rotx =0, roty =0 , rotz=0)


	# East direction is in given laser sky azimuth range ?
	if LaserSkies[laser][0] <= 90 < LaserSkies[laser][1]:	
		#print ("E az",azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],0))
		lj3.Text("EAST",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],90), 770, resize = 0.5, rotx =0, roty =0 , rotz=0)

	# South direction is in given laser sky azimuth range ?
	if LaserSkies[laser][0] <= 180 <  LaserSkies[laser][1]:
		#print ("S az",azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],0))
		lj3.Text("SOUTH",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],180), 770, resize = 0.5, rotx =0, roty =0 , rotz=0)

	# West direction is in given laser sky azimuth range ?
	if LaserSkies[laser][0] <= 270 < LaserSkies[laser][1]:
		#print ("W az",azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],0))
		lj3.Text("WEST",white,laser,azimuth2scrX(LaserSkies[laser][0],LaserSkies[laser][1],270), 770, resize = 0.5, rotx =0, roty =0 , rotz=0)




# Compute LaserSkies Coordinates for observer
def InitObserver(SkyCity, SkyCountryCode, time,ts):
	global LaserSkies, Skylat, Skylong, SkyfieldTime, AstrObserver, SkyObserver
	
	# Observer position i.e : Paris FR
	#Skylat = 48.85341  		# decimal degree
	#Skylong = 2.3488			# decimal degree
	#print()
	print("Observer GPS position and time...")
	Skylat, Skylong = CityPositiion(SkyCity,SkyCountryCode)
	print ("GPS Position of",SkyCity, "in", SkyCountryCode, ":",Skylat,Skylong)
	# City GPS altitude not in Cities database... Let's say it's :
	Skyelevation = 0			# meters

	# Observer Time : Now
	# Other time in Astropy style 
	# times = '1999-01-01T00:00:00.123456789'
	# t = Time(times, format='isot', scale='utc')
	#print()
	AstroSkyTime = time
	print ("AstroPy time", AstroSkyTime)
	SkyfieldTime = ts.from_astropy(AstroSkyTime)
	print("SkyfieldTime from AstropyUTC",SkyfieldTime.utc_iso())

	AstrObserver = EarthLocation(lat = Skylat * u.deg, lon = Skylong * u.deg, height = Skyelevation * u.m,)
	SkyObserver = earth + Topos(Skylat, Skylong)


	# Computer for all Laser "skies" their Right Ascension/Declinaison coordinates from their Altitude/azimuth Coordinates.
	# to later select their visible objects in radec catalogs like hipparcos. 
	# LaserSky definition for one laser (in decimal degrees) : [RightAzi, LeftAzi, TopAlt, BotAlt, LeftRa, RightRa, TopDec, BottomDec]
	# With 4 lasers with each one a quarter of the 360 ° real sky, there is 4 LaserSky :
	LaserSkies = [[45,135.0,90.0,0.0,0.0,0.0,0.0,0.0],[135,225,90,0,0,0,0,0],[225,315,90,0,0,0,0,0],[305,0,90,0,0,0,0,0]]
	RadecSkies(LaserSkies, AstroSkyTime)


def NewTime(timeshift):

	 SkyfieldTime += timeshift

	 if DisplaySolar:
	 	UpdateSolar()
	 if DisplayStars:
	 	UpdateStars()
	 if DisplayAnything:
	 	UpdateAnything()


#def handlerfunction(s, x, y):
    # Will receive message data unpacked in s, x, y
#    pass

def OSChandler(address, s, x, y):
    # Will receive message address, and message data flattened in s, x, y
    print("Planetarium OSC server got address", address,"s",s,"x",x,"y",y)
    pass



def WebStatus(message):
	lj3.Send("/status",message)


#
# Main part 
#
	
try:

	lj3.OSCstart()
	# Make server channels to receive packets.
	#osc_udp_server("127.0.0.1", 3721, "localhost")
	osc_udp_server("0.0.0.0", OSCinPort, "InPort")
	
	# Associate Python functions with message address patterns, using default
	# argument scheme OSCARG_DATAUNPACK.
	#osc_method("/planet/*", handlerfunction)
	# Too, but request the message address pattern before in argscheme
	osc_method("/planet/*", OSChandler, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATAUNPACK)

	ts = load.timescale()
	LoadCities()
	SkyCity = 'Paris'
	SkyCountryCode = 'FR'
	LoadSolar()
	InitObserver(SkyCity, SkyCountryCode, Time.now(),ts)

	
	LoadHipparcos(ts)


	StarSelect()

	#print()
	#print ("Updating Sky Objects for current observer...")
	#print()
	print("Updating solar system (de421) objects position for observer at", Skylat, Skylong, "time", SkyfieldTime.utc_iso())
	UpdateSolar()
	#print ("Done.")
	#print()
	print("Updating stars for observer at", Skylat, Skylong, "time", SkyfieldTime.utc_iso())
	UpdateStars(ts)
	print ("Done.")

	# UpdateStars()    Todo

	DisplayStars = True
	DisplaySolar = False
	DisplayOrientation = True
	DisplayAnything = False

	while 1:

		for laser in range(lasernumber):

			if DisplayOrientation:
				DrawOrientation(laser)
			if DisplaySolar:
				DrawSolar(laser)
			if DisplayStars:
				DrawStars(laser)
			if DisplayAnything:
				DrawAnything()

			lj3.DrawPL(laser)
			lj3.OSCframe()

		time.sleep(0.01)


except KeyboardInterrupt:
    pass

# Gently stop on CTRL C

finally:

	lj3.OSCstop()

print ("Fin du planetarium.")






