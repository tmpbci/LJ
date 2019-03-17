#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''

LJ Laser Server v0.8.1

Plugins Handler.

'''

from OSC import OSCServer, OSCClient, OSCMessage
from websocket_server import WebsocketServer
import gstt
import os
import subprocess
import sys


def Init(wserver):
    global WSserver

    WSserver = wserver


def sendWSall(message):
    #if gstt.debug >0:
        #print("WS sending %s" % (message))
    WSserver.send_message_to_all(message)

# What is plugin's OSC port ? 
def Port(name):
    
    data = gstt.plugins.get(name)
    return data.get("OSC")

# How to start the plugin ?
def Command(name):
    
    data = gstt.plugins.get(name)
    return data.get("command")

# Get all plugin current state 
def Data(name):
    
    return gstt.plugins.get(name)
   

def Start(name):

    # get Plugin configuration.
    command = Command(name)

    # Maybe it's not fully started
    data = Data(name)

    if command != "" and "pid" not in data : 

        sendWSall("/status Starting...")
        # Get LJ path
        ljpath = r'%s' % os.getcwd().replace('\\','/')

        print ""
        print "LJ is starting plugin :", name
        
        # Construct the command with absolute path.
        
        PluginPath = command.split(" ")
        # Launch as a subprocess
        PluginProcess = subprocess.Popen([PluginPath[0], ljpath + "/" + PluginPath[1]])
        
        if gstt.debug >0:
            print "LJ path :", ljpath
            print "New process pid for ", name, ":", PluginProcess.pid

        data = Data(name)

        data["pid"] = PluginProcess.pid
        data["process"] = PluginProcess

        # Process can be terminated with :
        # PluginProcess.terminate()

def OSCsend(name, oscaddress, oscargs =''):

    PluginPort = Port(name)
    sendWSall("/status Checking "+ name + "...")
    if gstt.debug >1:
            print ""
            print "OSCSend is checking plugin", name, "..."
            print "Plugin", name, "is at", gstt.LjayServerIP, ":" + str(PluginPort)
            print "Sending", oscaddress, oscargs,"to plugin", name
    
    osclientplugin = OSCClient()
    osclientplugin.connect((gstt.LjayServerIP, PluginPort)) 
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)

    try:
        osclientplugin.sendto(oscmsg, (gstt.LjayServerIP, PluginPort))
        oscmsg.clearData()
        #if gstt.debug >0:
        #    print oscaddress, oscargs, "was sent to",name     
        return True

    except:
        if gstt.debug > 0:
            print 'OSCSend : Connection to plugin IP', gstt.LjayServerIP ,':', PluginPort,'refused : died ?'
        #sendWSall("/status No plugin.")
        sendWSall("/status " + name + " is offline")
        sendWSall("/" + name + "/start 0")
        #PluginStart(name)
        return False


def Ping(name):
    
    return OSCsend(name,"/ping")

        
def Kill(name):

    data = Data(name)
    print ""
    if data["process"]  != None:
        print name, "plugin is owned by LJ."
        print "Killing plugin", name
        
        OSCsend(name,"/quit")
        #data["process"].terminate()

        sendWSall("/status Killing "+ name +".")
    else:
        print "Killing asked but plugin is not owned by LJ"
        sendWSall("/status Not own plugin")


# Send a command to given plugin. Will also start it if command contain /start 1 
def Send(name,oscpath):

   
    if oscpath[0].find(name) != -1:

        # Plugin is online ?
        if Ping(name):

            # Light up the plugin button
            sendWSall("/" + name + "/start 1")
            sendWSall("/status " + name + " online")    
            if gstt.debug >0:
                print "Plugin " + name + " online."
                print "Command", oscpath

            
            # If start 0, try to kill plugin 
            if oscpath[0].find("start") != -1 and oscpath[1] == "0":

                if gstt.debug >0:
                    print "start 0, so killing", name, "..."
                Kill(name)
            
            # Send osc command
            elif len(oscpath) == 1:
                OSCsend(name,oscpath[0], oscargs='noargs')
            else:
                OSCsend(name,oscpath[0], oscargs=oscpath[1])
            return True
        
        # Plugin not online..
        else:
            
            if gstt.debug >0:
                print "Send says plugin " + name + " is offline."
                #print "Command", oscpath

            sendWSall("/status Plugin " + name + " offline")
            sendWSall("/"+ name + "/start 0")
            
            # Try to Start it if /start 1
            if oscpath[0].find("start") != -1 and oscpath[1] == "1":
                if gstt.debug >0:
                    print "Trying to start", name, "..."
                Start(name)

            return False
