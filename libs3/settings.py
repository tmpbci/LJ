#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''
LJay/LJ
v0.7.0

Settings Handler

LICENCE : CC
'''

import configparser
from libs3 import gstt
import ast
import numpy as np


def Write(): 

	config.set('General', 'lasernumber', str(gstt.LaserNumber))
	config.set('General', 'ljayserverip', str(gstt.LjayServerIP))
	config.set('General', 'wwwip', str(gstt.wwwIP))
	config.set('General', 'bhoroscip', str(gstt.oscIPin))
	config.set('General', 'nozoscip', str(gstt.nozoscIP))
	config.set('General', 'debug', str(gstt.debug))
	config.set('General', 'autostart', gstt.autostart)

	for i in range(gstt.LaserNumber):
		laser = 'laser' + str(i)
		config.set(laser, 'ip', str(gstt.lasersIPS[i]))
		config.set(laser, 'type', str(gstt.lasertype[i]))
		config.set(laser, 'kpps', str(gstt.kpps[i]))
		config.set(laser, 'centerx', str(gstt.centerX[i]))
		config.set(laser, 'centery', str(gstt.centerY[i]))
		config.set(laser, 'zoomx', str(gstt.zoomX[i]))
		config.set(laser, 'zoomy', str(gstt.zoomY[i]))
		config.set(laser, 'sizex', str(gstt.sizeX[i]))
		config.set(laser, 'sizey', str(gstt.sizeY[i]))
		config.set(laser, 'finangle', str(gstt.finANGLE[i]))
		config.set(laser, 'swapx', str(gstt.swapX[i]))
		config.set(laser, 'swapy', str(gstt.swapY[i]))
		config.set(laser, 'warpdest', np.array2string(gstt.warpdest[i], precision=2, separator=',',suppress_small=True))
	config.write(open(gstt.ConfigName,'w'))



def Read(): 
	
	gstt.LaserNumber = config.getint('General', 'lasernumber')
	gstt.LjayServerIP= config.get('General', 'ljayserverip')
	gstt.wwwIP= config.get('General', 'wwwip')
	gstt.oscIPin = config.get('General', 'bhoroscip')
	gstt.nozoscip = config.get('General', 'nozoscip')
	gstt.debug = config.get('General', 'debug')
	gstt.plugins = ast.literal_eval(config.get('plugins', 'plugins'))
	gstt.autostart = config.get('General', 'autostart')


	for i in range(4):
		laser = 'laser' + str(i)
		gstt.lasersIPS[i]= config.get(laser, 'ip')
		gstt.lasertype[i]= config.get(laser, 'type')
		gstt.kpps[i] = config.getint(laser, 'kpps')
		#gstt.lasersPLcolor[i] = config.getint(laser, 'color')
		gstt.centerX[i]= config.getint(laser, 'centerx')
		gstt.centerY[i] = config.getint(laser, 'centery')
		gstt.zoomX[i] = config.getfloat(laser, 'zoomx')
		gstt.zoomY[i] = config.getfloat(laser, 'zoomy')
		gstt.sizeX[i] = config.getint(laser, 'sizex')
		gstt.sizeY[i] = config.getint(laser, 'sizey')
		gstt.finANGLE[i] = config.getfloat(laser, 'finangle')
		gstt.swapX[i] = config.getint(laser, 'swapx')
		gstt.swapY[i] = config.getint(laser, 'swapy')
		gstt.lsteps[i] = ast.literal_eval(config.get(laser, 'lsteps'))
		gstt.warpdest[i]= np.array(ast.literal_eval(config.get(laser, 'warpdest')))


config = configparser.ConfigParser()
config.read(gstt.ConfigName)


