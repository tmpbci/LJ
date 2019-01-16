# coding=UTF-8
'''
Created on 13 nov. 2014

@author: pclf
'''
import math

class Polar2D(object):
	'''
	classdocs
	'''


	def __init__(self, r, theta):
		'''
		Constructor
		'''
		self.r = r
		self.theta = theta
	
	def Rotate(self, theta):
		return Polar2D(self.r, self.theta + theta)

	def RotateSelf(self, theta):
		self.theta += theta
	
	def Zoom(self, r):
		return Polar2D(self.r * r, self.theta)

	def ZoomSelf(self, r):
		self.r *= r

	def RotateZoom(self, r, theta):
		return Polar2D(self.r * r, self.theta + theta)

	def RotateZoomSelf(self, r, theta):
		self.r *= r
		self.theta += theta
		
	def ToXY(self):
		theta_rd = math.radians(self.theta)
		return Vector2D(self.r * math.sin(theta_rd), - self.r * math.cos(theta_rd))
	
class Vector2D(object):
	
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __add__(self, other):
		return Vector2D(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other):
		return Vector2D(self.x - other.x, self.y - other.y)
	
	# __iadd__ et __isub__ si nécessaire
	
	def __mul__(self, k):
		return Vector2D(self.x * k, self.y * k)

	def __div__(self, k):
		return Vector2D(self.x / k, self.y / k)
	
	def ScalarProduct(self, v):
		return self.x*v.x + self.y*v.y
	
	def Det(self, v):
		return self.x*v.y - self.y*v.x
	
	def MatrixProduct(self, vx, vy):
		return Vector2D(self.ScalarProduct(vx),self.ScalarProduct(vy))
		
	def ToTuple(self):
		return (self.x,self.y)
		