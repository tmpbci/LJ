# coding=UTF-8
"""

LJ OSC and Websockets laser commands
v0.7.0


LICENCE : CC
by Sam Neurohack, Loloster, 
from /team/laser


"""

import types, time
import gstt
import homographyp
import settings
import redis


r = redis.StrictRedis(host=gstt.LjayServerIP , port=6379, db=0)


    
def UserOn(laser):

    print "User for laser ", laser
    r.set('/order/'+str(laser), 0)


def NewEDH(laser):

    print "New EDH requested for laser ", laser
    settings.Write()
    print "Settings saving swapX ", gstt.swapX[laser]
    print "Settings saving swapY ", gstt.swapY[laser]

    homographyp.newEDH(laser)

def BlackOn(laser):

    print "Black for laser ", laser
    r.set('/order/'+str(laser), 2)
    

def GridOn(laser):

    print "Grid for laser ", laser
    r.set('/order/'+str(laser), 3)


def Resampler(laser,lsteps):

    # lsteps is a string like : "[ (1.0, 8),(0.25, 3), (0.75, 3), (1.0, 10)]"
    print "Resampler change for laser ", laser
    r.set('/resampler/' + str(laser), lsteps)
    r.set('/order/'+str(laser), 4)


def LasClientChange(clientnumber):

    # 
    if r.get("/pl/"+str(clientnumber)+"/0") != None:

        print "Switching to laser client", clientnumber
        gstt.LasClientNumber = clientnumber
        r.set('/clientkey', "/pl/"+str(clientnumber)+"/")
        print "clientkey set to", "/pl/"+str(clientnumber)+"/"
        for laserid in xrange(0,gstt.LaserNumber):
            r.set('/order/'+str(laserid), 5)
    else:
        print "ERROR : MaxLasClient is set to ", gstt.MaxLasClient
        

        
def NoteOn(note):
    print "NoteOn", note

    # Change laser client
    if note < 8:
        LasClientChange(note)
    
    # Change PL displayed on webui
    if  note > 23 and note < 32:
        if note - 24 > gstt.LaserNumber -1:
            print "Only",gstt.LaserNumber,"lasers asked, you dum ass !"
        else: 
            gstt.Laser = note -24
            print "Current Laser switched to",gstt.Laser



def handler(oscpath, args):

    print ""
    print "Handler"

    if oscpath[1] == "client" or oscpath[1] =="noteon":
        if oscpath[1] == "client":
            LasClientChange(int(args[0]))
        else:
            NoteOn(int(args[0]))

    else:
        pathlength = len(oscpath)
        if pathlength == 3:
            laser = int(oscpath[2])
        else:
            laser = int(oscpath[3])

    print "args[0] :",args[0]," ", type(args[0])
    
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
            print "Black requested for laser ", laser
            BlackOn(laser)        
        else:
            print "No black for laser ", laser
            UserOn(laser)

    
    # /ip/lasernumber value
    if oscpath[1] == "ip":
        print "New IP for laser ", laser
        gstt.lasersIPS[laser]= args[0]
        settings.Write()


    # /kpps/lasernumber value
    # Live change of kpps is not implemented in newdac.py. Change will effect next startup.
    if oscpath[1] == "kpps":
        print "New kpps for laser ", laser, " next startup", int(args[0])
        gstt.kpps[laser]= int(args[0])
        settings.Write()

    # /angle/lasernumber value 
    if oscpath[1] == "angle":
        print "New Angle modification for laser ", oscpath[2], ":",  float(args[0])
        gstt.finANGLE[laser] += float(args[0])
        NewEDH(laser)
        "New angle", gstt.finANGLE[laser]
        
    # /intens/lasernumber value 
    if oscpath[1] == "intens":
        print "New intensity requested for laser ", laser, ":",  int(args[0])
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
    
        print "swapX was", gstt.swapX[laser]
        if args[0] == "0":
            print "swap X -1 for laser ", laser
            gstt.swapX[laser]= -1
            NewEDH(laser)

        else:
            print "swap X 1 for laser ",  laser
            gstt.swapX[laser]= 1
            NewEDH(laser)

    # /swap/Y/lasernumber value (0 or 1) 
    if oscpath[1] == "swap" and oscpath[2] == "Y":

        print "swapY was", gstt.swapX[laser]
        if args[0] == "0":
            print "swap Y -1 for laser ",  laser
            gstt.swapY[laser]= -1
            NewEDH(laser)
        else:
            print "swap Y 1 for laser ",  laser
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
        if gstt.zoomX[laser] + int(args[0]) > 0:
            gstt.zoomX[laser] += int(args[0])
            print "scale/X laser", laser , "modified to",  gstt.zoomX[laser]
            NewEDH(laser)

    # /scale/Y/lasernumber value
    if oscpath[1] == "scale" and oscpath[2] == "Y":
        if gstt.zoomY[laser] + int(args[0]) > 0:
            gstt.zoomY[laser] += int(args[0])
            print "scale/Y laser",  laser, "modified to",  gstt.zoomY[laser]
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

Code for bit analysis 2 bits / laser to encode order.

    # Grid PL is Laser bit 0 = 1 and bit 1 = 1
    #order = r.get('/order')
    #neworder =  order | (1<<laser*2)
    #neworder =  neworder | (1<< 1+laser*2)
    #r.set('/order', str(neworder))

    # Laser bit 0 = 0 and bit 1 = 0 : USER PL
    #order = r.get('/order')
    #neworder = order & ~(1<< laser*2)
    #neworder = neworder & ~(1<< 1+ laser*2)
    #r.set('/order', str(neworder))  

    # Laser bit 0 = 0 and bit 1 = 1 : New EDH
    #order = r.get('/order')
    #neworder = order & ~(1<< laser*2)
    #neworder =  neworder | (1<< 1+laser*2)
    #r.set('/order', str(neworder))

    # Black PL is Laser bit 0 = 1 and bit 1 = 0 :
    #order = r.get('/order')
    #neworder =  order | (1<<laser*2)
    #neworder =  neworder & ~(1<< 1+laser*2)

'''
