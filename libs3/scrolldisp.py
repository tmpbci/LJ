#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
ScrollDisp
v0.7.0

An example of an unicornhat hack for Launchpad Mini or Bhoreal.

This is a custom version of scrolldisp.py that display text on unicornhat
with use of bhorunicornhat to use with a Bhoreal or a Launchpad mini mk2

Default device is the launchpad.


Command line to display 2 chars:

To display 'OK' :
python3 scrolldisp.py OK

To display a rainbow :
python3 scrolldisp.py ~R

See the end of this script for more option like scrolling or use a bhoreal in command line.


As a Library :

Display(text, color=(255,255,255), delay=0.2, mididest ='launchpad')

DisplayScroll(text, color=(255,255,255), delay=0.2, mididest = 'launchpad')

Remember there is Cls functions
launchpad.Cls()
bhoreal.Cls()

'''

#from unicorn_hat_sim import unicornhat as u

import bhorunicornhat as u
import time, math, sys

class ScrollDisp:
    columns = []
    mappings = {'!': [" ",
                      "#",
                      "#",
                      "#",
                      "#",
                      " ",
                      "#",
                      " "],
                '\'': [" ",
                      "#",
                      "#",
                      " ",
                      " ",
                      " ",
                      " ",
                      " "],
                '(': ["  ",
                      " #",
                      "# ",
                      "# ",
                      "# ",
                      "# ",
                      " #",
                      "  "],
                ')': ["  ",
                      "# ",
                      " #",
                      " #",
                      " #",
                      " #",
                      "# ",
                      "  "],
                ',': ["  ",
                      "  ",
                      "  ",
                      "  ",
                      "  ",
                      "  ",
                      " #",
                      "# "],
                '-': ["   ",
                      "   ",
                      "   ",
                      "   ",
                      "###",
                      "   ",
                      "   ",
                      "   "],
                '.': [" ",
                      " ",
                      " ",
                      " ",
                      " ",
                      " ",
                      "#",
                      " "],
                '0': ["    ",
                      " ## ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      " ## ",
                      "    "],
                '1': ["   ",
                      " # ",
                      "## ",
                      " # ",
                      " # ",
                      " # ",
                      "###",
                      "   "],
                '2': ["    ",
                      " ## ",
                      "#  #",
                      "   #",
                      "  # ",
                      " #  ",
                      "####",
                      "    "],
                '3': ["    ",
                      "####",
                      "   #",
                      "  # ",
                      "   #",
                      "#  #",
                      " ## ",
                      "    "],
                '4': ["    ",
                      "#  #",
                      "#  #",
                      "####",
                      "   #",
                      "   #",
                      "   #",
                      "    "],
                '5': ["    ",
                      "####",
                      "#   ",
                      "### ",
                      "   #",
                      "#  #",
                      " ## ",
                      "    "],
                '6': ["    ",
                      " ## ",
                      "#   ",
                      "### ",
                      "#  #",
                      "#  #",
                      " ## ",
                      "    "],
                '7': ["    ",
                      "####",
                      "   #",
                      "  # ",
                      "  # ",
                      " #  ",
                      " #  ",
                      "    "],
                '8': ["    ",
                      " ## ",
                      "#  #",
                      " ## ",
                      "#  #",
                      "#  #",
                      " ## ",
                      "    "],
                '9': ["    ",
                      " ## ",
                      "#  #",
                      " ###",
                      "   #",
                      "   #",
                      " ## ",
                      "    "],
                ':': [" ",
                      " ",
                      " ",
                      "#",
                      " ",
                      " ",
                      "#",
                      " "],
                'A': ["    ",
                      " ## ",
                      "#  #",
                      "#  #",
                      "####",
                      "#  #",
                      "#  #",
                      "    "],
                'B': ["    ",
                      "### ",
                      "#  #",
                      "### ",
                      "#  #",
                      "#  #",
                      "### ",
                      "    "],
                'C': ["    ",
                      " ## ",
                      "#  #",
                      "#   ",
                      "#   ",
                      "#  #",
                      " ## ",
                      "    "],
                'D': ["    ",
                      "### ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      "### ",
                      "    "],
                'E': ["    ",
                      "####",
                      "#   ",
                      "### ",
                      "#   ",
                      "#   ",
                      "####",
                      "    "],
                'F': ["    ",
                      "####",
                      "#   ",
                      "### ",
                      "#   ",
                      "#   ",
                      "#   ",
                      "    "],
                'G': ["    ",
                      " ## ",
                      "#  #",
                      "#   ",
                      "# ##",
                      "#  #",
                      " ## ",
                      "    "],
                'H': ["    ",
                      "#  #",
                      "#  #",
                      "####",
                      "#  #",
                      "#  #",
                      "#  #",
                      "    "],
                'I': ["   ",
                      "###",
                      " # ",
                      " # ",
                      " # ",
                      " # ",
                      "###",
                      "   "],
                'J': ["    ",
                      " ###",
                      "   #",
                      "   #",
                      "   #",
                      "#  #",
                      " ## ",
                      "    "],
                'K': ["    ",
                      "#  #",
                      "# # ",
                      "##  ",
                      "##  ",
                      "# # ",
                      "#  #",
                      "    "],
                'L': ["   ",
                      "#  ",
                      "#  ",
                      "#  ",
                      "#  ",
                      "#  ",
                      "###",
                      "   "],
                'M': ["    ",
                      "#  #",
                      "####",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      "    "],
                'N': ["    ",
                      "#  #",
                      "## #",
                      "# ##",
                      "#  #",
                      "#  #",
                      "#  #",
                      "     "],
                'O': ["    ",
                      " ## ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      " ## ",
                      "    "],
                'P': ["    ",
                      "### ",
                      "#  #",
                      "### ",
                      "#   ",
                      "#   ",
                      "#   ",
                      "    "],
                'Q': ["    ",
                      " ## ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "# # ",
                      " # #",
                      "    "],
                'R': ["    ",
                      "### ",
                      "#  #",
                      "### ",
                      "##  ",
                      "# # ",
                      "#  #",
                      "    "],
                'S': ["    ",
                      " ###",
                      "#   ",
                      " #  ",
                      "  # ",
                      "   #",
                      "### ",
                      "    "],
                'T': ["     ",
                      "#####",
                      "  #  ",
                      "  #  ",
                      "  #  ",
                      "  #  ",
                      "  #  ",
                      "     "],
                'U': ["    ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      " ## ",
                      "    "],
                'V': ["   ",
                      "# # ",
                      "# # ",
                      "# # ",
                      "# # ",
                      "# # ",
                      " #  ",
                      "    "],
                'W': ["     ",
                      "#   #",
                      "#   #",
                      "#   #",
                      "# # #",
                      "## ##",
                      "#   #",
                      "     "],
                'X': ["   ",
                      "# #",
                      "# #",
                      " # ",
                      " # ",
                      "# #",
                      "# #",
                      "   "],
                'Y': ["   ",
                      "# #",
                      "# #",
                      "# #",
                      " # ",
                      " # ",
                      " #  ",
                      "    "],
                'Z': ["    ",
                      "####",
                      "   #",
                      "  # ",
                      " #  ",
                      "#   ",
                      "####",
                      "    "],
                '[': ["  ",
                      "##",
                      "# ",
                      "# ",
                      "# ",
                      "# ",
                      "##",
                      "  "],
                ']': ["  ",
                      "##",
                      " #",
                      " #",
                      " #",
                      " #",
                      "##",
                      "  "],
                '_': ["    ",
                      "    ",
                      "    ",
                      "    ",
                      "    ",
                      "    ",
                      "    ",
                      "####"],
                'a': ["    ",
                      "    ",
                      " ## ",
                      "   #",
                      " ###",
                      "#  #",
                      " ###",
                      "    "],
                'b': ["    ",
                      "#   ",
                      "#   ",
                      "### ",
                      "#  #",
                      "#  #",
                      "### ",
                      "    "],
                'c': ["    ",
                      "    ",
                      " ## ",
                      "#  #",
                      "#   ",
                      "#  #",
                      " ## ",
                      "    "],
                'd': ["    ",
                      "   #",
                      "   #",
                      " ###",
                      "#  #",
                      "#  #",
                      " ###",
                      "    "],
                'e': ["    ",
                      "    ",
                      " ## ",
                      "#  #",
                      "####",
                      "#   ",
                      " ## ",
                      "    "],
                'f': ["    ",
                      " ## ",
                      "#  #",
                      "#   ",
                      "##  ",
                      "#   ",
                      "#   ",
                      "    "],
                'g': ["    ",
                      "    ",
                      " ## ",
                      "#  #",
                      " ###",
                      "   #",
                      "### ",
                      "    "],
                'h': ["    ",
                      "#   ",
                      "#   ",
                      "# # ",
                      "## #",
                      "#  #",
                      "#  #",
                      "    "],
                'i': ["   ",
                      " # ",
                      "   ",
                      "## ",
                      " # ",
                      " # ",
                      "###",
                      "   "],
                'j': ["   ",
                      "  #",
                      "   ",
                      "  #",
                      "  #",
                      "  #",
                      "# #",
                      " # "],
                'k': ["    ",
                      "#   ",
                      "#  #",
                      "# # ",
                      "##  ",
                      "# # ",
                      "#  #",
                      "    "],
                'l': ["   ",
                      "## ",
                      " # ",
                      " # ",
                      " # ",
                      " # ",
                      "###",
                      "   "],
                'm': ["     ",
                      "     ",
                      "## # ",
                      "# # #",
                      "#   #",
                      "#   #",
                      "#   #",
                      "     "],
                'n': ["    ",
                      "    ",
                      "### ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      "    "],
                'o': ["    ",
                      "    ",
                      " ## ",
                      "#  #",
                      "#  #",
                      "#  #",
                      " ## ",
                      "    "],
                'p': ["    ",
                      "    ",
                      "### ",
                      "#  #",
                      "#  #",
                      "### ",
                      "#   ",
                      "#   "],
                'q': ["    ",
                      "    ",
                      " ###",
                      "#  #",
                      "#  #",
                      " ###",
                      "   #",
                      "   #"],
                'r': ["    ",
                      "    ",
                      "# ##",
                      "##  ",
                      "#   ",
                      "#   ",
                      "#   ",
                      "    "],
                's': ["    ",
                      "    ",
                      " ###",
                      "#   ",
                      " ## ",
                      "   #",
                      "### ",
                      "    "],
                't': ["    ",
                      " #  ",
                      "####",
                      " #  ",
                      " #  ",
                      " #  ",
                      "  ##",
                      "    "],
                'u': ["    ",
                      "    ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      " ## ",
                      "    "],
                'v': ["     ",
                      "     ",
                      "#   #",
                      "#   #",
                      " # # ",
                      " # # ",
                      "  #  ",
                      "     "],
                'w': ["     ",
                      "     ",
                      "#   #",
                      "#   #",
                      "# # #",
                      "# # #",
                      " # # ",
                      "     "],
                'x': ["    ",
                      "    ",
                      "#  #",
                      "#  #",
                      " ## ",
                      "#  #",
                      "#  #",
                      "    "],
                'y': ["    ",
                      "    ",
                      "#  #",
                      "#  #",
                      " ###",
                      "   #",
                      "#  #",
                      " ## "],
                'z': ["    ",
                      "    ",
                      "####",
                      "  # ",
                      " #  ",
                      "#   ",
                      "####",
                      "    "]
               }
    sharpnotes = {
                'A': ["   #",
                      " ## ",
                      "#  #",
                      "#  #",
                      "####",
                      "#  #",
                      "#  #",
                      "    "],
                'C': ["   #",
                      " ## ",
                      "#  #",
                      "#   ",
                      "#   ",
                      "#  #",
                      " ## ",
                      "    "],
                'D': ["   #",
                      "### ",
                      "#  #",
                      "#  #",
                      "#  #",
                      "#  #",
                      "### ",
                      "    "],
                'F': ["   #",
                      "### ",
                      "#   ",
                      "### ",
                      "#   ",
                      "#   ",
                      "#   ",
                      "    "],
                'G': ["   #",
                      " ## ",
                      "#  #",
                      "#   ",
                      "# ##",
                      "#  #",
                      " ## ",
                      "    "]
              }
    def append_mapping(self, char, color):
        #self.append_space()
        bitmap = self.mappings[char]
        n = len(bitmap[0]) 
        for x in range(n):
            self.columns.append([(color if bitmap[i][x] == '#' else (0,0,0)) for i in range(8)])
                
    def append_rainbow(self):
        for x in range(8):
            r = int((math.cos(x * math.pi / 4) + 1) * 127)
            g = int((math.cos((x - 8.0 / 3.0) * math.pi / 4) + 1) * 127)
            b = int((math.cos((x + 8.0 / 3.0) * math.pi / 4) + 1) * 127)
            self.columns.append([(r,g,b) for i in range(8)])

    def append_space(self, n=1):
        for x in range(n):
            self.columns.append([(0,0,0) for i in range(8)])

    def append_buffer(self):
        self.append_space(9)

    def append_letter(self, char, color=None):
        if char == ' ':
            self.append_space(2)
        elif char == 0:
            self.append_rainbow()
        elif char in self.mappings.keys():
            self.append_mapping(char, color)
        else:
            self.columns.append([(255,255,255),(255,255,255),(255,255,255),(255,255,255),(255,255,255),(255,255,255),(255,255,255),(255,255,255)])
            print("unknown char {0} ({1})".format(char, ord(char)))


    def append_sharpnote(self, text, color=(255,255,255)):

        # Note 
        # Should be a better test for A-G letter.    
        if text[0] in self.mappings.keys():
            bitmap = self.sharpnotes[text[0]]
            
            n = len(bitmap[0]) 
            for x in range(n):
              self.columns.append([(color if bitmap[i][x] == '#' else (0,0,0)) for i in range(8)])
                

        # Octave
        if text[2] in self.mappings.keys():    
            self.append_letter(text[2], color)


    def append_string(self, text, color=(255,255,255)):
        i = 0
        while i < len(text):
            if text[i] == '~':
                i += 1
                if text[i] == 'R': #rainbow
                    self.append_letter(0)
            else:
                self.append_letter(text[i], color)
            i += 1

    def set_text(self, text, color=(255,255,255)):
        self.columns = []
        #self.append_buffer()

        if len(text) == 3 and text[1] == "#":
          self.append_sharpnote(text)
        else:
          self.append_string(text)

        self.append_buffer()

    def __init__(self, text=""):
        self.set_text(text)
        
    def start(self, delay=0.1):
        
        u.set_pixels(self.columns[0:8])
        u.show()
        time.sleep(delay)

    def startScroll(self, delay=0.1):

        for x in range(len(self.columns) - 8):
            u.set_pixels(self.columns[x:x+8])
            u.show()
            time.sleep(delay)


def Display(text, color=(255,255,255), delay=0.2, mididest ='launchpad'):
    disp = ScrollDisp()
    #print(text)

    if mididest == 'bhoreal':
      u.dest(mididest,180)
    else:
      u.dest(mididest,270)

    disp.set_text(text, color)
    disp.start(delay)

def DisplayScroll(text, color=(255,255,255), delay=0.2, mididest = 'launchpad'):
    disp = ScrollDisp()
    if mididest == 'bhoreal':
      u.dest(mididest,180)
    else:
      u.dest(mididest,270)
    disp.set_text(text, color)
    disp.startScroll(delay)


if __name__ == '__main__':

    from libs import midi3

    # Implemented for script compatibility but actually do nothing on supported devices 
    u.brightness(0.5)

    # 2 chars with no scrolling
    Display(' '.join(sys.argv[1:]))


    # text with scrolling
    # DisplayScroll(' '.join(sys.argv[1:]))



    # To use with a Bhoreal just add mididest = 'bhoreal' in Display() 
    # or DisplayScroll()

    # Display(' '.join(sys.argv[1:]), mididest = 'bhoreal')
