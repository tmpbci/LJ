# coding=UTF-8

'''
Live words on different lasers
LICENCE : CC
'''

import redis

import sys,time
import argparse

import os
ljpath = r'%s' % os.getcwd().replace('\\','/')
# import from shell
sys.path.append('../libs')

#import from LJ
sys.path.append(ljpath +'/libs/')
#print (ljpath+'/libs')
import lj23 as lj

is_py2 = sys.version[0] == '2'
if is_py2:
    from OSC import OSCServer, OSCClient, OSCMessage
    print ("Importing lj23 and OSC from libs...")
else:
    from OSC3 import OSCServer, OSCClient, OSCMessage
    print ("Importing lj23 and OSC3 from libs...")

myIP = "127.0.0.1"

duration = 300

OSCinPort = 8006
oscrun = True

Word0 = "BRAINFUCK"
Word1 = "D"
Word2 = "CAPTCHA"
Word3 = "D"


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


lj.Config(redisIP,ljclient,"words")
#r = redis.StrictRedis(host=redisIP, port=6379, db=0)

# 'Destination' for each PL 
#                  name, number, active, PL , scene, laser
# PL 0
Dest0 = lj.DestObject('0', 0, True, 0, 0, 0)
# PL 1
Dest1 = lj.DestObject('1', 1, True, 1, 0, 1)
# PL 2
Dest2 = lj.DestObject('2', 2, True, 2, 0, 2)
# PL 3
Dest3 = lj.DestObject('3', 3, True, 3, 0, 3)

#
# OSC
#

oscserver = OSCServer( (myIP, OSCinPort) )
oscserver.timeout = 0
#oscrun = True

# this method of reporting timeouts only works by convention
# that before calling handle_request() field .timed_out is 
# set to False
def handle_timeout(self):
	self.timed_out = True

# funny python's way to add a method to an instance of a class
import types
oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# RAW OSC Frame available ? 
def OSCframe():
	# clear timed_out flag
	#print "oscframe"
	oscserver.timed_out = False
	# handle all pending requests then return
	while not oscserver.timed_out:
		oscserver.handle_request()


# Stop osc server
def OSCstop():

	oscserver.close()



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
	lj.WebStatus("Words to virtual "+ str(value))
	ljclient = value
	lj.LjClient(ljclient)




# /quit dummyvalue
def quit(value):
	# don't do this at home (or it'll quit blender)
	global oscrun

	oscrun = False
	print("Stopped by /quit.")
	lj.ClosePlugin()


def Run():

	# OSC Server callbacks
	print("Words starting its OSC server at", myIP, "port",OSCinPort,"...")
	#oscserver.addMsgHandler( "default", lj.OSChandler )
	#oscserver.addMsgHandler( "/words/ljclient", OSCljclient )
	oscserver.addMsgHandler( "/words/text/0", OSCword0)
	oscserver.addMsgHandler( "/words/text/1", OSCword1)
	oscserver.addMsgHandler( "/words/text/2", OSCword2)
	oscserver.addMsgHandler( "/words/text/3", OSCword3)
	#oscserver.addMsgHandler( "/ping", lj.OSCping)
	#oscserver.addMsgHandler( "/quit", lj.OSCquit)
	# Add OSC generic plugins commands : 'default", /ping, /quit, /pluginame/obj, /pluginame/var, /pluginame/adddest, /pluginame/deldest
	lj.addOSCdefaults(oscserver)

	color = lj.rgb2int(0,255,0)
	lj.WebStatus("Loading Words...")
	lj.WebStatus("Words ready.")
	lj.SendLJ("/words/start 1")
	
	lj.SendLJ("words/text/0",Word0)
	lj.SendLJ("words/text/1",Word1)

	try:

		while lj.oscrun:
		
			OSCframe()
	
			lj.Text(Word0, color, PL = 0, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			#lj.DrawPL(0)
	
			lj.Text(Word1, color, PL = 1, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			#lj.DrawPL(1)
	
			lj.Text(Word2, color, PL = 2, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			#lj.DrawPL(2)
	
			lj.Text(Word3, color, PL = 3, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			#lj.DrawPL(3)
	
			lj.DrawDests()
			time.sleep(0.01)

	except KeyboardInterrupt:
		pass

	# Gently stop on CTRL C

	finally:

		lj.ClosePlugin()
		OSCstop()



Run()


