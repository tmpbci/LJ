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


duration = 300

OSCinPort = 8006

Word0 = "0"
Word1 = "1"
Word2 = "2"
Word3 = "3"

'''
is_py2 = sys.version[0] == '2'
if is_py2:
	from Queue import Queue
else:
	from queue import Queue
'''
print ("")
print ("Arguments parsing if needed...")
argsparser = argparse.ArgumentParser(description="Text Cycling for LJ")
argsparser.add_argument("-r","--redisIP",help="IP of the Redis server used by LJ (127.0.0.1 by default) ",type=str)
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


if args.verbose:
	debug = args.verbose
else:
	debug = 0


lj3.Config(redisIP,ljclient)
#r = redis.StrictRedis(host=redisIP, port=6379, db=0)


def OSCword0(value):
	# Will receive message address, and message data flattened in s, x, y
	print("I got /words with value", value)
	Word0 = value

def OSCword1(value):
	# Will receive message address, and message data flattened in s, x, y
	print("I got /words with value", value)
	Word1 = value

def OSCword2(value):
	# Will receive message address, and message data flattened in s, x, y
	print("I got /words with value", value)
	Word3 = value

def OSCword3(value):
	# Will receive message address, and message data flattened in s, x, y
	print("I got /words with value", value)
	Word3 = value

def OSCljclient(value):
	# Will receive message address, and message data flattened in s, x, y
	print("I got /words/ljclient with value", value)
	ljclient = value
	lj3.LjClient(ljclient)


def WebStatus(message):
	lj3.Send("/status",message)



def Run():

	WebStatus("Load Words")

	# OSC Server callbacks
	print("Starting OSC at 127.0.0.1 port",OSCinPort,"...")
	osc_startup()
	osc_udp_server("127.0.0.1", OSCinPort, "InPort")
	osc_method("/words/0*", OSCword0)
	osc_method("/words/1*", OSCword1)
	osc_method("/words/2*", OSCword2)
	osc_method("/words/3*", OSCword3)
	osc_method("/ping*", lj3.OSCping)
	osc_method("/words/ljclient", OSCljclient)

	color = lj3.rgb2int(255,255,255)

	WebStatus("Words ready.")

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

		WebStatus("Words Exit")
		print("Stopping OSC...")
		lj3.OSCstop()

	print ("Words Stopped.")


Run()


