# coding=UTF-8
"""
LJay/LJ 

v0.8

Command line arguments parser

by Sam Neurohack 
from /team/laser

"""


import gstt
import argparse

print "-h will display help"
print ""

def handle():


	#have to be done before importing bhorosc.py to get correct port assignment
	argsparser = argparse.ArgumentParser(description="LJ v0.8")
	argsparser.add_argument("-r","--redisIP",help="IP address to bind builtin servers (OSC and websocket) also must be the Redis server IP ",type=str)
	argsparser.add_argument("-L","--Lasers",help="Number of lasers connected.",type=int)
	argsparser.add_argument("-v","--verbose",help="Debug mode 0,1 or 2.",type=int)
	argsparser.add_argument("-x","--invx",help="Invert laser 0 X axis again",action="store_true")
	argsparser.add_argument("-y","--invy",help="Invert laser 0 Y axis again",action="store_true")
	argsparser.add_argument("-d","--display",help="Point List number displayed in simulator",type=int)
	argsparser.add_argument("-a","--align",help="Reset laser 0 alignement values",action="store_true")
	argsparser.add_argument("-i","--iport",help="port number for builtin LJ OSC server (8002 by default)",type=int)	
	argsparser.add_argument("-n","--nozoidIP",help="IP for llstr' Nozoid OSC server port 8003 ('127.0.0.1' by default)",type=str)
	argsparser.add_argument("-b","--bhoroscIP",help="IP for OSC output ('127.0.0.1' by default)",type=str)
	argsparser.add_argument("-o","--oport",help="OSC output port number (8001 by default)",type=int)



	# Keep it ! if new features of cli.py is used in a monolaser program
	# argsparser.add_argument("-l","--laser",help="Last digit of etherdream ip address 192.168.1.0/24 (4 by default). Localhost if digit provided is 0.",type=int)
	

	args = argsparser.parse_args()

	# Verbose = debug
	if args.verbose  != None:
		#print "setting gstt.debug to", args.verbose
		gstt.debug = args.verbose

	# Ports arguments
	if args.iport:
		iport = args.iport
		gstt.iport = iport
	else:
		iport = gstt.iport

	if args.oport:
		oport = args.oport
		gstt.oport = oport
	else:
		oport = gstt.oport

	if gstt.debug > 0:
		print "gstt.oport:",gstt.oport
		print "gstt.iport:",gstt.iport


	# X Y inversion arguments
	if args.invx == True:

		gstt.swapX[0] = -1 * gstt.swapX[0]
		gstt.centerx[0] = 0
		gstt.centery[0] = 0
		#WriteSettings()
		print("laser 0 X new invertion Asked")
		if gstt.swapX[0] == 1:
			print ("X not Inverted")
		else:
			print ("X Inverted")

	if args.invy == True:

		gstt.swapY[0] = -1 * gstt.swapY[0]
		gstt.centerx[0] = 0
		gstt.centery[0] = 0
		#WriteSettings()
		print("laser 0 Y new invertion Asked")
		if gstt.swapY[0] == 1:
			print ("Y not Inverted")
		else:
			print("Y inverted")

	# Redis Computer IP
	if args.redisIP  != None:
		gstt.LjayServerIP  = args.redisIP



	# Point list number used by simulator
	if args.display  != None:
		gstt.simuPL = args.display
		print "Display : " + str(gstt.simuPL)

	

	# Lasers = number of laser connected
	if args.Lasers  != None:
		gstt.LaserNumber = args.Lasers
	
	
	if args.bhoroscIP  != None:
		gstt.oscIPin = args.bhoroscIP
	else:
		gstt.oscIPin = '127.0.0.1'

	if args.nozoidIP  != None:
		gstt.nozoscIP = args.nozoidIP
	else:
		gstt.nozoscIP = '127.0.0.1'

	# Etherdream target for mono laser program
	'''
	if args.laser  != None:
		lstdgtlaser = args.laser		

		if lstdgtlaser == 0:
			etherIP = "127.0.0.1"
		else:
			etherIP = "192.168.1."+str(lstdgtlaser)

	else:
		etherIP = "192.168.1.4"

	#print ("Laser 1 etherIP:",etherIP)
	'''

	# Reset alignment values
	if args.align == True:

		gstt.centerx[0] = 0
		gstt.centery[0] = 0
		gstt.zoomx[0] = 15
		gstt.zoomy[0] = 15
		gstt.sizex[0] = 32000
		gstt.sizey[0] = 32000
		gstt.finangle[0] = 0.0
		gstt.swapx[0] = 1
		gstt.swapy[0] = 1
		#Settings.Write()
	
handle()