#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

typetext('hello')
tap(key)

Loosely found and reuse in LPHK from nimaid
https://github.com/nimaid/LPHK

mouse functions commented yet

"""
import keyboard
# import ms

media_keys = {"vol_up" : 57392, "vol_down" : 57390, "mute" : 57376, "play_pause" : 57378, "prev_track" : 57360, "next_track" : 57369}
#with mouse
#media_keys = {"vol_up" : 57392, "vol_down" : 57390, "mute" : 57376, "play_pause" : 57378, "prev_track" : 57360, "next_track" : 57369, "mouse_left" : "mouse_left","mouse_middle" : "mouse_middle", "mouse_right" : "mouse_right"}
pressed = set()

def sp(name):
    try:
        return keyboard.key_to_scan_codes(str(name))[0]
    except:
        try:
            return media_keys[str(name)]
        except:
            return None

def press(key):
    pressed.add(key)
    if type(key) == str:
        '''
        if "mouse_" in key:
            ms.press(key[6:])
            return
        '''
    keyboard.press(key)

def release(key):
    pressed.discard(key)
    if type(key) == str:
        '''
        if "mouse_" in key:
            ms.release(key[6:])
            return
        '''
    keyboard.release(key)

def release_all():
    for key in pressed.copy():
        release(key)

def tap(key):
    if type(key) == str:
        '''
        if "mouse_" in key:
            ms.click(key[6:])
            return
        '''
    press(key)
    release(key)

def typetext(name):

    #print(name)
    for letter in name:
        #print (letter)
        tap(letter)

