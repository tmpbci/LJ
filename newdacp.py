#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''
LJay v0.8.0

newdacp.py
Unhanced version (redis and process style) of the etherdream python library from j4cDAC.

LICENCE : CC
Sam Neurohack, pclf

Conversion in etherdream coordinates, geometric corrections,... 
Init call with a laser number and which point list to draw. Etherdream IP is found in conf file for given laser number

Uses redis keys value for live inputs/outputs 
These redis keys are read and set at each main loop.

Live inputs :
/pl/lasernumber [(x,y,color),(x1,y1,color),...] A string of list of pygame points list. 
/resampler/lasernumber [(1.0,8), (0.25,3),(0.75,3),(1.0,10)] : a string for resampling rules. 
					the first tuple (1.0,8) is for short line < 4000 in etherdream space
					(0.25,3),(0.75,3),(1.0,10) for long line > 4000
					i.e (0.25,3) means go at 25% position on the line, send 3 times this position to etherdream

Live ouputs :
/lstt/lasernumber value    etherdream last_status.playback_state  (0: idle   1: prepare   2: playing)
/cap/lasernumber           number of empty points sent to fill etherdream buffer (up to 1799)
/lack/lasernumber value    "a": ACK   "F": Full  "I": invalid. 64 or 35 for no connection. 
Geometric corrections :




'''

import socket
import time
import struct
from gstt import debug, PL
import gstt
import math
from itertools import cycle
#from globalVars import *
import pdb
import ast
import redis

import homographyp
import numpy as np

black_points = [(278.0,225.0,0),(562.0,279.0,0),(401.0,375.0,0),(296.0,454.0,0),(298.0,165.0,0)]
grid_points = [(300.0,200.0,0),(500.0,00.0,65280),(500.0,400.0,65280),(300.0,400.0,65280),(300.0,200.0,65280),(200.0,100.0,0),(600.0,100.0,65280),(600.0,500.0,65280),(200.0,500.0,65280),(200.0,100.0,65280)]

r = redis.StrictRedis(host=gstt.LjayServerIP, port=6379, db=0)


def pack_point(x, y, r, g, b, i = -1, u1 = 0, u2 = 0, flags = 0):
	"""Pack some color values into a struct dac_point.

	Values must be specified for x, y, r, g, and b. If a value is not
	passed in for the other fields, i will default to max(r, g, b); the 
	rest default to zero.
	"""
	
	if i < 0:
		i = max(r, g, b)

	return struct.pack("<HhhHHHHHH", flags, x, y, r, g, b, i, u1, u2)


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
		'''
		if debug == 2:
			for l in lines:
				print prefix + l
		'''

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
		for l in lines:
			print prefix + l
		if debug == 1:
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

				delta_x, delta_y = self.xyrgb[0] - self.xyrgb_prev[0], self.xyrgb[1] - self.xyrgb_prev[1]
				
				#test adaptation selon longueur ligne
				if math.hypot(delta_x, delta_y) < 4000:

					# For glitch art : decrease lsteps
					l_steps = [ (1.0, 8)]
					#l_steps = gstt.stepshortline

				else:
					# For glitch art : decrease lsteps
					l_steps = [ (0.25, 3), (0.75, 3), (1.0, 10)]
					#_steps = gstt.stepslongline

				for e in l_steps:
					step = e[0]

					for i in xrange(0,e[1]):

						self.xyrgb_step = (self.xyrgb_prev[0] + step*delta_x, self.xyrgb_prev[1] + step*delta_y) + self.xyrgb[2:]		
						yield self.xyrgb_step

				self.xyrgb_prev = self.xyrgb
			

	def GetPoints(self, n):

		d = [self.newstream.next() for i in xrange(n)]
		#print d
		return d


	# Etherpoint all transform in one matrix, with warp !!
	# xyc : x y color
	def EtherPoint(self,xyc):
	
		c = xyc[2]

		#print ""
		#print "pygame point",[(xyc[0],xyc[1],xyc[2])]
		#gstt.EDH[self.mylaser]= np.array(ast.literal_eval(r.get('/EDH/'+str(self.mylaser))))
		position = homographyp.apply(gstt.EDH[self.mylaser],np.array([(xyc[0],xyc[1])]))

		#print "etherdream point",position[0][0],  position[0][1], ((c >> 16) & 0xFF) << 8, ((c >> 8) & 0xFF) << 8, (c & 0xFF) << 8
		#print ''
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
		#print "laser response", self.mylaser, response
		gstt.lstt_dacanswers[self.mylaser] = response
		cmdR = data[1]
		status = Status(data[2:])
		r.set('/lack/'+str(self.mylaser), response)

		if cmdR != cmd:
			raise ProtocolError("expected resp for %r, got %r"
				% (cmd, cmdR))

		if response != "a":
			raise ProtocolError("expected ACK, got %r"
				% (response, ))

		self.last_status = status
		return status

	def __init__(self, mylaser, PL, port = 7765):
		"""Connect to the DAC over TCP."""
		socket.setdefaulttimeout(2)

		#print "init"
		self.mylaser = mylaser
		#print "DAC", self.mylaser, "Handler process, connecting to", gstt.lasersIPS[mylaser] 
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connstatus = self.conn.connect_ex((gstt.lasersIPS[mylaser], port))
		#print "Connection status for", self.mylaser,":", self.connstatus
		#print 'debug', debug, gstt.debug
		# ipconn state is -1 at startup (see gstt) and modified here
		r.set('/lack/'+str(self.mylaser), self.connstatus)
		gstt.lstt_ipconn[self.mylaser] =  self.connstatus		

		self.buf = ""
		# Upper case PL is the Point List number
		self.PL = PL

		# Lower case pl is the actual point list coordinates
		self.pl = ast.literal_eval(r.get('/pl/'+str(self.mylaser)))
		#if self.mylaser ==0:
		print "DAC Init Laser", self.mylaser
		#print  "pl :", self.pl
		#print "EDH/"+str(self.mylaser),r.get('/EDH/'+str(self.mylaser))
		if r.get('/EDH/'+str(self.mylaser)) == None:
			print "Laser",self.mylaser,"NO EDH !! Computing one..."
			homographyp.newEDH(self.mylaser)
		else:	
			gstt.EDH[self.mylaser] = np.array(ast.literal_eval(r.get('/EDH/'+str(self.mylaser))))
			print "Laser",self.mylaser,"found its EDH in redis"
			#print gstt.EDH[self.mylaser]
		
		'''
		d =homographyp.apply(gstt.EDH[self.mylaser],np.array([(300,400)]))
		print ''
		print "d",d
		print "d0",d[0]
		#print "d1",len(d[1])
		print " "
		'''

		self.xyrgb = self.xyrgb_prev = (0,0,0,0,0)
		self.newstream = self.OnePoint()

		print "Connection status for", self.mylaser,":", self.connstatus
		#print 'debug', debug
		if self.connstatus != 0:
			print ""
			print "Connection ERROR",self.connstatus,"with laser", str(mylaser),":",str(gstt.lasersIPS[mylaser])
			#print "first 10 points in PL",self.PL, self.GetPoints(10)

		# Reference points 
		# Read the "hello" message
		first_status = self.readresp("?")
		first_status.dump()
		position = []


	def begin(self, lwm, rate):
		cmd = struct.pack("<cHI", "b", lwm, rate)
		#print "Begin newdac : Laser ",  str(self.mylaser), " PL : ", str(self.PL)

		self.conn.sendall(cmd)
		return self.readresp("b")

	def update(self, lwm, rate):
		cmd = struct.pack("<cHI", "u", lwm, rate)
		self.conn.sendall(cmd)
		return self.readresp("u")

	def encode_point(self, point):
		return pack_point(*point)

	def write(self, points):
		epoints = map(self.encode_point, points)
		cmd = struct.pack("<cH", "d", len(epoints))
		self.conn.sendall(cmd + "".join(epoints))
		return self.readresp("d")

	def prepare(self):
		self.conn.sendall("p")
		return self.readresp("p")


	def stop(self):
		self.conn.sendall("s")
		return self.readresp("s")

	def estop(self):
		self.conn.sendall("\xFF")
		return self.readresp("\xFF")

	def clear_estop(self):
		self.conn.sendall("c")
		return self.readresp("c")

	def ping(self):
		self.conn.sendall("?")
		return self.readresp("?")

	def play_stream(self):

		# print last playback state
		#print "laser", self.mylaser, "Pb : ",self.last_status.playback_state

		# error if etherdream is already playing state (from other source)
		if self.last_status.playback_state == 2:
			raise Exception("already playing?!")
		
		# if idle go to prepare state
		elif self.last_status.playback_state == 0:
			self.prepare()

		started = 0

		while True:

			#print "laser", self.mylaser, "Pb : ",self.last_status.playback_state
			# update drawing parameters from redis keys

			order = int(r.get('/order'))

			#Laser order bit 0 = 0
			if not order & (1 << (self.mylaser*2)):
				#print "laser",mylaser,"bit 0 : 0"

				# Laser bit 0 = 0 and bit 1 = 0 : USER PL
				if not order & (1 << (1+self.mylaser*2)):
					#print "laser",mylaser,"bit 1 : 0"
					self.pl = ast.literal_eval(r.get('/pl/'+str(self.mylaser)))
				
				else:
				# Laser bit 0 = 0 and bit 1 = 1 : New EDH
					#print "laser",mylaser,"bit 1 : 1" 
					print "Laser",self.mylaser,"new EDH ORDER in redis"
					gstt.EDH[self.mylaser]= np.array(ast.literal_eval(r.get('/EDH/'+str(self.mylaser))))
					# Back to USER PL
					order = r.get('/order')
					neworder = order & ~(1<< self.mylaser*2)
					neworder = neworder & ~(1<< 1+ self.mylaser*2)
					r.set('/order', str(neworder))	  
			else:
			
			# Laser bit 0 = 1 
				print "laser",mylaser,"bit 0 : 1"

				# Laser bit 0 = 1 and bit 1 = 0 : Black PL
				if not order & (1 << (1+self.mylaser*2)):
					#print "laser",mylaser,"bit 1 : 0"
					self.pl = black_points
				
				else:
				# Laser bit 0 = 1 and bit 1 = 1 : GRID PL
					#print "laser",mylaser,"bit 1 : 1"   
					self.pl = grid_points 



			#self.pl = ast.literal_eval(r.get('/pl/'+str(self.mylaser)))

			#if self.mylaser == 0:
			#	print "franken pl for ", self.mylaser, ":", self.pl
			#print "franken 0 point :", self.pl[0]

			'''
			self.resampler = ast.literal_eval(r.get('/resampler/'+str(self.mylaser)))
			print "resampler for", self.mylaser, ":",self.resampler
			gstt.stepshortline    = self.resampler[0]
			gstt.stepslongline[0] = self.resampler[1]
			gstt.stepslongline[1] = self.resampler[2]
			gstt.stepslongline[2] = self.resampler[3]
			'''

			r.set('/lstt/'+str(self.mylaser), self.last_status.playback_state)
			# pdb.set_trace()
			# How much room?

			cap = 1799 - self.last_status.fullness
			points = self.GetPoints(cap)

			r.set('/cap/'+str(self.mylaser), cap)

			#if self.mylaser == 0:
			#print self.mylaser, cap
			if cap < 100:
				time.sleep(0.001)
				cap += 150

#			print "Writing %d points" % (cap, )
			#t0 = time.time()
			#print points
			self.write(points)
			#t1 = time.time()
#			print "Took %f" % (t1 - t0, )

			if not started:
				self.begin(0, gstt.kpps[self.mylaser])
				started = 1

# not used in LJay.
def find_dac():
	"""Listen for broadcast packets."""

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(("0.0.0.0", 7654))

	while True:
		data, addr = s.recvfrom(1024)
		bp = BroadcastPacket(data)
		
		print "Packet from %s: " % (addr, )
		bp.dump()
