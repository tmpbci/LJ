"""
Directions Buttons defined correctly only for PS3 and USBJoystick 


Represent various videogame controllers

TODO: Various play schemes/configs
XXX: UNTESTED
"""

import re

def setup_controls(joystick):
	"""
	Joystick wrapper.
	"""
	if re.search('playstation', joystick.get_name(), re.I):
		return Ps3Controller(joystick)

	elif re.search('X-box', joystick.get_name(), re.I):
		return XboxController(joystick)

	elif re.search('Saitek', joystick.get_name(), re.I):
		return MySaitekController(joystick)
	
	elif re.search('Thrustmaster dual analog 3.2', joystick.get_name(), re.I):
		return MyThrustController(joystick)
		
	elif re.search('2n1 USB', joystick.get_name(), re.I):
		return CSLController(joystick)

	elif re.search('Joystick', joystick.get_name(), re.I):
		return USBController(joystick)

	return Controller(joystick)

class Controller(object):

	def __init__(self, joystick):
		"""Pass a PyGame joystick instance."""
		self.js = joystick

	def getLeftHori(self):
		return self.js.get_axis(2)

	def getLeftVert(self):
		return self.js.get_axis(3)

	def getRightHori(self):
		return self.js.get_axis(0)

	def getRightVert(self):
		return self.js.get_axis(1)

	def getLeftTrigger(self):
		return self.js.get_button(9)

	def getRightTrigger(self):
		return self.js.get_button(2)

class XboxController(Controller):

	def __init__(self, joystick):
		super(XboxController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(3)

	def getRightVert(self):
		return self.js.get_axis(4)

	def getLeftTrigger(self):
		return self.js.get_axis(2)

	def getRightTrigger(self):
		return self.js.get_button(11)

class Ps3Controller(Controller):

#up  4 _DOWN   6 left  7 right 5 croix  14 rond 13 triangle 12

	def __init__(self, joystick):
		super(Ps3Controller, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(2)

	def getRightVert(self):
		return self.js.get_axis(3)

	def getLeftTrigger(self):
		# TODO: Verify
		return self.js.get_button(8)

	def getRightTrigger(self):
		# TODO: Verify
		return self.js.get_button(9)

	def getUp(self):
		return self.js.get_button(4)

	def getDown(self):
		return self.js.get_button(6)

	def getLeft(self):
		return self.js.get_button(7)

	def getRight(self):
		return self.js.get_button(5)

	def getFire1(self):
		return self.js.get_button(14)

	def getFire2(self):
		return self.js.get_button(13)


class MySaitekController(Controller):

	def __init__(self, joystick):
		super(MySaitekController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(3)

	def getRightVert(self):
		return self.js.get_axis(2)

	def getLeftTrigger(self):
		return self.js.get_button(6)

	def getRightTrigger(self):
		return self.js.get_button(7)

class MyThrustController(Controller):

	def __init__(self, joystick):
		super(MyThrustController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(0)

	def getLeftVert(self):
		return self.js.get_axis(1)

	def getRightHori(self):
		return self.js.get_axis(2)

	def getRightVert(self):
		return self.js.get_axis(3)

	def getLeftTrigger(self):
		return self.js.get_button(5)

	def getRightTrigger(self):
		return self.js.get_button(7)


class CSLController(Controller):

	def __init__(self, joystick):
		super(CSLController, self).__init__(joystick)

	def getLeftHori(self):
		return self.js.get_axis(2)

	def getLeftVert(self):
		return self.js.get_axis(3)

	def getRightHori(self):
		return self.js.get_axis(0)

	def getRightVert(self):
		return self.js.get_axis(1)

	def getLeftTrigger(self):
		return self.js.get_button(6)

	def getRightTrigger(self):
		return self.js.get_button(7)

	def getFire1(self):
		return self.js.get_button(2)

	def getFire2(self):
		return self.js.get_button(1)

class USBController(Controller):


# my USB Joystick 
#up  axis 0 -1 DOWN axis 0 1 left axis 1 1 right axis 1 -1 bouton gauche 10 bouton droite 9

	def __init__(self, joystick):
		super(USBController, self).__init__(joystick)


	def getUp(self):
		if self.js.get_axis(0) == -1:
			return  1
		else:
			return 0

	def getDown(self):
		if self.js.get_axis(0) > 0.9:
			return  1
		else:
			return 0

	def getLeft(self):
		if self.js.get_axis(1) == 1:
			return  1
		else:
			return 0

	def getRight(self):
		if self.js.get_axis(1) == -1:
			return  1
		else:
			return 0

	def getLeftTrigger(self):
		return self.js.get_button(10)

	def getRightTrigger(self):
		return self.js.get_button(9)

	def getFire1(self):
		if self.js.get_button(10) == 1:
			print "fire 1"
		return self.js.get_button(10)

	def getFire2(self):
		if self.js.get_button(9) == 1:
			print "fire 2"
		return self.js.get_button(9)

