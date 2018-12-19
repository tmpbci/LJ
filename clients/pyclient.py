# coding=UTF-8

'''
Multi Laser client example 

LICENCE : CC
'''

import redis

# IP defined in /etd/redis/redis.conf
redisIP = '127.0.0.1'

r = redis.StrictRedis(host=redisIP, port=6379, db=0)

# (x,y,color in integer) 65280 is color #00FF00 
# Green rectangular shape :
pl0 =  [(100,300,65280),(200,300,65280),(200,200,65280),(100,200,65280)]


# If you want to use rgb for color :
def rgb2int(r,g,b):
    return int('0x%02x%02x%02x' % (r,g,b),0)

# White rectangular shape 
pl1 =  [(100,300,rgb2int(255,255,255)),(200,300,rgb2int(255,255,255)),(200,200,rgb2int(255,255,255)),(100,200,rgb2int(255,255,255))]


# /pl/clientnumber/lasernumber pointlist

# Consider you're client 0
# Send to laser 0 (see mainy.conf)
r.set('/pl/0/0', str(pl0))

# Send to laser 1 (see mainy.conf)
r.set('/pl/0/1', str(pl1))
# Send to laser 2 (see mainy.conf)
r.set('/pl/0/2', str(pl1))

'''
You can also use PolyLineOneColor or rPolylineOneColor to stack n point lists to build a "frame"

import framy

# for laser0 :

pl0 =  [(100,300),(200,300),(200,200),(100,200)]
framy.PolyLineOneColor(pl0, rgb2int(255,255,255), 0 , closed = False)
# You can add as much polylineOneColor as you want = construct a "frame"
# Then send it to the laser server :
print "All one color lines sent to laser 0 :",framy.LinesPL(0) # Will be True is sent correctly

# instead of PolyLineOneColor you can use rPolylineOneColor to send 2D point list around 0,0 with 3D rotation,resizing and repositioning at xpos ypos
# rPolylineOneColor is very useful to add different polylines to different position. Imagine different game elements.
# rPolyLineOneColor(xy_list, c, PL , closed, xpos = 0, ypos =0, resize =1, rotx =0, roty =0 , rotz=0):
# Send the pl0 to laser 1

framy.rPolyLineOneColor((pl0, c = rgb2int(255,255,255),  PL = 1, closed = False, xpos = 200, ypos = 250, resize = 1, rotx =0, roty =0 , rotz=0)
print "All one color lines sent to laser 1 :",framy.LinesPL(1) # Will be True is sent correctly
'''