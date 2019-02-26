#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''
LJ Laser Server v0.8

Laser server + webUI servers (ws + OSC)

- get point list to draw : /pl/lasernumber
- for report /lstt/lasernumber /lack/lasernumber /cap/lasernumber
- A nice ws debug tool : websocat 

todo :


'''

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

extoscIP = gstt.oscIPin
print "extosc IP :", extoscIP

nozoscIP = gstt.nozoscip
print "Nozosc IP :", nozoscIP

debug = gstt.debug 
print "Debug :", debug

lasernumber = gstt.LaserNumber -1
print "Lasers requested :", gstt.LaserNumber


# Websocket listening port
wsPORT = 9001

# With extosc
# OSC Server : accept OSC message on port 8002 
#oscIPin = "192.168.1.10"s
extoscIPin = serverIP
extoscPORTin = 8002

# OSC Client : to send OSC message to an IP port 8001
extoscIPout = extoscIP 
extoscPORTout = 8001


# With Nozoid
# OSC Client : to send OSC message to Nozoid inport 8003
NozoscIPout = nozoscIP
NozoscPORTout = 8003


# With Planetarium
# OSC Client : to send OSC message to planetarium inport 8005
planetIPout = nozoscIP
planetPORTout = 8005


oscserver = OSCServer( (extoscIPin, extoscPORTin) )
oscserver.timeout = 0
OSCRunning = True


def handle_timeout(self):
    self.timed_out = True

oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)

osclientext = OSCClient()
oscmsg = OSCMessage()
osclientext.connect((extoscIPout, extoscPORTout)) 

# send UI string as OSC message to extosc 8001
# sendextosc(oscaddress, [arg1, arg2,...])

def sendextosc(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    #print ("sending to extosc : ",oscmsg)
    try:
        osclientext.sendto(oscmsg, (extoscIPout, extoscPORTout))
        oscmsg.clearData()
    except:
        print ('Connection to extosc IP', extoscIPout, 'port', extoscPORTout,'refused : died ?')
        sendWSall("/on 0")
        sendWSall("/status NoLJay")
        
    #time.sleep(0.001)


# send UI string as OSC message to Nozosc 8003
# sendnozosc(oscaddress, [arg1, arg2,...])

osclientnozoid = OSCClient()
osclientnozoid.connect((NozoscIPout, NozoscPORTout)) 

def sendnozosc(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    print "Sending OSC to Nozosc server :", oscaddress,'with args', oscargs 
    try:
        osclientnozoid.sendto(oscmsg, (NozoscIPout, NozoscPORTout))
        oscmsg.clearData()
    except:
        print 'Connection to nozosc IP', NozoscIPout,'port', NozoscPORTout,' refused : died ?'
        sendWSall("/on 0")
        sendWSall("/status No Nozosc ")
    
    #time.sleep(0.001)

# send UI string as OSC message to Planet 8005
# sendplanet(oscaddress, [arg1, arg2,...])

osclientplanet = OSCClient()
osclientplanet.connect((planetIPout, planetPORTout)) 

def sendplanet(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    print "Sending OSC to Planet server :", oscaddress,'with args :', oscargs 
    try:
        osclientplanet.sendto(oscmsg, (planetIPout, planetPORTout))
        oscmsg.clearData()
    except:
        print 'OSC send to planet IP', planetIPout, 'port', planetPORTout, "refused : died ?"
        sendWSall("/planet/start 0")
        sendWSall("/status No Planet")
        
    #time.sleep(0.001)

# OSC default path handler : send incoming OSC message to UI via websocket 9001
def handler(path, tags, args, source):

    oscpath = path.split("/")
    print ""
    print "OSC default handler in main said : path", path," oscpath ", oscpath," args", args
    #print "debug", gstt.debug
    #if gstt.debug >0:
    #    print "default handler"
    #    print "OSC said  path", path," oscpath ", oscpath," args", args
    
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



# OSC server Thread : handler, dacs reports and simulator points sender to UI.
def osc_thread():

    while True:
        try:
            while True:

                time.sleep(0.1)
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
                    if gstt.debug >1:
                        print "laserid", laserid, "lack", lack
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
                #print r.get('/pl/'+str(gstt.LasClientNumber)+'/'+str(gstt.Laser))
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


# Called for each ws received message.
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'    

    #if gstt.debug >0:
    #    print ("")
    #    print("WS Client(%d) said: %s" % (client['id'], message))
    
    print("")
   
    oscpath = message.split(" ")
    print "WS Client", client['id'], "said :", message, "splitted in an oscpath :", oscpath

    # If message included "planet" forward the message as OSC to planet IP port 8005
    if oscpath[0].find("planet") != -1:
        if len(oscpath) == 1:
            sendplanet(oscpath[0], oscargs='noargs')
        else:
            sendplanet(oscpath[0], oscargs=oscpath[1])

    # If message included "nozoid" forward the message as OSC to nozoid IP port 8003
    elif oscpath[0].find("nozoid") != -1:
        if len(oscpath) == 1:
            sendnozosc(oscpath[0], oscargs='noargs')
        else:
            sendnozosc(oscpath[0], oscargs=oscpath[1])

     # If message included "ai" do something
    elif oscpath[0].find("ai") != -1:
        print "ai order ", oscpath

    # If message included "lissa" do something
    elif oscpath[0].find("lissa") != -1:
        print "lissa order ", oscpath

     # If message included "vj" do something
    elif oscpath[0].find("vj") != -1:
        print "VJ order ", oscpath

    elif len(oscpath) > 1:
        args[0] = str(oscpath[1]) 
        #print oscpath[0].split("/"),oscpath[1]

    # current UI has no dedicated off button so /on 0 trigs /off to extosc
    elif oscpath[0] == "/on":
        if oscpath[1] == "1":
            sendextosc("/on")
        else:
            sendextosc("/off")

    else:
        args[0] = "noargs"
        commands.handler(oscpath[0].split("/"),args)

    
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
    
    # Launch OSC thread listening to extosc
    print ""
    print "Launching OSC server..."
    print "at", extoscIPin, "port",str(extoscPORTin)
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

print "Fin de LJ."


'''
Some code previously used, for reference :

random_points = [(300.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 0), (500.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 65280), (500.0+random.randint(-100, 100), 400.0+random.randint(-100, 100), 65280), (300.0+random.randint(-100, 100), 400.0+random.randint(-100, 100), 65280), (300.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 65280)]
'''



