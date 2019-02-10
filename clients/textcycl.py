# coding=UTF-8

'''
Cycling text on one LJ laser.
LICENCE : CC
'''

import redis
import lj
import sys,time
import argparse

duration = 300
lasertext = ["TEAMLASER","FANFAN","LOLOSTER","SAM"]

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

lj.Config(redisIP,ljclient)
#r = redis.StrictRedis(host=redisIP, port=6379, db=0)


# If you want to use rgb for color :
def rgb2int(r,g,b):
    return int('0x%02x%02x%02x' % (r,g,b),0)


def Run():

	counter =0
	step = 0
	timing = -1
	color = rgb2int(255,255,255)


	while 1:
	
		if timing == duration or timing == -1:
			message = lasertext[step]
			lj.Text(message, color, PL = 0, xpos = 300, ypos = 300, resize = 1, rotx =0, roty =0 , rotz=0)
			lj.DrawPL(0)
			timing = 0

		else:
			step += 1
			if step >3:
				step =0	
		timing += 1
		time.sleep(0.01)

Run()


