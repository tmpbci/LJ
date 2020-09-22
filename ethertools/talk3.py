#!/usr/bin/env python
#
# j4cDAC test code
#
# Copyright 2011 Jacob Potter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import dac3 as dac

class SquarePointStream(object):
    '''
    def produce(self):
        pmax = 15600
        pstep = 100
        cmax = 65535
        while True:
            for x in xrange(-pmax, pmax, pstep):
                yield (x, pmax, cmax, 0, 0, cmax)
            for y in xrange(pmax, -pmax, -pstep):
                yield (pmax, y, 0, cmax, 0, cmax)
            for x in xrange(pmax, -pmax, -pstep):
                yield (x, -pmax, 0, 0, cmax, cmax)
            for y in xrange(-pmax, pmax, pstep):
                yield (-pmax, y, cmax, cmax, cmax, cmax)
    '''

    def produce(self):

        pmax = 15600
        pstep = 100
        Cmax = 65535

        
        while True:

            print("Cmax:",Cmax)
                        
            for x in range(-pmax, pmax, pstep):

                yield (x, pmax,  Cmax, 0, 0)            # pure Red
                #yield (x, pmax, 0, Cmax, 0)            # pure Green
                #yield (x, pmax, 0, 0, Cmax)            # pure Blue
                #yield (x, pmax, Cmax, Cmax, Cmax)       # pure White

            
            for y in range(pmax, -pmax, -pstep):

                #yield (pmax, y,  Cmax, 0, 0)            # pure Red
                yield (pmax, y, 0, Cmax, 0)              # pure Green
                #yield (pmax, y,  0, 0, Cmax)           # pure Blue
                #yield (pmax, y, Cmax, Cmax, Cmax)       # pure White
            
            for x in range(pmax, -pmax, -pstep):
                #yield (x, -pmax,  Cmax, 0, 0)          # pure Red
                #yield (x, -pmax, 0, Cmax, 0)           # pure Green
                yield (x, -pmax, 0, 0, Cmax)           # pure Blue
                #yield (x, -pmax, Cmax, Cmax, Cmax)     # pure White
                
            
            for y in range(-pmax, pmax, pstep):
                #yield (-pmax, y,   Cmax, 0, 0)         # pure Red
                #yield (-pmax, y,0, Cmax, 0)            # pure Green
                #yield (-pmax, y, 0, 0, Cmax)           # pure Blue
                yield (-pmax, y, Cmax, Cmax, Cmax)      # pure White




    def __init__(self):
        self.stream = self.produce()

    def read(self, n):
        return [next(self.stream) for i in range(n)]

class NullPointStream(object):
    def read(self, n):
        return [(0, 0, 0, 0, 0)] * n

#dac.find_dac()

d = dac.DAC(dac.find_first_dac())
#d = dac.DAC("192.168.1.43")

d.play_stream(SquarePointStream())
