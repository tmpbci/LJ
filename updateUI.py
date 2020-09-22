#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
'''
LJ UI IP updater v0.8.1

'''
#wwwIP = "192.168.2.78"
#wwwIP = "aurora.teamlaser.fr"
wwwIP = "192.168.1.48"

import os, sys
ljpath = r'%s' % os.getcwd().replace('\\','/')

python2 = (2, 6) <= sys.version_info < (3, 0)

def Updatepage(file_name):

    print("updating", file_name)
    f=open(file_name,"r+")
    a=f.readlines()
    #print a

    for line in a:

        if python2 == True:

          # python2
          if "var LJ = " in line > -1:
            p=a.index(line)
            #so now we have the position of the line which to be modified
            a[p]="      var LJ = 'ws://"+wwwIP+":9001/'\n"
            #print(p, line, a[p])

        else:

          # python3
          IPline = ("var LJ = " in line)
          if IPline == True:

            p=a.index(line)
            #so now we have the position of the line which to be modified
            a[p]="      var LJ = 'ws://"+wwwIP+":9001/'\n"
            #print(p, line, a[p])

    f.seek(0)
    f.truncate() #ersing all data from the file
    f.close()
    #so now we have an empty file and we will write the modified content now in the file
    o=open(file_name,"w")
    for i in a:
       o.write(i)
    o.close()
    #now the modification is done in the file

def www(wwwip):
    global wwwIP 

    wwwIP = wwwip
    print("Updating www files to use", wwwIP)
    Updatepage(ljpath+"/www/LJ.js")
    Updatepage(ljpath+"/www/trckr/trckrcam1.html")
    Updatepage(ljpath+"/www/simu.html")
    Updatepage(ljpath+"/www/align.html")
    Updatepage(ljpath+"/www/auralls.html")
    Updatepage(ljpath+"/www/index.html")
