#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

'''

Ableton Link

LICENCE : CC
Sam Neurohack


Get:

git clone --recursive https://github.com/gonzaloflirt/link-python.git

Build:

Make sure python 3 is installed on your system.

mkdir build
cd build
cmake ..
cmake --build .

'''
import midix
import sys

prevphase = 0
bpm = 120

def Start():
    global lnk
    import link

    print("Link ENABLED")
    lnk = link.Link(120)
    lnk.enabled = True
    lnk.startStopSyncEnabled = True
    linked = True


def BeatEvent():
    global lnk, prevphase


    lnkstr = lnk.captureSessionState()
    link_time = lnk.clock().micros();
    tempo_str = '{0:.2f}'.format(lnkstr.tempo())
    bpm = float(tempo_str)
    #beatstep.SendOSCUI('/bpm', [bpm])
    beats_str = '{0:.2f}'.format(lnkstr.beatAtTime(link_time, 0))
    playing_str = str(lnkstr.isPlaying()) # always False ???
    phase = lnkstr.phaseAtTime(link_time, 4)


    # new beat ?
    if int(phase) != prevphase:
        prevphase = int(phase)
        #print("LINK BPM:",bpm)
        sys.stdout.write("Beat "+str(beats_str) + '  \r')
        sys.stdout.flush()
        midix.SendUI('/beats', [beats_str])

        #alink.SendOSCUI('/states/cc/'+str(ccnumber), [value])
        currentbeat = float(beats_str)
        #midix.SendAU('/aurora/beats', beats_str)
        #AllStatus("Beat "+str(beats_str))



# Change current Link Tempo.
def newtempo(tempo):
    global lnk

    #print("val2", val2, "tempo", tempo)

    if linked == True:
        lnk.enabled = False
        lnk.startStopSyncEnabled = False
        lnk = link.Link(tempo)
        lnk.enabled = True
        lnk.startStopSyncEnabled = True
        bpm = tempo
        print(("New BPM", bpm))
        midix.SendUI('/bpm', [bpm])

    else:
        print("Link is disabled")


# 
def BPMAdj(val1, keyname):

    print((gstt.currentbpm))

    # + 1
    if val1 == 1:
        newtempo(gstt.currentbpm+1)

    # -1
    if val1 == 127 and gstt.currentbpm > 0:
        newtempo(gstt.currentbpm-1)



