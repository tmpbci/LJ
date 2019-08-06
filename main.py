#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''
LJ Laser Server v0.8.1

Inspiration for new WebUI icon menu :
https://codepen.io/AlbertFeynman/pen/mjXeMV

Laser server + webUI servers (ws + OSC)

- get point list to draw : /pl/lasernumber
- for report /lstt/lasernumber /lack/lasernumber /cap/lasernumber
- A nice ws debug tool : websocat 
- a "plugin" is a generator that send points to LJ. Plugins if they have an open OSC port can be checked and restart if in the same computer. 

Todo : 

- If no plugin ping is not received, restart the plugin.
- upgrade to python3


All used ports: 

8002 OSC incoming
9001 WS communication with WebGUI 
Plugins OSC Ports (see LJ.conf)

'''


print ""
print ""
print "LJ Laser Server"
print "v0.8.2"
print ""

import redis

from libs import gstt, settings
settings.Read()

# Arguments may alter .conf file so import settings first then cli
from libs import cli

settings.Write()

from multiprocessing import Process, Queue, TimeoutError 
import random, ast

from libs import plugins, tracer, homographyp, commands, font1

import subprocess
import sys
import os
#import midi

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

print "Laser client number :",gstt.SceneNumber
serverIP = gstt.LjayServerIP
print "Redis IP :", serverIP

oscserverIP = gstt.oscIPin
print "OSCserver IP :", oscserverIP

nozoscIP = gstt.nozoscip
print "Nozosc IP :", nozoscIP

debug = gstt.debug 
print "Debug :", debug

lasernumber = gstt.LaserNumber -1
print "Lasers requested :", gstt.LaserNumber


# Websocket listening port
wsPORT = 9001

# oscserver
# OSC Server : accept OSC message on port 8002 
#oscIPin = "192.168.1.10"s
oscserverIPin = serverIP

print "oscserverIPin", oscserverIPin
oscserverPORTin = 8002

# OSC Client : to send OSC message to an IP port 8001
oscserverIPout = oscserverIP 
oscserverPORTout = 8001


# Nozoid OSC Client : to send OSC message to Nozoid inport 8003
NozoscIPout = nozoscIP
NozoscPORTout = plugins.Port("nozoid")


# Planetarium OSC Client : to send OSC message to planetarium inport 8005
planetIPout = nozoscIP
planetPORTout = plugins.Port("planet")

# Bank0 OSC Client : to send OSC message to bank0 inport 8010
bank0IPout = nozoscIP
bank0PORTout = plugins.Port("bank0")


oscserver = OSCServer( (oscserverIPin, oscserverPORTin) )
oscserver.timeout = 0
OSCRunning = True


def handle_timeout(self):
    self.timed_out = True

oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# OSC default path handler : send incoming OSC message to UI via websocket 9001
def handler(path, tags, args, source):

    oscpath = path.split("/")
    if gstt.debug > 0:
        print ""
        print "OSC handler in main said : path", path," oscpath ", oscpath," args", args

    if oscpath[1] != "pong":
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

def PingAll():

    print ("Pinging all plugins...")
    for plugin in gstt.plugins.keys():

        print("pinging", plugin)
        #sendWSall("/"+ plugin + "/start 0")
        plugins.Ping(plugin)



# OSC server Thread : handler, dacs reports and simulator points sender to UI.
def osc_thread():

    #while True:
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

                #print "Sending simu frame from",'/pl/'+str(gstt.SceneNumber)+'/'+str(gstt.Laser)
                #print r.get('/pl/'+str(gstt.SceneNumber)+'/'+str(gstt.Laser))
                sendWSall("/simul" +" "+ r.get('/pl/'+str(gstt.SceneNumber)+'/'+str(gstt.Laser)))


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
def new_client(client, wserver):

    print("New WS client connected and was given id %d" % client['id'])
    sendWSall("/status Hello %d" % client['id'])

    for laserid in range(0,gstt.LaserNumber):    

        sendWSall("/ip/" + str(laserid) + " " + str(gstt.lasersIPS[laserid]))
        sendWSall("/kpps/" + str(laserid)+ " " + str(gstt.kpps[laserid]))
        sendWSall("/laser"+str(laserid)+"/start 1")

        if gstt.swapX[laserid] == 1:
            sendWSall("/swap/X/" + str(laserid)+ " 1")
        else:
            sendWSall("/swap/X/" + str(laserid)+ " 0")

        if gstt.swapY[laserid] == 1:
            sendWSall("/swap/Y/" + str(laserid)+ " 1")
        else:
            sendWSall("/swap/Y/" + str(laserid)+ " 0")

# Called for every WS client disconnecting
def client_left(client, wserver):
    print("WS Client(%d) disconnected" % client['id'])


# Called for each WS received message.
def message_received(client, wserver, message):

    if len(message) > 200:
        message = message[:200]+'..'    

    #if gstt.debug >0:
    #    print ("")
    #    print("WS Client(%d) said: %s" % (client['id'], message))
    
    print("")
   
    oscpath = message.split(" ")
    if gstt.debug > 0:
        print "WS Client", client['id'], "said :", message, "splitted in an oscpath :", oscpath
    
    PingAll()
    message4plugin = False

    # WS received Message is for a plugin ?

    for plugin in gstt.plugins.keys():
    
        if oscpath[0].find(plugin) != -1:
    
            message4plugin = True
            if plugins.Send(plugin,oscpath):
                print "message sent correctly to", plugin
            else:
                print"plugin was offline"


    # WS received message is an LJ command 

    if message4plugin == False:

        if len(oscpath) == 1:
            args[0] = "noargs"
            #print "noargs command"
    
    
        elif len(oscpath) > 1:
            args[0] = str(oscpath[1]) 
            #print "arg",oscpath[1]
        
        commands.handler(oscpath[0].split("/"),args)
    
    print ""
    
 
    # if needed a loop back : WS Client -> server -> WS Client
    #sendWSall("ws"+message)


def handle_timeout(self):
    self.timed_out = True


def sendWSall(message):
    #if gstt.debug >0:
        #print("WS sending %s" % (message))
    wserver.send_message_to_all(message)
 
'''   
print ""
print "Midi Configuration"
midi.InConfig()
midi.OutConfig()
'''

# Creating a startup point list for each client : 0,1,2,...

print ""
for clientid in range(0,gstt.MaxScenes+1):
    print "Creating startup point lists for client",clientid,"..."
    digit_points = font1.DigitsDots(clientid,65280)

    # Order all lasers to show the laser client number at startup -> tell all 4 laser process to USER PLs
    for laserid in range(0,gstt.LaserNumber):

        if r.set('/pl/'+str(clientid)+'/'+str(laserid), str(digit_points)) == True:
            print "/pl/"+str(clientid)+"/"+str(laserid)+" ", ast.literal_eval(r.get('/pl/'+str(clientid)+'/'+str(laserid)))

        r.set('/order/'+str(laserid), 0)

if r.set("/clientkey","/pl/"+str(gstt.SceneNumber)+"/")==True:
    print "sent clientkey : /pl/"+str(gstt.SceneNumber)+"/"

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
    wserver = WebsocketServer(wsPORT,host=serverIP)
    plugins.Init(wserver)
    
    # Launch OSC thread listening to oscserver
    print ""
    print "Launching OSC server..."
    print "at", oscserverIPin, "port",str(oscserverPORTin)
    print "Will update webUI dac status every second"
    oscserver.addMsgHandler( "/noteon", commands.NoteOn )
    # Default OSC handler for all OSC incoming message
    oscserver.addMsgHandler("default", handler)
    thread.start_new_thread(osc_thread, ())
    


    #print wserver
    print ""
    print "Launching webUI Websocket server..."
    print "at", serverIP, "port",wsPORT
    wserver.set_fn_new_client(new_client)
    wserver.set_fn_client_left(client_left)
    wserver.set_fn_message_received(message_received)
    print ""
    print "Resetting all Homographies.."
    for laserid in range(0,gstt.LaserNumber):  
        homographyp.newEDH(laserid)
    print ""
    print "WS server running forever..."
    wserver.run_forever()


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



