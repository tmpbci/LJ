'''
LJ Laser Server v0.8

Laser server + webUI servers (ws + OSC)

- get point list to draw : /pl/lasernumber
- for report /lstt/lasernumber /lack/lasernumber /cap/lasernumber

todo :


'''
from __future__ import absolute_import
import time
import gstt
import redis


print ""
print ""
print "LJ Laser Servers"
print "v0.8.0"
print ""

import settings
settings.Read()

import cli
settings.Write()
from multiprocessing import Process, Queue, TimeoutError 
import random, ast

import tracer
import homographyp
import commands
import font1


from OSC import OSCServer, OSCClient, OSCMessage
from websocket_server import WebsocketServer
#import socket
import types, thread, time

r = redis.StrictRedis(host=gstt.LjayServerIP , port=6379, db=0)
args =[0,0]


def dac_process(number, pl):
    while True:
        try:
            d = tracer.DAC(number,pl)
            d.play_stream()
        except Exception as e:

            import sys, traceback
            if gstt.debug == 2:
                print '\n---------------------'
                print 'Exception: %s' % e
                print '- - - - - - - - - - -'
                traceback.print_tb(sys.exc_info()[2])
                print "\n"
            pass

        except KeyboardInterrupt:
            sys.exit(0)
 


#
# webUI server
#

print "Laser client number :",gstt.LasClientNumber
serverIP = gstt.LjayServerIP
print "Redis IP :", serverIP

bhoroscIP = gstt.oscIPin
print "Bhorosc IP :", bhoroscIP

nozoscIP = gstt.nozoscip
print "Nozosc IP :", nozoscIP

debug = gstt.debug 
print "Debug :", debug

lasernumber = gstt.LaserNumber -1
print "Lasers requested :", gstt.LaserNumber


# Websocket listening port
wsPORT = 9001

# With Bhorosc
# OSC Server : relay OSC message from Bhorosc outport 8002 to UI
#oscIPin = "192.168.1.10"s
bhoroscIPin = serverIP
bhoroscPORTin = 8002

# OSC Client : relay message from UI to Bhorosc inport 8001
bhoroscIPout = bhoroscIP 
bhoroscPORTout = 8001


# With Nozosc
# OSC Client : relay message from UI to Nozosc inport 8003
NozoscIPout = nozoscIP
NozoscPORTout = 8003


print bhoroscIPin
oscserver = OSCServer( (bhoroscIPin, bhoroscPORTin) )
oscserver.timeout = 0
OSCRunning = True


def handle_timeout(self):
    self.timed_out = True

oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)

osclientbhorosc = OSCClient()
oscmsg = OSCMessage()
osclientbhorosc.connect((bhoroscIPout, bhoroscPORTout)) 

# send UI string as OSC message to Bhorosc 8001
# sendbhorosc(oscaddress, [arg1, arg2,...])

def sendbhorosc(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    #print ("sending to bhorosc : ",oscmsg)
    try:
        osclientbhorosc.sendto(oscmsg, (bhoroscIPout, bhoroscPORTout))
        oscmsg.clearData()
    except:
        print ('Connection to bhorosc refused : died ?')
        sendWSall("/on 0")
        sendWSall("/status NoLJay")
        pass
    #time.sleep(0.001)


# send UI string as OSC message to Nozosc 8003
# sendnozosc(oscaddress, [arg1, arg2,...])

def sendnozosc(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    #print ("sending to nozosc : ",oscmsg)
    try:
        osclientnozosc.sendto(oscmsg, (NozoscIPout, NozoscPORTout))
        oscmsg.clearData()
    except:
        print ('Connection to nozosc refused : died ?')
        sendWSall("/on 0")
        sendWSall("/status No Nozosc ")
        pass
    #time.sleep(0.001)


# OSC default path handler : send OSC message from Bhorosc 8002 to UI via websocket 9001
def handler(path, tags, args, source):

    oscpath = path.split("/")
    print ""
    print "OSC said : ", path, oscpath, args
    #print "debug", gstt.debug
    if gstt.debug >0:
        print ""
        print "default handler"
        print "OSC said : ", path, oscpath, args
    sendWSall(path + " " + str(args[0]))
    commands.handler(oscpath,args)


# RAW OSC Frame available ? 
def osc_frame():
    #print 'oscframe'
    # clear timed_out flag
    oscserver.timed_out = False
    # handle all pending requests then return
    while not oscserver.timed_out:
        oscserver.handle_request()



# OSC Thread. OSC handler and Automated status sender to UI.
def osc_thread():

    while True:
        try:
            while True:

                time.sleep(1)
                osc_frame()
                for laserid in range(0,gstt.LaserNumber):           # Laser not used -> led is not lit

                    lstt = r.get('/lstt/'+ str(laserid))
                    #print "laserid", laserid,"lstt",lstt
                    if lstt == "0":                              # Dac IDLE state(0) -> led is blue (3)
                        sendWSall("/lstt/" + str(laserid) + " 3")
                    if lstt == "1":                              # Dac PREPARE state (1) -> led is cyan (2)
                        sendWSall("/lstt/" + str(laserid) + " 2")
                    if lstt == "2":                              # Dac PLAYING (2) -> led is green (1)
                        sendWSall("/lstt/" + str(laserid) + " 1")
                
                    
                    lack= r.get('/lack/'+str(laserid))
                    if gstt.debug >0:
                        print "laserid", laserid,"lack",lack
                    if lack == 'a':                             # Dac sent ACK ("a") -> led is green (1)
                        sendWSall("/lack/" + str(laserid) +" 1")
                    if lack == 'F':                             # Dac sent FULL ("F") -> led is orange (5)
                        sendWSall("/lack/" + str(laserid) +" 5")
                    if lack == 'I':                             # Dac sent INVALID ("I") -> led is yellow (4)
                        sendWSall("/lack/" + str(laserid)+" 4")
                    #print lack
                    
                    if lack == "64" or lack =="35":           # no connection to dac -> leds are red (6)
                        sendWSall("/lack/" + str(laserid) + " 0")   
                        sendWSall("/lstt/" + str(laserid) + " 0")  
                        #sendWSall("/lstt/" + str(laserid) + " 0")  
                        sendWSall("/points/" + str(laserid) + " 0")
                        
                    else:
                        # last number of points sent to etherdream buffer
                        sendWSall("/points/" + str(laserid) + " " + str(r.get('/cap/'+str(laserid))))

                #print "Sending simu frame from",'/pl/'+str(gstt.LasClientNumber)+'/'+str(gstt.Laser)
                sendWSall("/simul" +" "+ r.get('/pl/'+str(gstt.LasClientNumber)+'/'+str(gstt.Laser)))


        except Exception as e:
            import sys, traceback
            print '\n---------------------'
            print 'Exception: %s' % e
            print '- - - - - - - - - - -'
            traceback.print_tb(sys.exc_info()[2])
            print "\n"



#
# Websocket part
# 

# Called for every WS client connecting (after handshake)
def new_client(client, server):

    print("New WS client connected and was given id %d" % client['id'])
    sendWSall("/status Hello %d" % client['id'])

    for laserid in range(0,gstt.LaserNumber):    
        sendWSall("/ip/" + str(laserid) + " " + str(gstt.lasersIPS[laserid]))
        sendWSall("/kpps/" + str(laserid)+ " " + str(gstt.kpps[laserid]))

        if gstt.swapX[laserid] == 1:
            sendWSall("/swap/X/" + str(laserid)+ " 1")
        else:
            sendWSall("/swap/X/" + str(laserid)+ " 0")

        if gstt.swapY[laserid] == 1:
            sendWSall("/swap/Y/" + str(laserid)+ " 1")
        else:
            sendWSall("/swap/Y/" + str(laserid)+ " 0")

# Called for every WS client disconnecting
def client_left(client, server):
    print("WS Client(%d) disconnected" % client['id'])


# Called when a WS client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'    

    if gstt.debug >0:
        print ("")
        print("WS Client(%d) said: %s" % (client['id'], message))
    
    print("WS Client(%d) said: %s" % (client['id'], message))
    oscpath = message.split(" ")
    args[0] = str(oscpath[1]) 
    #print oscpath[0].split("/"),oscpath[1]
    commands.handler(oscpath[0].split("/"),args)
    
    # current UI has no dedicated off button so /on 0 trigs /off to bhorosc
    if oscpath[0] == "/on":
        if oscpath[1] == "1":
            sendbhorosc("/on")
        else:
            sendbhorosc("/off")
    
    # if needed a loop back : WS Client -> server -> WS Client
    #sendWSall("ws"+message)


def handle_timeout(self):
    self.timed_out = True


def sendWSall(message):
    #if gstt.debug >0:
        #print("WS sending %s" % (message))
    server.send_message_to_all(message)
    


# Creating a startup point list for each client : 0,1,2,...

print ""
for clientid in range(0,gstt.MaxLasClient):
    print "Creating startup point lists for client",clientid,"..."
    digit_points = font1.DigitsDots(clientid,65280)

    # Order all lasers to show the laser client number at startup -> tell all 4 laser process to USER PLs
    for laserid in range(0,gstt.LaserNumber):

        if r.set('/pl/'+str(clientid)+'/'+str(laserid), str(digit_points)) == True:
            print "/pl/"+str(clientid)+"/"+str(laserid)+" ", ast.literal_eval(r.get('/pl/'+str(clientid)+'/'+str(laserid)))

        r.set('/order/'+str(laserid), 0)

if r.set("/clientkey","/pl/"+str(gstt.LasClientNumber)+"/")==True:
    print "sent clientkey : /pl/"+str(gstt.LasClientNumber)+"/"

print ""
print "Etherdream connection check is NOT DISPLAYED"

# Launch one process (a newdacp instance) by etherdream

print ""
dac_worker0= Process(target=dac_process,args=(0,0))
print "Launching Laser 0 Process..."
dac_worker0.start()

if lasernumber >0:
    dac_worker1= Process(target=dac_process,args=(1,0))
    print "Launching Laser 1 Process..."
    dac_worker1.start()

if lasernumber >1:
    dac_worker2= Process(target=dac_process,args=(2,0))
    print "Launching Laser 2 Process..."
    dac_worker2.start()

if lasernumber >2:
    dac_worker3= Process(target=dac_process,args=(3,0))
    print "Launching Laser 3 Process..."
    dac_worker3.start()

# Main loop do nothing. Maybe do the webui server ?
try:
    #while True:
    
    # Websocket startup
    server = WebsocketServer(wsPORT,host=serverIP)
    
    # Launch OSC thread listening to Bhorosc
    print ""
    print "Launching OSC server..."
    print "at", bhoroscIPin, "port",str(bhoroscPORTin)
    print "Will update webUI dac status every second"
    oscserver.addMsgHandler( "/noteon", commands.NoteOn )
    # Default OSC handler for all OSC incoming message
    oscserver.addMsgHandler("default", handler)
    thread.start_new_thread(osc_thread, ())
    


    #print server
    print ""
    print "Launching webUI Websocket server..."
    print "at", serverIP, "port",wsPORT
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    print ""
    print "Resetting all Homographies.."
    for laserid in range(0,gstt.LaserNumber):  
        homographyp.newEDH(laserid)
        
    print ""
    print "ws server running forver..."
    server.run_forever()


except KeyboardInterrupt:
    pass

# Gently stop on CTRL C

finally:

    dac_worker0.join()
    if lasernumber >0:
        dac_worker1.join()
    if lasernumber >1:
        dac_worker2.join()
    if lasernumber >2:
        dac_worker3.join()


    for laserid in range(0,lasernumber+1):
        print "Laser",laserid,"feedbacks reset."
        r.set('/lack/'+str(laserid),64)
        r.set('/lstt/'+str(laserid),64)
        r.set('/cap/'+str(laserid),0)

print "Fin des haricots"


'''
Some code previously used, for reference :

random_points = [(300.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 0), (500.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 65280), (500.0+random.randint(-100, 100), 400.0+random.randint(-100, 100), 65280), (300.0+random.randint(-100, 100), 400.0+random.randint(-100, 100), 65280), (300.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 65280)]
'''



