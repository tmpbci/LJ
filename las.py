# coding=UTF-8
"""

LJ OSC handler
v0.7.0


LICENCE : CC
by Sam Neurohack, Loloster, 
from /team/laser


"""

import types, time
import gstt

#import colorify
import homographyp
import settings
#import alignp
import redis


r = redis.StrictRedis(host=gstt.LjayServerIP , port=6379, db=0)


    
def UserOn(laser):

    print "User for laser ", laser
    r.set('/order/'+str(laser), 0)
    # Laser bit 0 = 0 and bit 1 = 0 : USER PL
    #order = r.get('/order')
    #neworder = order & ~(1<< laser*2)
    #neworder = neworder & ~(1<< 1+ laser*2)
    #r.set('/order', str(neworder))  


def NewEDH(laser):

    print "New EDH requested for laser ", laser
    settings.Write()
    homographyp.newEDH(laser)
    
    #r.set('/order/'+str(laser), 1)
    # Laser bit 0 = 0 and bit 1 = 1 : New EDH
    #order = r.get('/order')
    #neworder = order & ~(1<< laser*2)
    #neworder =  neworder | (1<< 1+laser*2)
    #r.set('/order', str(neworder))

def BlackOn(laser):

    print "Black for laser ", laser
    r.set('/order/'+str(laser), 2)
    # Black PL is Laser bit 0 = 1 and bit 1 = 0 :
    #order = r.get('/order')
    #neworder =  order | (1<<laser*2)
    #neworder =  neworder & ~(1<< 1+laser*2)
    

def GridOn(laser):

    print "Grid for laser ", laser
    r.set('/order/'+str(laser), 3)
    # Grid PL is Laser bit 0 = 1 and bit 1 = 1
    #order = r.get('/order')
    #neworder =  order | (1<<laser*2)
    #neworder =  neworder | (1<< 1+laser*2)
    #r.set('/order', str(neworder))


def Resampler(laser,lsteps):

    # lsteps is a string like : "[ (1.0, 8),(0.25, 3), (0.75, 3), (1.0, 10)]"
    print "Resampler change for laser ", laser
    r.set('/resampler/' + str(laser), lsteps)
    r.set('/order/'+str(laser), 4)


def handler(oscpath, args):

    pathlength = len(oscpath)
    if pathlength == 3:
        laser = int(oscpath[2])
    else:
        laser = int(oscpath[3])

    # /grid/lasernumber value (0 or 1) 
    if oscpath[1] == "grid":
    
        if args[0] == "1":
            print "Grid requested for laser ", laser
            GridOn(laser)     
        else:
            print "No grid for laser ", laser
            UserOn(laser)


    # /black/lasernumber value (0 or 1) 
    if oscpath[1] == "black":
    
        if args[0] == "1":
            print "Grid requested for laser ", laser
            BlackOn(laser)        
        else:
            print "No grid for laser ", laser
            UserOn(laser)


    
    # /ip/lasernumber value
    if oscpath[1] == "ip":
        print "New IP for laser ", laser
        gstt.lasersIPS[laser]= args[0]
        settings.Write()


    # /kpps/lasernumber value
    # Live change of kpps is not implemented in newdac.py. Change will effect next startup.
    if oscpath[1] == "kpps":
        print "New kpps for laser ", laser, " next startup", args[0]
        gstt.kpps[laser]= int(args[0])
        settings.Write()

    # /angle/lasernumber value 
    if oscpath[1] == "angle":
        print "New Angle modification for laser ", oscpath[2], ":",  args[0]
        gstt.finANGLE[laser] += int(args[0])
        NewEDH(laser)
        
    # /intens/lasernumber value 
    if oscpath[1] == "intens":
        print "New intensity requested for laser ", laser, ":",  args[0]
        print "Change not implemented yet"



    # /resampler/lasernumber lsteps
    # lsteps is a string like "[ (1.0, 8),(0.25, 3), (0.75, 3), (1.0, 10)]"
    if oscpath[1] == "resampler":
        Resampler(laser,args[0])
        

    # /mouse/lasernumber value (0 or 1) 
    if oscpath[1] == "mouse":
    
        if args[0] == "1":
            print "Mouse requested for laser ", oscpath[2]
            gstt.Laser = oscpath[2]
        else:
            print "No mouse for laser ",  oscpath[2]


    # /swap/X/lasernumber value (0 or 1) 
    if oscpath[1] == "swap" and oscpath[2] == "X":
    
        if args[0] == "0":
            print "swap X : -1 for laser ", laser
            gstt.swapX[laser]= -1
            NewEDH(laser)

        else:
            print "swap X : 1 for laser ",  laser
            gstt.swapX[laser]= 1
            NewEDH(laser)

    # /swap/Y/lasernumber value (0 or 1) 
    if oscpath[1] == "swap" and oscpath[2] == "Y":
        if args[0] == "0":
            print "swap Y : -1 for laser ",  laser
            gstt.swapY[laser]= -1
            NewEDH(laser)
        else:
            print "swap Y : 1 for laser ",  laser
            gstt.swapY[laser]= 1
            NewEDH(laser)

    # /loffset/X/lasernumber value
    if oscpath[1] == "loffset" and oscpath[2] == "X":
        print "offset/X laser", laser, "modified to",  args[0]
        gstt.centerX[laser] -=  int(args[0])
        NewEDH(laser)
    
    # /loffset/Y/lasernumber value
    if oscpath[1] == "loffset" and oscpath[2] == "Y":
        print "offset/Y laser", laser, "modified to",  args[0]
        gstt.centerY[laser] -=  int(args[0])
        NewEDH(laser)


    # /scale/X/lasernumber value
    if oscpath[1] == "scale" and oscpath[2] == "X":
        print "scale/X laser", laser , "modified to",  args[0]
        gstt.zoomX[laser] += int(args[0])
        NewEDH(laser)

    # /scale/Y/lasernumber value
    if oscpath[1] == "scale" and oscpath[2] == "Y":
        print "scale/Y laser",  laser, "modified to",  args[0]
        gstt.zoomY[laser] += int(args[0])
        NewEDH(laser)

'''
For reference values of EDH modifier if assign to keyboard keys (was alignp)

        gstt.centerY[gstt.Laser] -= 20

        gstt.centerY[gstt.Laser] += 20

        gstt.zoomX[gstt.Laser]-= 0.1

        gstt.zoomX[gstt.Laser] += 0.1
         gstt.zoomY[gstt.Laser] -= 0.1
       
        gstt.zoomY[gstt.Laser] += 0.1
        
        gstt.sizeX[gstt.Laser] -= 50
        
        gstt.sizeX[gstt.Laser] += 50
        
        gstt.sizeY[gstt.Laser] -= 50
        
        gstt.sizeY[gstt.Laser] += 50
        
        gstt.finANGLE[gstt.Laser] -= 0.001
        
        gstt.finANGLE[gstt.Laser] += 0.001
'''
