# coding=UTF-8

'''

LJ v0.8.1

Cycling text on one LJ laser.
LICENCE : CC

'''
import sys,time
sys.path.append('../libs')
import redis
import lj3

import argparse
import traceback

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
#from osc4py3 import oscmethod as osm
from osc4py3.oscmethod import * 

OSCinPort = 8007

duration = 300
lasertext = ["TEAMLASER","FANFAN","LOLOSTER","SAM"]

PL = 0

'''
is_py2 = sys.version[0] == '2'
if is_py2:
	from Queue import Queue
else:
	from queue import Queue
'''

print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Text Cycling for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-l","--laser",help="Laser number to be displayed (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)


args = argsparser.parse_args()


if args.client:
	ljclient = args.client
else:
	ljclient = 0

if args.laser:
	plnumber = args.laser
else:
	plnumber = 0

if args.verbose:
	debug = args.verbose
else:
	debug = 0

# Redis Computer IP
if args.redisIP  != None:
	redisIP  = args.redisIP
else:
	redisIP = '127.0.0.1'


# myIP
if args.myIP  != None:
	myIP  = args.myIP
else:
	myIP = '127.0.0.1'


lj3.Config(redisIP,ljclient,"cycl")
#r = redis.StrictRedis(host=redisIP, port=6379, db=0)

oscrun = True

# If you want to use rgb for color :
def rgb2int(r,g,b):
	return int('0x%02x%02x%02x' % (r,g,b),0)


def WebStatus(message):

	lj3.SendLJ("/status",message)

def OSCljclient(value):

	print("Cycl got /cycl/ljclient with value", value)
	lj3.WebStatus("Cycl to virtual "+ str(value))
	ljclient = value
	lj3.LjClient(ljclient)


def OSCpl(value):
	global PL

	print("Cycl got /cycl/pl with value", value)
	lj3.WebStatus("Cycl to pl "+ str(value))
	PL = int(value)
	lj3.LjPl(PL)


# /quit dummyvalue
def quit(value):
	global oscrun

	lj3.ClosePlugin()
	oscrun = False
	
'''
# /ping
def OSCping():

	lj3.OSCping("cycl")

'''

print("Cycl starting its OSC server at", myIP, "port",OSCinPort,"...")
osc_startup()
osc_udp_server(myIP, OSCinPort, "InPort")
osc_method("/ping*", lj3.OSCping)
osc_method("/quit", quit)
#osc_method("/ping*", OSCping)
#osc_method("/quit", OSCquit)
osc_method("/cycl/ljclient*", OSCljclient)
osc_method("/cycl/pl*", OSCpl)

WebStatus("Textcycl Ready")
lj3.SendLJ("/cycl/start 1")

def Run():

	counter =0
	step = 0
	timing = -1
	color = rgb2int(255,255,255)

	try:
		while oscrun:
		
			if timing == duration or timing == -1:
				message = lasertext[step]
				#print ('PL',PL)
				lj3.Text(message, color, PL = PL, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
				lj3.DrawPL(PL)
				timing = 0
	
			else:
				step += 1
				if step >3:
					step =0	
			timing += 1
			lj3.OSCframe()
			time.sleep(0.01)

	except Exception:
		traceback.print_exc()
	except KeyboardInterrupt:
		pass

	# Gently stop on CTRL C

	finally:

		quit()

Run()


