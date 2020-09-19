#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''

Tracer v0.8.2

Etherdream DACs handler on network via Redis 

LICENCE : CC
Sam Neurohack, pclf

Includes live conversion in etherdream coordinates, geometric corrections, color balance change, intensity limitation, grid display,...

One tracer process is launched per requested laser by LJ. Lasers parameters in LJ.conf.
Live I/O based on redis keys : inputs (Pointlists to draw,...) and outputs (DAC state, errors,..).
Keys are mostly read and set at each main loop.
This tracer include an enhanced version (support for several lasers) of the etherdream python library from j4cDAC.


* Redis keys reference *

- Drawing things :

/pl/Scene/lasernumber  [(x,y,color),(x1,y1,color),...]	 The live list of drawn pygame points. Tracer continously ask redis for key /clientkey+lasernumber
/resampler/lasernumber [(1.0,8), (0.25,3),(0.75,3),(1.0,10)] : a string for resampling rules. 
							the first tuple (1.0,8) is for short line < 4000 in etherdream space
							(0.25,3),(0.75,3),(1.0,10) for long line > 4000
							i.e (0.25,3) means go at 25% position on the line, send 3 times this position to etherdream
/clientkey				"/pl/SceneNumber/" 				What Scene to retrieve from redis
/EDH/lasernumber

- Tracer control :

/order 				  	0-8 					Set redis key with new value then issue the order number

						0 : Draw Normal point list
						1 : Get the new EDH 		 = reread redis key /EDH/lasernumber
						2 : Draw BLACK point list
						3 : Draw GRID point list
						4 : Resampler Change (longs and shorts lsteps)
						5 : Client Key Change 		 = reread redis key /clientkey
						6 : Max Intensity Change 	 = reread redis key /intensity
						7 : kpps change 			 = reread redis key /kpps
						8 : color balance change 	 = reread redis keys /red /green /blue


- Managing Etherdream DACs :

Discrete drawing values

/kpps      				0-		 		  DAC output speed to laser, then order 7. Depends of actual angle
/intensity 				0-255			  Laser output power, then order 6 (for alignement,...)
/red       				0-100  			  % of full red, then order 8 
/green     				0-100     		  % of full green, then order 8 
/blue      				0-100 			  % of full blue, then order 8 

DAC status report 

/lstt/lasernumber     	etherdream last_status.playback_state  (0: idle   1: prepare   2: playing)
/cap/lasernumber      	number of empty points sent to fill etherdream buffer (up to 1799)
/lack/lasernumber 	    "a": ACK   "F": Full  "I": invalid. 64 or 35 for no connection. 


Geometric corrections 

Doctodo


'''
import socket
import time
import struct
#from gstt import debug
from libs3 import gstt,log
import math
from itertools import cycle
#from globalVars import *
import pdb
import ast
import redis

from libs3 import homographyp
import numpy as np
import binascii

black_points = [(278.0,225.0,0),(562.0,279.0,0),(401.0,375.0,0),(296.0,454.0,0),(298.0,165.0,0)]
grid_points = [(300.0,200.0,0),(500.0,200.0,65280),(500.0,400.0,65280),(300.0,400.0,65280),(300.0,200.0,65280),(300.0,200.0,0),(200.0,100.0,0),(600.0,100.0,65280),(600.0,500.0,65280),(200.0,500.0,65280),(200.0,100.0,65280)]

r = redis.StrictRedis(host=gstt.LjayServerIP, port=6379, db=0)
# r = redis.StrictRedis(host=gstt.LjayServerIP , port=6379, db=0, password='-+F816Y+-')
ackstate = {'61': 'ACK', '46': 'FULL', '49': "INVALID", '21': 'STOP', '64': "NO CONNECTION ?", '35': "NO CONNECTION ?" , '97': 'ACK', '70': 'FULL', '73': "INVALID", '33': 'STOP', '100': "NOCONNECTION", '48': "NOCONNECTION", 'a': 'ACK', 'F': 'FULL', 'I': "INVALID", '!': 'STOP', 'd': "NO CONNECTION ?", '0': "NO CONNECTION ?"}
lstate = {'0': 'IDLE', '1': 'PREPARE', '2': "PLAYING", '64': "NOCONNECTION ?" }

def pack_point(laser, intensity, x, y, r, g, b, i = -1, u1 = 0, u2 = 0, flags = 0):
	"""Pack some color values into a struct dac_point."""

	#print("Tracer", laser,":", r,g,b,"intensity", intensity, "i", i)
	
	if r > intensity:
		r = intensity
	if g > intensity:
		g = intensity
	if b > intensity:
		b = intensity
	

	if max(r, g, b) == 0:
		i = 0
	else: 
		i = intensity

	x = int(x)
	y = int(y)
	#print("Tracer ", laser, ": packing", x, y, r, g, b, "intensity", intensity, "i", i)


	if x < -32767:
		x = -32767
		if gstt.debug >1:
			log.err("Tracer "+ str(laser) +" : x coordinates was below -32767")

	if x > 32767:
		x = 32767
		if gstt.debug >1:
			log.err("Tracer "+ str(laser) +" : x coordinates was bigger than 32767")


	if y < -32767:
		y = -32767
		if gstt.debug >1:
			log.err("Tracer "+ str(laser) +" : y coordinates was below -32767")

	if y > 32767:
		y = 32767
		if gstt.debug >1:
			log.err("Tracer "+ str(laser) +" : y coordinates was bigger than 32767")

	return struct.pack("<HhhHHHHHH", flags, x, y, r, g, b, i, u1, u2)
	#return struct.pack("<HhhHHHHHH", flags, round(x), round(y), r, g, b, i, u1, u2)


class ProtocolError(Exception):
	"""Exception used when a protocol error is detected."""
	pass


class Status(object):
	"""Represents a status response from the DAC."""

	def __init__(self, data):
		"""Initialize from a chunk of data."""
		self.protocol_version, self.le_state, self.playback_state, \
		  self.source, self.le_flags, self.playback_flags, \
		  self.source_flags, self.fullness, self.point_rate, \
		  self.point_count = \
			struct.unpack("<BBBBHHHHII", data)

	def dump(self, prefix = " - "):
		"""Dump to a string."""
		lines = [
			""
			"Host ",
			"Light engine: state %d, flags 0x%x" %
				(self.le_state, self.le_flags),
			"Playback: state %d, flags 0x%x" %
				(self.playback_state, self.playback_flags),
			"Buffer: %d points" %
				(self.fullness, ),
			"Playback: %d kpps, %d points played" %
				(self.point_rate, self.point_count),
			"Source: %d, flags 0x%x" %
				(self.source, self.source_flags)
		]
		
		if gstt.debug == 2:
			print()
			for l in lines:
				print(prefix + l)
		

class BroadcastPacket(object):
	"""Represents a broadcast packet from the DAC."""

	def __init__(self, st):
		"""Initialize from a chunk of data."""
		self.mac = st[:6]
		self.hw_rev, self.sw_rev, self.buffer_capacity, \
		self.max_point_rate = struct.unpack("<HHHI", st[6:16])
		self.status = Status(st[16:36])

	def dump(self, prefix = " - "):
		"""Dump to a string."""
		lines = [
			"MAC: " + ":".join(
				"%02x" % (ord(o), ) for o in self.mac),
			"HW %d, SW %d" %
				(self.hw_rev, self.sw_rev),
			"Capabilities: max %d points, %d kpps" %
				(self.buffer_capacity, self.max_point_rate)
		]
		print()
		for l in lines:
			print(prefix + l)
		if gstt.debug > 1:
			self.status.dump(prefix)


class DAC(object):
	"""A connection to a DAC."""


	# "Laser point List" Point generator
	# each points is yielded : Getpoints() call n times OnePoint()
	
	def OnePoint(self):
		
		while True:

			#pdb.set_trace()	
			for indexpoint,currentpoint in enumerate(self.pl):
				#print indexpoint, currentpoint
				xyc = [currentpoint[0],currentpoint[1],currentpoint[2]]
				self.xyrgb = self.EtherPoint(xyc)
				#print(self.xyrgb[2:])
				rgb = (round(self.xyrgb[2:][0] *self.intred/100), round(self.xyrgb[2:][1] *self.intgreen/100), round(self.xyrgb[2:][2] *self.intblue/100))
				#print("rgb :", rgb)

				#round(*self.intred/100) 
				#round(*self.intgreen/100)
				#round(*self.intblue/100)
				
				delta_x, delta_y = self.xyrgb[0] - self.xyrgb_prev[0], self.xyrgb[1] - self.xyrgb_prev[1]
				
				#test adaptation selon longueur ligne
				if math.hypot(delta_x, delta_y) < 4000:

					# For glitch art : decrease lsteps
					#l_steps = [ (1.0, 8)]
					l_steps = gstt.stepshortline

				else:
					# For glitch art : decrease lsteps
					#l_steps = [ (0.25, 3), (0.75, 3), (1.0, 10)]
					l_steps = gstt.stepslongline

				for e in l_steps:
					step = e[0]

					for i in range(0,e[1]):

						self.xyrgb_step = (self.xyrgb_prev[0] + step*delta_x, self.xyrgb_prev[1] + step*delta_y) + rgb # + self.xyrgb_prev[2:]# + rgb
						#print(self.xyrgb_step)
						yield self.xyrgb_step

				self.xyrgb_prev = self.xyrgb
			

	def GetPoints(self, n):

		d = [next(self.newstream) for i in range(n)]
		#print d
		return d


	# Etherpoint all transform in one matrix, with warp !!
	# xyc : x y color
	def EtherPoint(self,xyc):
	
		c = xyc[2]

		#print("")
		#print("pygame point",[(xyc[0],xyc[1],xyc[2])])
		#gstt.EDH[self.mylaser]= np.array(ast.literal_eval(r.get('/EDH/'+str(self.mylaser))))
		position = homographyp.apply(gstt.EDH[self.mylaser],np.array([(xyc[0],xyc[1])]))

		#print("etherdream point",position[0][0],  position[0][1], ((c >> 16) & 0xFF) << 8, ((c >> 8) & 0xFF) << 8, (c & 0xFF) << 8)

		return (position[0][0],  position[0][1], ((c >> 16) & 0xFF) << 8, ((c >> 8) & 0xFF) << 8, (c & 0xFF) << 8)


	def read(self, l):
		"""Read exactly length bytes from the connection."""
		while l > len(self.buf):
			self.buf += self.conn.recv(4096)

		obuf = self.buf
		self.buf = obuf[l:]
		return obuf[:l]

	def readresp(self, cmd):
		"""Read a response from the DAC."""

		
		data = self.read(22)
		response = data[0]
		gstt.lstt_dacanswers[self.mylaser] = response
		cmdR = chr(data[1])
		status = Status(data[2:])

		r.set('/lack/'+str(self.mylaser), response)

		if cmdR != cmd:
			raise ProtocolError("expected resp for %r, got %r"
				% (cmd, cmdR))

		if response != ord('a'):
			raise ProtocolError("expected ACK, got %r"
				% (response, ))

		self.last_status = status
		return status

	def __init__(self, mylaser, PL, port = 7765):
		"""Connect to the DAC over TCP."""
		socket.setdefaulttimeout(2)

		self.mylaser = mylaser
		self.clientkey = r.get("/clientkey").decode('ascii')

		#log.info("Tracer "+str(self.mylaser)+" connecting to "+ gstt.lasersIPS[mylaser])
		#print("DAC", self.mylaser, "Handler process, connecting to", gstt.lasersIPS[mylaser] )
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connstatus = self.conn.connect_ex((gstt.lasersIPS[mylaser], port))
		if self.connstatus == 35 or self.connstatus == 64:
			log.err("Tracer "+ str(self.mylaser)+" ("+ gstt.lasersIPS[mylaser]+"): "+ackstate[str(self.connstatus)])
		else:
			print("Tracer "+ str(self.mylaser)+" ("+ gstt.lasersIPS[mylaser]+"): "+ackstate[str(self.connstatus)])

		# ipconn state is -1 at startup (see gstt) and modified here
		r.set('/lack/'+str(self.mylaser), self.connstatus)
		gstt.lstt_ipconn[self.mylaser] =  self.connstatus		

		self.buf = b''
		# Upper case PL is the Point List number
		self.PL = PL

		# Lower case pl is the actual point list coordinates
	

		#pdb.set_trace()
		self.pl = ast.literal_eval(r.get(self.clientkey + str(self.mylaser)).decode('ascii'))
		if r.get('/EDH/'+str(self.mylaser)) == None:
			#print("Laser",self.mylaser,"NO EDH !! Computing one...")
			homographyp.newEDH(self.mylaser)
		else:	
	
			gstt.EDH[self.mylaser] = np.array(ast.literal_eval(r.get('/EDH/'+str(self.mylaser)).decode('ascii')))
			#print("Laser",self.mylaser,"found its EDH in redis")
			#print gstt.EDH[self.mylaser]
		
		self.xyrgb = self.xyrgb_prev = (0,0,0,0,0)
		self.intensity = 65280
		self.intred = 100
		self.intgreen = 100
		self.intblue = 100
		self.newstream = self.OnePoint()
		
		if gstt.debug >0:
			print("Tracer",self.mylaser,"init asked for ckey", self.clientkey+str(self.mylaser))
			if self.connstatus != 0:
				#print(""
				log.err("Connection ERROR " +str(self.connstatus)+" with laser "+str(mylaser)+" : "+str(gstt.lasersIPS[mylaser]))
				#print("first 10 points in PL",self.PL, self.GetPoints(10)
			else:
				print("Connection status for DAC "+str(self.mylaser)+" : "+ str(self.connstatus))


		# Reference points 
		# Read the "hello" message
		first_status = self.readresp("?")
		first_status.dump()
		position = []


	def begin(self, lwm, rate):
		cmd = struct.pack("<cHI", b'b', lwm, rate)
		print("Tracer",  str(self.mylaser), "begin with PL : ", str(self.PL))
		self.conn.sendall(cmd)
		return self.readresp("b")

	def update(self, lwm, rate):
		print(("update", lwm, rate))
		cmd = struct.pack("<cHI", b'u', lwm, rate)
		self.conn.sendall(cmd)
		return self.readresp("u")

	def encode_point(self, point):
		return pack_point(self.mylaser, self.intensity, *point)

	def write(self, points):
		epoints = list(map(self.encode_point, points))
		cmd = struct.pack("<cH", b'd', len(epoints))
		self.conn.sendall(cmd + b''.join(epoints))
		return self.readresp('d')

	def prepare(self):
		self.conn.sendall(b'p')
		return self.readresp('p')


	def stop(self):
		self.conn.sendall('s')
		return self.readresp('s')

	def estop(self):
		self.conn.sendall("\xFF")
		return self.readresp("\xFF")

	def clear_estop(self):
		self.conn.sendall("c")
		return self.readresp("c")

	def ping(self):
		self.conn.sendall('?')
		return self.readresp('?')



	def play_stream(self):

		#print("laser", self.mylaser, "Pb : ",self.last_status.playback_state)

		# error if etherdream is already playing state (from other source)
		if self.last_status.playback_state == 2:
			raise Exception("already playing?!")
		
		# if idle go to prepare state
		elif self.last_status.playback_state == 0:
			self.prepare()

		started = 0

		while True:

			#print("laser", self.mylaser, "Pb : ",self.last_status.playback_state)

			order = int(r.get('/order/'+str(self.mylaser)).decode('ascii'))
			#print("tracer", str(self.mylaser),"order", order, type(order)

			if order == 0:
				
				# USER point list
				self.pl = ast.literal_eval(r.get(self.clientkey+str(self.mylaser)).decode('ascii'))
				#print("Tracer : laser", self.mylaser, " order 0 : pl : ",len(self.pl))

			else:
	
				# Get the new EDH 
				if order == 1:
					print("Tracer",self.mylaser,"new EDH ORDER in redis")
					gstt.EDH[self.mylaser]= np.array(ast.literal_eval(r.get('/EDH/'+str(self.mylaser)).decode('ascii')))
					# Back to user point list
					r.set('/order/'+str(self.mylaser), 0)
				
				# BLACK point list
				if order == 2:
					print("Tracer",self.mylaser,"BLACK ORDER in redis")
					self.pl = black_points
	
				# GRID point list
				if order == 3:
					print("Tracer",self.mylaser,"GRID ORDER in redis")
					self.pl = grid_points
	
			
				# Resampler Change
				if order == 4:
					self.resampler = ast.literal_eval(r.get('/resampler/'+str(self.mylaser)).decode('ascii'))
					print("Tracer", self.mylaser," : resetting lsteps for",self.resampler)
					gstt.stepshortline    = self.resampler[0]
					gstt.stepslongline[0] = self.resampler[1]
					gstt.stepslongline[1] = self.resampler[2]
					gstt.stepslongline[2] = self.resampler[3]
					# Back to user point list order
					r.set('/order/'+str(self.mylaser), 0)
	
				# Client Key change
				if order == 5:
					print("Tracer", self.mylaser, "new clientkey")
					self.clientkey = r.get('/clientkey')
					# Back to user point list order
					r.set('/order/'+str(self.mylaser), 0)
	
				# Intensity change
				if order == 6:
					self.intensity = int(r.get('/intensity/' + str(self.mylaser)).decode('ascii')) << 8
					print("Tracer" , self.mylaser, "new Intensity", self.intensity)
					gstt.intensity[self.mylaser] = self.intensity
					r.set('/order/'+str(self.mylaser), "0")
					
				# kpps change
				if order == 7:
					gstt.kpps[self.mylaser] = int(r.get('/kpps/' + str(self.mylaser)).decode('ascii'))
					print("Tracer",self.mylaser,"new kpps", gstt.kpps[self.mylaser])
					self.update(0, gstt.kpps[self.mylaser])
					r.set('/order/'+str(self.mylaser), "0")

				# color balance change
				if order == 8:
					self.intred = int(r.get('/red/' + str(self.mylaser)).decode('ascii'))
					self.intgreen = int(r.get('/green/' + str(self.mylaser)).decode('ascii'))
					self.intblue = int(r.get('/blue/' + str(self.mylaser)).decode('ascii'))
					print("Tracer", self.mylaser, "new color balance", self.intred,"% ", self.intgreen, "% ",self.intblue,"% ")
					r.set('/order/'+str(self.mylaser), "0")
		
	
			r.set('/lstt/'+str(self.mylaser), self.last_status.playback_state)
			# pdb.set_trace()
			# How much room?

			cap = 1799 - self.last_status.fullness
			points = self.GetPoints(cap)

			r.set('/cap/'+str(self.mylaser), cap)

			if cap < 100:
				time.sleep(0.001)
				cap += 150

#			print("Writing %d points" % (cap, ))
			#t0 = time.time()
			#print points
			self.write(points)
			#t1 = time.time()
#			print("Took %f" % (t1 - t0, )

			if not started:
				print("Tracer", self.mylaser, "starting with", gstt.kpps[self.mylaser],"kpps")
				self.begin(0, gstt.kpps[self.mylaser])
				started = 1

# not used in LJ.
def find_dac():
	"""Listen for broadcast packets."""

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(("0.0.0.0", 7654))

	while True:
		data, addr = s.recvfrom(1024)
		bp = BroadcastPacket(data)
		
		print(("Packet from %s: " % (addr, )))
		bp.dump()


'''
			#Laser order bit 0 = 0
			if not order & (1 << (self.mylaser*2)):
				#print("laser",mylaser,"bit 0 : 0")

				# Laser bit 0 = 0 and bit 1 = 0 : USER PL
				if not order & (1 << (1+self.mylaser*2)):
					#print("laser",mylaser,"bit 1 : 0")
					self.pl = ast.literal_eval(r.get('/pl/'+str(self.mylaser)))
				
				else:
				# Laser bit 0 = 0 and bit 1 = 1 : New EDH
					#print("laser",mylaser,"bit 1 : 1" )
					print("Laser",self.mylaser,"new EDH ORDER in redis"
					gstt.EDH[self.mylaser]= np.array(ast.literal_eval(r.get('/EDH/'+str(self.mylaser))))
					# Back to USER PL
					order = r.get('/order')
					neworder = order & ~(1<< self.mylaser*2)
					neworder = neworder & ~(1<< 1+ self.mylaser*2)
					r.set('/order', str(neworder))	  
			else:
			
			# Laser bit 0 = 1 
				print("laser",mylaser,"bit 0 : 1")

				# Laser bit 0 = 1 and bit 1 = 0 : Black PL
				if not order & (1 << (1+self.mylaser*2)):
					#print("laser",mylaser,"bit 1 : 0")
					self.pl = black_points
				
				else:
				# Laser bit 0 = 1 and bit 1 = 1 : GRID PL
					#print("laser",mylaser,"bit 1 : 1"   )
					self.pl = grid_points 
'''
