# coding=UTF-8
"""

LJ OSC and Websockets laser commands
v0.7.0


LICENCE : CC
by Sam Neurohack, Loloster, 
from /team/laser

Commands reference. Use commands from websocket (webUI) or OSC, do not set values in redis directly except for /pl.

/scale/X/lasernumber value   
/scale/Y/lasernumber value

/client or note on < 8 : change client displayed for Current Laser
23 < /noteon < 32 : PL number displayed on webUI simulator    

/grid/lasernumber value (0 or 1) : switch given laser with grid display on or off

/black/lasernumber value (0 or 1) : set given laser to black on or off

/ip/lasernumber value : change given laser IP i.e '192.168.1.1'

/kpps/lasernumber value
Live change of kpps is not implemented in newdac.py. Change will effect next startup.

/angle/lasernumber value : increase/decrease angle correction for given laser by value

/intens/lasernumber value : increase/decrease intensity for given laser by value 

/resampler/lasernumber lsteps : change resampling strategy (glitch art) for given laser
lsteps is a string like "[ (1.0, 8),(0.25, 3), (0.75, 3), (1.0, 10)]"
 
/mouse/lasernumber value (0 or 1) 

/swap/X/lasernumber value (0 or 1) 
/swap/Y/lasernumber value (0 or 1) 

/loffset/X/lasernumber value : change X offset  of given laser by value
/loffset/Y/lasernumber value : change Y offset of given laser by value

/order value : instruct tracer what to do.

/planet will be forwarded to planetarium client.
/nozoid will be forwarded to nozoid client.

0 : display user pointlist with current client key. See below for client key.
1 : pull in redis a new correction matrix (EDH) 
2 : display black 
3 : display grid
4 : resampler 
5 : pull in redis a new client key


/pl/clientnumber/lasernumber value : value is the pointlist to draw as string type. For string format see code in clients directory.

Example : client 0 send 2 point lists one for laser 0 and one for laser 1 by sending in redis :
/pl/0/0 and /pl/0/1
The "client key" when client 0 is selected to be displayed by lasers is "/pl/0/". 
Each tracer pull its pointlist by using the current client key "/pl/0/" 
and add its laser number at startup : /pl0/0 ant /pl/0/1

"Client" is a concept. Imagine in a demoparty there is 4 lasers. 
John and Paul want to draw on all lasers. 
Let's give John client 0, he will send points to /pl/0/0, /pl/0/1, /pl/0/2 and /pl/0/3.

Paul is client 1, so he will use /pl/1/0, /pl/1/1, /pl/1/2 and /pl/1/3.

Both can send their pointlists to redis server.
When John get the lasers switch to client 0, when it's Paul turn switch to client 1.

But say Bob and Lisa needs only 2 lasers each. Give them client 2. 
Bob could use /pl/2/0 and /pl/2/1 and Lisa could use /pl/2/2 and /pl/2/3.


"""
from __future__ import absolute_import
import types, time
import gstt
import homographyp
import settings
import redis
import plugins


r = redis.StrictRedis(host=gstt.LjayServerIP , port=6379, db=0)

GenericCommands = ["start","ljclient","clientnumber","noteon","pong","mouse","emergency","simu","status","run","nozoid","planet","live","words","ai","bank0","lj"]


    
def UserOn(laser):

    print "User for laser ", laser
    plugins.sendWSall("/status User on laser " + str(laser))
    r.set('/order/'+str(laser), 0)


def NewEDH(laser):

    print "New EDH requested for laser ", laser
    plugins.sendWSall("/status New EDH on laser " + str(laser))
    settings.Write()
    print "Settings saving swapX ", gstt.swapX[laser]
    print "Settings saving swapY ", gstt.swapY[laser]

    homographyp.newEDH(laser)

def BlackOn(laser):

    print "Black for laser ", laser
    plugins.sendWSall("/status Black on laser " + str(laser))
    r.set('/order/'+str(laser), 2)
    

def GridOn(laser):

    print "Grid for laser ", laser
    plugins.sendWSall("/status Grid on laser " + str(laser))
    r.set('/order/'+str(laser), 3)


def Resampler(laser,lsteps):

    # lsteps is a string like : "[ (1.0, 8),(0.25, 3), (0.75, 3), (1.0, 10)]"
    print "Resampler change for laser ", laser
    r.set('/resampler/' + str(laser), lsteps)
    r.set('/order/'+str(laser), 4)


def LasClientChange(clientnumber):

    if r.get("/pl/"+str(clientnumber)+"/0") != None:

        print "Switching to laser client", clientnumber
        gstt.LasClientNumber = clientnumber
        plugins.sendWSall("/status Client " + str(gstt.LasClientNumber) + " laser " + str(gstt.Laser))

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
            plugins.sendWSall("/status Not Enough Laser")

        else: 
            gstt.Laser = note -24
            plugins.sendWSall("/status Client " + str(gstt.LasClientNumber) + " laser " + str(gstt.Laser))
            print "Current Laser switched to", gstt.Laser

def Mouse(x1,y1,x2,y2):
    print "Mouse", x1,y1,x2,y2



def handler(oscpath, args):

    #print ""
    print "OSC handler in commands.py got /"+ str(oscpath)+ " with args :",args

    # 2 incoming cases : generic or specific for a given lasernumber :
    # Generic : Commands without a laser number
    #if oscpath[1] == "client" or oscpath[1]=="clientnumber" or oscpath[1] =="noteon" or oscpath[1]=="pong" or oscpath[1]=="mouse" or oscpath[1]=="emergency" or oscpath[1]=="simu" or oscpath[1]=="status" or oscpath[1]=="run" or oscpath[1]=="nozoid" or oscpath[1]=="planet"  or oscpath[1]=="live"  or oscpath[1]=="planet" :
    
    if oscpath[1] in GenericCommands:   

        if oscpath[1] == "ljclient":
            LasClientChange(int(args[0]))

        elif oscpath[1] == "noteon":
            NoteOn(int(args[0]))

        elif oscpath[1] == "pong":
            print "LJ commands got pong from", args
            plugins.sendWSall("/" + args[0] + "start 1")
            plugins.sendWSall("/status got pong from "+ args[0] +".")
            
        elif oscpath[1] == "mouse":
            Mouse(int(args[0]),int(args[1]),int(args[2]),int(args[3]))
        
        # /emergency value (0 or 1) 
        if oscpath[1] == "emergency":
        
            if args[0] == "1":
                
                for laser in range(gstt.lasernumber):
                    print "Black requested for laser ", laser
                    BlackOn(laser)
                print "EMERGENCY MODE"
                plugins.sendWSall("/status EMERGENCY MODE")   
            else:
                for laser in range(gstt.lasernumber):
                    print "Back to normal for laser ", laser
                    UserOn(laser)

    # Commands with a laser number
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
            print "New angle", gstt.finANGLE[laser]
            
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
