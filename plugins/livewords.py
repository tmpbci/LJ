# coding=UTF-8

'''
Live words on different lasers
LICENCE : CC
'''

import redis
import lj3
import sys,time
import argparse

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
#from osc4py3 import oscmethod as osm
from osc4py3.oscmethod import * 

myIP = "127.0.0.1"

duration = 300

OSCinPort = 8006

Word0 = "LASER"
Word1 = "LASER"
Word2 = "LASER"
Word3 = "LASER"

'''
is_py2 = sys.version[0] == '2'
if is_py2:
	from Queue import Queue
else:
	from queue import Queue
'''
print ("Words is checking arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Text Cycling for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-m","--myIP",help="Local IP (127.0.0.1 by default) ",type=str)
argsparser.add_argument("-c","--client",help="LJ client number (0 by default)",type=int)
argsparser.add_argument("-v","--verbose",help="Verbosity level (0 by default)",type=int)

args = argsparser.parse_args()


if args.client:
	ljclient = args.client
else:
	ljclient = 0

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


if args.verbose:
	debug = args.verbose
else:
	debug = 0


lj3.Config(redisIP,ljclient)
#r = redis.StrictRedis(host=redisIP, port=6379, db=0)


def OSCword0(value):
	global Word0

	# Will receive message address, and message data flattened in s, x, y
	print("Words 0 got /words/text/0 with value", value)
	Word0 = value

def OSCword1(value):
	global Word1

	# Will receive message address, and message data flattened in s, x, y
	print("Words 1 got /words/text/1 with value", value)
	Word1 = value

def OSCword2(value):
	global Word2

	# Will receive message address, and message data flattened in s, x, y
	print("Words 2 got /words/text/2 with value", value)
	Word2 = value

def OSCword3(value):
	global Word3

	# Will receive message address, and message data flattened in s, x, y
	print("Words 3 got /words/text/3 with value", value)
	Word3 = value

def OSCljclient(value):
	# Will receive message address, and message data flattened in s, x, y
	print("Words got /words/ljclient with value", value)
	lj3.WebStatus("Words to virtual "+ str(value))
	ljclient = value
	lj3.LjClient(ljclient)



# /ping
def OSCping():

	lj3.OSCping("words")
	lj3.SendLJ("words/text/0",Word0)
	lj3.SendLJ("words/text/1",Word1)

# /quit
def OSCquit():

	lj3.OSCquit("words")


def Run():

	# OSC Server callbacks
	print("Words starting its OSC server at", myIP, "port",OSCinPort,"...")
	osc_startup()
	osc_udp_server(myIP, OSCinPort, "InPort")
	osc_method("/words/text/0*", OSCword0)
	osc_method("/words/text/1*", OSCword1)
	osc_method("/words/text/2*", OSCword2)
	osc_method("/words/text/3*", OSCword3)
	osc_method("/ping*", OSCping)
	osc_method("/words/ljclient*", OSCljclient)
	osc_method("/quit", OSCquit)

	color = lj3.rgb2int(255,255,255)
	lj3.WebStatus("Loading Words...")
	lj3.WebStatus("Words ready.")
	lj3.SendLJ("/words/start 1")
	
	lj3.SendLJ("words/text/0",Word0)
	lj3.SendLJ("words/text/1",Word1)

	try:

		while 1:
		
			lj3.OSCframe()
	
			lj3.Text(Word0, color, PL = 0, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			lj3.DrawPL(0)
	
			lj3.Text(Word1, color, PL = 1, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			lj3.DrawPL(1)
	
			lj3.Text(Word2, color, PL = 2, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			lj3.DrawPL(2)
	
			lj3.Text(Word3, color, PL = 3, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			lj3.DrawPL(3)
	
			time.sleep(0.01)

	except KeyboardInterrupt:
		pass

	# Gently stop on CTRL C

	finally:

		lj3.WebStatus("Words Exit")
		print("Stopping Words OSC...")
		lj3.OSCstop()

	print ("Words Stopped.")


Run()


