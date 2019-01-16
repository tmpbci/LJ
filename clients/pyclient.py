# coding=UTF-8

'''
Multi Laser client example with direct send of point lists to redis server.

Remember : LJ will automatically warp geometry according to alignement data. See webUI.  

LICENCE : CC
'''

import redis

# IP defined in /etd/redis/redis.conf
redisIP = '127.0.0.1'

r = redis.StrictRedis(host=redisIP, port=6379, db=0)

# (x,y,color in integer) 65280 is color #00FF00 
# Green rectangular shape :
pl0 =  [(100,300,65280),(200,300,65280),(200,200,65280),(100,200,65280),(100,300,65280)]


# If you want to use rgb for color :
def rgb2int(r,g,b):
    return int('0x%02x%02x%02x' % (r,g,b),0)

# White rectangular shape 
pl1 =  [(100,300,rgb2int(255,255,255)),(200,300,rgb2int(255,255,255)),(200,200,rgb2int(255,255,255)),(100,200,rgb2int(255,255,255)),(100,300,rgb2int(255,255,255))]


# /pl/clientnumber/lasernumber pointlist

# Consider you're client 0
# Send to laser 0 (see LJ.conf)
r.set('/pl/0/0', str(pl0))

# Send to laser 1 (see LJ.conf)
r.set('/pl/0/1', str(pl1))
# Send to laser 2 (see LJ.conf)
r.set('/pl/0/2', str(pl1))

