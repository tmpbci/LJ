#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''
LJ Laser Server v0.8.2

Inspiration for a future WebUI icon menu :
https://codepen.io/AlbertFeynman/pen/mjXeMV

Laser server + webUI servers (ws + OSC)

- get point list to draw : /pl/lasernumber
- for report /lstt/lasernumber /lack/lasernumber /cap/lasernumber
- a nice ws debug tool : websocat 
- a "plugin" is a generator that send points to LJ. Plugins if they have an open OSC port can be checked and restart if in the same computer. 


All used ports: 

8002 OSC incoming
9001 Websocket communication with WebGUI 
Plugins OSC Ports (see LJ.conf)

'''
#import pdb

from libs3 import log
print("")
print("")
log.infog("LJ Laser Server")
log.infog("v0.8.2")
print("")
print("-h will display help")
print("")

import redis
import os
ljpath = r'%s' % os.getcwd().replace('\\','/')


import sys

#sys.path.append('libs3/')

from libs3 import gstt, settings
gstt.ljpath= ljpath

log.info("Reading " + gstt.ConfigName + " setup file...")
settings.Read()

# Arguments may alter .conf file so import settings first then cli
from libs3 import cli

settings.Write()

from multiprocessing import Process, set_start_method
import random, ast

from libs3 import plugins

from libs3 import tracer3 as tracer 
from libs3 import homographyp, commands, font1
#from webui import build

#import subprocess

import os
#import midi

from libs3 import OSC3 
from websocket_server import WebsocketServer
#import socket
import types, _thread, time



r = redis.StrictRedis(host=gstt.LjayServerIP , port=6379, db=0)
# r = redis.StrictRedis(host=gstt.LjayServerIP , port=6379, db=0, password='-+F816Y+-')
args =[0,0]


def dac_process(number, pl):

    import sys
    from libs3 import gstt

    print("Starting dac process", number)

    while True:
        try:
            d = tracer.DAC(number,pl)
            d.play_stream()

        except Exception as e:

            import sys
            import traceback

            if gstt.debug > 0:
                log.err('\n---------------------')
                log.err('Exception: %s' % e)
                log.err('- - - - - - - - - - -')
                traceback.print_tb(sys.exc_info()[2])
                print("\n")
            pass

        except KeyboardInterrupt:
            sys.exit(0)
 


#
# Servers init variables
#

print("Start Scene number :",gstt.SceneNumber)

print("WebUI connect to :", gstt.wwwIP)

serverIP = gstt.LjayServerIP
print("Redis IP :", serverIP)

oscserverIP = gstt.oscIPin
print("OSCserver IP :", oscserverIP)

nozoscIP = gstt.nozoscip
print("Nozosc IP :", nozoscIP)

debug = gstt.debug 
print("Debug :", debug)


# Websocket listening port
wsPORT = 9001

# oscserver
# OSC Server : accept OSC message on port 8002 
#oscIPin = "192.168.1.10"s
oscserverIPin = serverIP

print("oscserverIPin", oscserverIPin)
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

'''
# Bank0 OSC Client : to send OSC message to bank0 inport 8010
bank0IPout = nozoscIP
bank0PORTout = plugins.Port("bank0")
'''


#
# DACs available checks ?
#


import socket

#retry = 1
#delay = 1


#
# OSC
#

oscserver = OSC3.OSCServer( (oscserverIPin, oscserverPORTin) )
oscserver.timeout = 0
OSCRunning = True


def handle_timeout(self):
    self.timed_out = True

oscserver.handle_timeout = types.MethodType(handle_timeout, oscserver)


# OSC default path handler : send incoming OSC message to UI via websocket 9001
def handler(path, tags, args, source):

    oscpath = path.split("/")
    if gstt.debug > 0:
        print("")
        print("OSC handler in main said : path", path," oscpath ", oscpath," args", args)

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

    if gstt.debug > 0:
        print("Pinging all plugins...")
        
    for plugin in list(gstt.plugins.keys()):
        if gstt.debug > 0:
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

                    lstate = {'0': 'IDLE', '1': 'PREPARE', '2': "PLAYING", '64': "NOCONNECTION ?" }
                    lstt = r.get('/lstt/'+ str(laserid)).decode('ascii')
                    #print ("laserid", laserid,"lstt",lstt, type(lstt))
                    if gstt.debug >1:
                        print("DAC", laserid, "is in (lstt) :", lstt , lstate[str(lstt)])
                    if lstt == "0":                                 # Dac IDLE state(0) -> led is blue (3)
                        sendWSall("/lstt/" + str(laserid) + " 3")

                    if lstt == "1":                                 # Dac PREPARE state (1) -> led is cyan (2)
                        sendWSall("/lstt/" + str(laserid) + " 2")

                    if lstt == "2":                                 # Dac PLAYING (2) -> led is green (1)
                        sendWSall("/lstt/" + str(laserid) + " 1")
                

                    ackstate = {'61': 'ACK', '46': 'FULL', '49': "INVALID", '21': 'STOP', '64': "NOCONNECTION ?", '35': "NOCONNECTION ?" , '97': 'ACK', '70': 'FULL', '73': "INVALID", '33': 'STOP', '100': "NOCONNECTION", '48': "NOCONNECTION", 'a': 'ACK', 'F': 'FULL', 'I': "INVALID", '!': 'STOP', 'd': "NOCONNECTION", '0': "NOCONNECTION"}
                    lack= r.get('/lack/'+str(laserid)).decode('ascii')

                    if gstt.debug >1:
                        print("DAC", laserid, "answered (lack):", lack, chr(int(lack)), ackstate[str(lack)])

                    if chr(int(lack)) == 'a':                       # Dac sent ACK ("a") -> led is green (1)
                        sendWSall("/lack/" + str(laserid) +" 1")

                    if chr(int(lack)) == 'F':                       # Dac sent FULL ("F") -> led is orange (5)
                        sendWSall("/lack/" + str(laserid) +" 5")

                    if chr(int(lack)) == 'I':                       # Dac sent INVALID ("I") -> led is yellow (4)
                        sendWSall("/lack/" + str(laserid)+" 4")
                    #print lack
                    
                    if lack == "64" or lack =="35":                 # no connection to dac -> leds are red (6)
                        sendWSall("/lack/" + str(laserid) + " 6")   
                        sendWSall("/lstt/" + str(laserid) + " 6")  
                        #sendWSall("/lstt/" + str(laserid) + " 0")  
                        sendWSall("/points/" + str(laserid) + " 6")
                        
                    else:
                        # last number of points sent to etherdream buffer
                        sendWSall("/points/" + str(laserid) + " " + str(r.get('/cap/'+str(laserid)).decode('ascii')))

                #print "Sending simu frame from",'/pl/'+str(gstt.SceneNumber)+'/'+str(gstt.Laser)
                #print r.get('/pl/'+str(gstt.SceneNumber)+'/'+str(gstt.Laser))
                sendWSall("/simul" +" "+ str(r.get('/pl/'+str(gstt.SceneNumber)+'/'+str(gstt.Laser)).decode('ascii')))


        except Exception as e:
            import sys, traceback
            print('\n---------------------')
            print('Exception: %s' % e)
            print('- - - - - - - - - - -')
            traceback.print_tb(sys.exc_info()[2])
            print("\n")

#
# Websocket part
# 

# Called for every WS client connecting (after handshake)
def new_client(client, wserver):

    print("New WS client connected and was given id %d" % client['id'])
    sendWSall("/status Hello " + str(client['id']))

    for laserid in range(0,gstt.LaserNumber):    

        sendWSall("/ip/" + str(laserid) + " " + str(gstt.lasersIPS[laserid]))
        sendWSall("/kpps/" + str(laserid)+ " " + str(gstt.kpps[laserid]))
        #sendWSall("/laser"+str(laserid)+"/start 1")
        sendWSall("/laser "+str(laserid))
        #print("/laser "+str(laserid))
        sendWSall("/lack/" + str(laserid) + " 6")
        #print("/lack/" + str(laserid) + " 6") 
        sendWSall("/lstt/" + str(laserid) + " 6")  
        #print("/lstt/" + str(laserid) + " 6")
        sendWSall("/points/" + str(laserid) + " 0")
        #print("/points/" + str(laserid) + " 0")

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

    #if len(message) > 200:
    #    message = message[:200]+'..'    

    #if gstt.debug >0:
    #    print ("")
    #    print("WS Client(%d) said: %s" % (client['id'], message))
    
    oscpath = message.split(" ")
    #print "WS Client", client['id'], "said :", message, "splitted in an oscpath :", oscpath
    if gstt.debug > 0:
        print("WS Client", client['id'], "said :", message, "splitted in an oscpath :", oscpath)
    
    PingAll()
    message4plugin = False

    # WS received Message is for a plugin ?

    for plugin in list(gstt.plugins.keys()):
    
        if oscpath[0].find(plugin) != -1:
    
            message4plugin = True
            #print(oscpath)
            if plugins.Send(plugin, oscpath):
                print("plugins sent incoming WS correctly to", plugin)
            else:
                print("plugins detected", plugin, "offline.")


    # WS received message is an LJ command 

    if message4plugin == False:

        if len(oscpath) == 1:
            args[0] = "noargs"
            #print "noargs command"
    
        elif len(oscpath) > 1:
            args[0] = str(oscpath[1]) 
            #print "arg",oscpath[1]
        
        commands.handler(oscpath[0].split("/"),args)
    

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

# Creating a startup point list for each laser : 0,1,2,...

print("")
log.info("Creating startup point lists...")


if r.set("/clientkey","/pl/"+str(gstt.SceneNumber)+"/")==True:
    print("sent clientkey : /pl/"+str(gstt.SceneNumber)+"/")
    
#pdb.set_trace()
for sceneid in range(0,gstt.MaxScenes+1):
    print("Scene "+ str(sceneid))
    #digit_points = font1.DigitsDots(sceneid,65280)

    # Order all lasers to show the laser client number at startup -> tell all 4 laser process to USER PLs
    for laserid in range(0,gstt.LaserNumber):

        digit_points = font1.DigitsDots(laserid,65280)
        if r.set('/pl/'+str(sceneid)+'/'+str(laserid), str(digit_points)) == True:
            pass
            #print( ast.literal_eval(r.get('/pl/'+str(sceneid)+'/'+str(laserid)).decode('ascii')))
            #print("/pl/"+str(sceneid)+"/"+str(laserid)+" "+str(ast.literal_eval(r.get('/pl/'+str(sceneid)+'/'+str(laserid)).decode('ascii'))))

        r.set('/order/'+str(laserid), 0)

#
# Starts one DAC process per requested Laser
#

def fff(name):
        print()
        print('HELLO', name ) #indent
        print()

if __name__ == '__main__':

    # Bug in 3.8.4 MacOS default multiprocessing start method is spawn. Spawn doesn't work properly
    set_start_method('fork')

    print("")
    if gstt.LaserNumber == -1:
        log.infog("Autodetected DACs mode")
        commands.DAChecks()
        print("dacs", gstt.dacs)

    else: 
        log.infog("Resquested DACs mode")

    lasernumber = gstt.LaserNumber -1
    print("LaserNumber = ", gstt.LaserNumber)

    
    log.info("Starting "+str(gstt.LaserNumber) + " DACs process...")
    
    # Launch one process (a newdacp instance) by etherdream
    dac_worker0= Process(target=dac_process, args=(0,0,))
    dac_worker0.start()
    print("Tracer 0 : name", dac_worker0.name , "pid", dac_worker0.pid )
    
    if lasernumber >0:
        dac_worker1= Process(target=dac_process, args=(1,0,))
        print("Tracer 1 : name", dac_worker1.name , "pid", dac_worker1.pid )
        dac_worker1.start()
    
    if lasernumber >1:
        dac_worker2= Process(target=dac_process, args=(2,0,))
        dac_worker2.start()
        print("Tracer 2 : name", dac_worker2.name , "pid", dac_worker2.pid )
    
    if lasernumber >2:
        dac_worker3= Process(target=dac_process, args=(3,0,))
        print("Tracer 3 : name", dac_worker3.name , "pid", dac_worker3.pid )
        dac_worker3.start()
    print("")
    #def Run():
    
    #
    # Main loop do nothing. Maybe do the webui server ?
    #
    
    try:
        #while True:
        
        # Websocket startup
        wserver = WebsocketServer(wsPORT,host=serverIP)
        plugins.Init(wserver)
        
        log.info("Starting servers...")
        # Launch OSC thread listening to oscserver
        print("Launching OSC server...")
        print("at", oscserverIPin, "port",str(oscserverPORTin))
        #print("Will update webUI dac status every second")
        oscserver.addMsgHandler( "/noteon", commands.NoteOn)
        oscserver.addMsgHandler( "/scim", commands.Scim)
        oscserver.addMsgHandler( "/line1", commands.Line1)
        oscserver.addMsgHandler( "/forwardui", commands.ForwardUI)
        # Default OSC handler for all OSC incoming message
        oscserver.addMsgHandler("default", handler)
        _thread.start_new_thread(osc_thread, ())
    
        #print wserver
        print("Launching webUI Websocket server...")
        print("at", serverIP, "port",wsPORT)
        wserver.set_fn_new_client(new_client)
        wserver.set_fn_client_left(client_left)
        wserver.set_fn_message_received(message_received)
        print("")
        log.info("Resetting all Homographies...")
        for laserid in range(0,gstt.LaserNumber):  
            homographyp.newEDH(laserid)
    
        # plugins autostart
        print("")
        log.info("Plugins startup...")
    
        if gstt.autostart != "":
         
            for pluginname in gstt.autostart.split(","):
                print("Autostarting", pluginname, "...")
                plugins.Start(pluginname)
        
        print("")
        log.infog("LJ server running...")
        
        wserver.run_forever()
        
    
    except Exception:
        log.err("Exception")
        traceback.print_exc()

    except Restart(moment):
        print("Autokill asked at", moment)
    
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
            print("Laser",laserid,"feedbacks resetting...")
            r.set('/lack/'+str(laserid),64)
            r.set('/lstt/'+str(laserid),64)
            r.set('/cap/'+str(laserid),0)
    
    print("Fin de LJ.")
    
    #if __name__ == "__main__":
    #    Run()
    
    '''
    Some code previously used, for reference :
    
    random_points = [(300.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 0), (500.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 65280), (500.0+random.randint(-100, 100), 400.0+random.randint(-100, 100), 65280), (300.0+random.randint(-100, 100), 400.0+random.randint(-100, 100), 65280), (300.0+random.randint(-100, 100), 200.0+random.randint(-100, 100), 65280)]
    '''



