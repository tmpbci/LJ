#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-

"""

Web UI index html page builder
v0.2 for LJ v0.8 +


LICENCE : CC
by Sam Neurohack 
from /team/laser


"""

blocknames = [
'blocks/head.html', 
'blocks/title.html', 
'blocks/menu.html', 
'blocks/align.html', 
'blocks/live.html', 
'blocks/simuheader.html', 
'blocks/planetarium.html', 
'blocks/lissa.html', 
'blocks/ai.html',
'blocks/plugins.html',
'blocks/bank0.html',
'blocks/pose.html',
'blocks/words.html',
'blocks/nozoids.html', 
'blocks/run.html',
'blocks/footer.html' 
]
with open('index.html', 'w') as outfile:
    for block in blocknames:
        with open(block) as infile:
            outfile.write(infile.read())