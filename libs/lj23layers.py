# coding=UTF-8
'''

lj23layers v0.7.6 for LJ v0.8+

Some LJ functions useful for python clients 

"layers" version : "PL" has been replaced by layer


Class management :

https://stackoverflow.com/questions/739882/iterating-over-object-instances-of-a-given-class-in-python
https://stackoverflow.com/questions/8628123/counting-instances-of-a-class
http://effbot.org/pyfaq/how-do-i-get-a-list-of-all-instances-of-a-given-class.htm

Config(redisIP, client number,name) 

Basic Draw :

- PolyLineOneColor, rPolyLineOneColor, LineTo, Line
- PolyLineRGB, rPolyLineRGB, LineRGBTo, LineRGB
- rgb2int(r,g,b)
- Drawlayer (point list number) : once you stacked all wanted elements, like 2 polylines, send them to lasers.
- DrawDests():                Draw all requested destinations for each layer .

High level draw :

- Text(word, integercolor, layer , xpos, ypos, resize, rotx, roty, rotz) : Display a word
- TextRGB(word, red, green, blue, ...)
- Embeded font1


Laser objects (name and convenient group of parameters for one or several point lists)

- RelativeObject
- FixedObject

layer "Destinations" : tells Live what layer to draw and to what scene/Laser ("destination") to send it.


OSC and plugins functions :

SendLJ(adress,message) :    LJ remote control. See commands.py
SendResol(address,message): Send OSC message to Resolume.
WebStatus(message) :        display message on webui

Ljscene(client):            Change scene number in redis keys
Ljlayer(layer):             Change layer number in redis keys = laser target.
ClosePlugin(name):          Send UI closing info of given plugin

OSCstart():     Start the OSC system.
OSCframe():     Handle incoming OSC message. Calling the right callback
OSCstop():      Properly close the OSC system
OSCping():      /ping Answer to LJ pings by sending /pong name
OSCquit():      /quit Exit calling script using name in terminal
OSCadddest():   layer , scene, laser   Add a destination 
OSCdeldest():   layer , scene, lasers  delete a destination
OSCobj():       /name/obj objectname attribute value    for automation
OSCvar():       /name/var variablename value            for automation

setup_controls(joystick) 

XboxController :     getLeftHori, getLeftVert, getRightHori, getRightVert, getLeftTrigger, getRightTrigger
Ps3Controller :      getLeftHori, getLeftVert, getRightHori, getRightVert, getLeftTrigger, getRightTrigger, getUp, getDown, getLeft, getRight, getFire1, getFire2(self):
MySaitekController : getLeftHori,getLeftVert, getRightHori,getRightVert, getLeftTrigger,getRightTrigger
MyThrustController : getLeftHori, getLeftVert, getRightHori, getRightVert, getLeftTrigger, getRightTrigger
CSLController :      getLeftHori,getLeftVert,getRightHori, getRightVert,getLeftTrigger,getRightTrigger,getFire1,getFire2
my USB Joystick :    getUp,getDown,getLeft,getRight,etLeftTrigger, getRightTrigger,getFire1, getFire2


LICENCE : CC
Sam Neurohack

'''

import math
import redis
import sys
import weakref
import struct
import numpy as np
from multiprocessing import Process, Queue, TimeoutError 

is_py2 = sys.version[0] == '2'
if is_py2:
    from OSC import OSCServer, OSCClient, OSCMessage
    #print ("Importing lj23 and OSC from libs...")
else:
    from OSC3 import OSCServer, OSCClient, OSCMessage
    #print ("Importing lj23 and OSC3 from libs...")


#redisIP = '127.0.0.1'
#r = redis.StrictRedis(host=redisIP, port=6379, db=0)

ClientNumber = 0
name = "noname"
oscrun = True
point_list = []
layers = [[],[],[],[]]

fft3Groups = [-1,-1,-1,-1]

Dests = dict()

oscIPresol = "127.0.0.1"
oscPORTresol = 7000


'''

 Laser "objects"


 set a name and convenient group of parameters for one or several point lists
 
 RelativeObject is for point lists around 0,0 with builtin move/rotation.

 How to init with object color, xpos,... :
 osciObj = lj.RelativeObject('osciObj', True, 255, [], white, red, green,blue,0 , False, centerX , centerY , 1 , Xrot , Yrot , Zrot)
 How to use in drawing functions : you're free to use 0, some or all of any laserobject attributes 
 - draw one or several pointlists with 'A' laserobject color and 'B' laserobject xpos ypos ?
 - Change color of 'main' object and all other objects using it will change also
 how to change attribute :
 osciObj.resize = 2 or /pluginame/change 'OsciObj' 'resize' 2

'''

class RelativeObject:

    kind = 'relative'
    counter = 0

    def __init__(self, name, active, intensity, xy, color, red, green, blue, layer , closed, xpos , ypos , resize , rotx , roty , rotz):
        self.name = name
        self.active = active    # True/False
        self.intensity = intensity
        self.xy = []             # Dots list
        self.color = color      # RGB color in int
        self.red = red
        self.green = green
        self.blue = blue
        self.layer = layer 
        self.closed = closed
        self.xpos = xpos
        self.ypos = ypos
        self.resize = resize
        self.rotx = rotx
        self.roty = roty
        self.rotz = rotz

        RelativeObject.counter += 1
        #type(self).counter += 1

    def __del__(self):
        RelativeObject.counter -= 1


# Fixed Laser object : point list in 'pygame' space (top left = 0,0 / bottom right)
class FixedObject:

    kind = 'fixed'
    counter = 0

    def __init__(self, name, intensity, active, xy, color, red, green, blue, layer , closed):
        self.name = name
        self.active = active    # True/False
        self.intensity = intensity
        self.xy = []
        self.color = color
        self.red = red
        self.green = green
        self.blue = blue
        self.layer = layer 
        self.closed = closed

        FixedObject.counter += 1

    def __del__(self):
        FixedObject.counter -= 1

'''

class IterDest(type):
    def __new__ (cls, name, bases, dct):
        dct['_instances'] = []
        return super().__new__(cls, name, bases, dct)
 
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        cls._instances.append(instance)
        return instance
 
    def __iter__(cls):
        return iter(cls._instances)

class DestObject():

# class Destinations(metaclass=IterDest):
    __metaclass__ = IterDest
    counter = 0
    def __init__(self, name, number, active, layer , scene, laser):
        self.name = name
        self.number = number
        self.active = active
        self.layer = layer 
        self.scene = scene
        self.laser = laser

        DestObject.counter += 1

    def __del__(self):
        DestObject.counter -= 1
'''
class DestObject():

# class Destinations(metaclass=IterDest):
    _instances = set()
    counter = 0

    def __init__(self, name, number, active, layer , scene, laser):
        self.name = name
        self.number = number
        self.active = active
        self.layer = layer 
        self.scene = scene
        self.laser = laser
        self._instances.add(weakref.ref(self))
        DestObject.counter += 1

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead


    def __del__(self):
        DestObject.counter -= 1



def Config(redIP,client,myname):
    global ClientNumber, name, redisIP, r

    redisIP = redIP
    r = redis.StrictRedis(host=redisIP, port=6379, db=0)    
    
    # ClientNumber 255 are not drawing anything like artnet
    ClientNumber = client
    #print ("client configured",ClientNumber)
    name = myname
    print ("Plugin declare its name",name)
    #print layer 
    return r


def LjClient(client):
    global ClientNumber

    ClientNumber = client



def Ljlayer(somelayer):
    global layer 

    layer = somelayer 


def fromRedis(n):

   encoded = r.get(n)
   #print("")
   #print('fromredis key',n,":",encoded)
   h, w = struct.unpack('>II',encoded[:8])
   #print("fromredis array size",n,":",h,w)
   a = np.frombuffer(encoded, dtype=np.int16, offset=8).reshape(h,w)
   #print("fromredis array",n,":",a)
   return a

# Store Numpy array 'a' in Redis key 'n'
# Write also in redis key 'a' numpy array, its 2 dimensions size : h time w values
def toRedis(n,a):

   #print("array.shape", a.shape, len(a.shape) )
   if len(a.shape) == 1:
        h = a.shape[0]
        w = 1
   else:
        h,w = a.shape
   #print("toredis", n,"h",h,"w",w,"a",a)
   shape = struct.pack('>II',h,w)

   #shape = struct.pack('>II',len(a),1)
   #print("toredis",n,a)
   encoded = shape + a.tobytes()

   # Store encoded data in Redis
   return r.set(n,encoded)


#
# OSC functions
# 

# OSC clients

def SendLJ(oscaddress,oscargs=''):
        
    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclientlj = OSCClient()
    osclientlj.connect((redisIP, 8002)) 

    print("lj23 in",name," sending OSC message : ", oscmsg, "to", redisIP, ":8002")
    try:
        osclientlj.sendto(oscmsg, (redisIP, 8002))
        oscmsg.clearData()
    except:
        print ('Connection to LJ refused : died ?')
        pass
    #time.sleep(0.001



#  Resolume OSC Arena client.
# sendresol(oscaddress, [arg1, arg2,...])
# example : sendresol("/noteon",note)

def SendResol(oscaddress,oscargs):

    oscmsg = OSCMessage()
    oscmsg.setAddress(oscaddress)
    oscmsg.append(oscargs)
    
    osclientresol = OSCClient()
    osclientresol.connect((oscIPresol, oscPORTresol)) 

    print("lj sending OSC message : ", oscmsg, "to Resolume", oscIPresol, ":", oscPORTresol)
    try:
        osclientresol.sendto(oscmsg, (oscIPresol, oscPORTresol))
        oscmsg.clearData()
    except:
        print ('Connection to Resolume refused : died ?')
        pass




def WebStatus(message):
    SendLJ("/status", message)


# Closing plugin messages to LJ
def ClosePlugin():
        WebStatus(name+" Exiting")
        SendLJ("/"+name+"/start",0)




# RAW OSC Frame available ? 
def OSCframe():
    # clear timed_out flag
    #print "oscframe"
    oscserver.timed_out = False
    # handle all pending requests then return
    while not oscserver.timed_out:
        oscserver.handle_request()

# Answer to LJ pings with /pong value
def OSCping(path, tags, args, source):
#def OSCping():
    print(name, "got /ping from LJ -> reply /pong", name)
    SendLJ("/pong",name)

# Properly close the system. Todo
def OSCstop():
    oscserver.close()


# /quit
def OSCquit(path, tags, args, source):
    global oscrun

    oscrun = False
    print('lj23 got /quit for',name)
    #WebStatus(name + " quit.")
    #SendLJ("/"+name+"/start",0)
    #print("Stopping OSC...")
    #OSCstop()
    #sys.exit()


# default handler
def OSChandler(path, tags, args, source):

    oscaddress = ''.join(path.split("/"))
    print("Default OSC Handler in",name,": msg from Client : " + str(source[0]),)
    print("OSC address", path)
    if len(args) > 0:
        print("with args", args)

    #oscIPout = str(source[0])
    #osclient.connect((oscIPout, oscPORTout))


# for any laser object : /pluginame/obj objectname attribute value 
# like : /pluginname/obj 'fft' 'xpos' 100
# attributes for all lj Objects:  name,  xy_list, c, layer 
# + for RelativeObjects : closed, xpos , ypos , resize , rotx , roty , rotz
def OSCobj(path, tags, args, source):

    obj = eval(args[0]+"."+ args[1])
    obj = args[2]


def OSCvar(path, tags, args, source):

    obj = eval(args[0])
    obj = args[1]


def addOSCdefaults(server):
    global oscserver

    oscserver = server
    oscserver.addMsgHandler( "default", OSChandler )
    oscserver.addMsgHandler( "/ping", OSCping)
    oscserver.addMsgHandler( "/quit", OSCquit)
    oscserver.addMsgHandler( "/"+ name + "/adddest", OSCadddest)
    oscserver.addMsgHandler( "/"+ name + "/deldest", OSCdeldest)
    oscserver.addMsgHandler( "/"+ name + "/obj", OSCobj)
    oscserver.addMsgHandler( "/"+ name + "/var", OSCvar)



#
# Drawing basic functions
# 

def rgb2int(r,g,b):
    return int('0x%02x%02x%02x' % (r,g,b),0)


def LineTo(xy, c, layer ):
 
    layers[layer].append((xy + (c,)))

def rLineTo(xy, c, layer , xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0):

    layers[layer ].append((Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz) + (c,)))


def Line(xy1, xy2, c, layer ):
    LineTo(xy1, 0, layer )
    LineTo(xy2, c , layer )

def rLine(xy1, xy2, c, layer ,  xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0):
    rLineTo(xy1, 0, layer )
    rLineTo(xy2, c , layer )


def PolyLineOneColor(xy_list, c, layer , closed ):
    #print "--"
    #print "c",c
    #print "xy_list",xy_list
    #print "--"
    xy0 = None      
    for xy in xy_list:
        if xy0 is None:
            xy0 = xy
            #print "xy0:",xy0
            LineTo(xy0,0, layer )
            LineTo(xy0,c, layer )
        else:
            #print "xy:",xy
            LineTo(xy,c, layer )
    if closed:
        LineTo(xy0,c, layer )



# Computing points coordinates for rPolyline function from 3D and around 0,0 to pygame coordinates
def Pointransf(xy, xpos = 0, ypos =0, resize =1, rotx =0, roty =0 , rotz=0):

        x = xy[0] * resize
        y = xy[1] * resize
        z = 0

        rad = math.radians(rotx)
        cosaX = math.cos(rad)
        sinaX = math.sin(rad)

        y2 = y
        y = y2 * cosaX - z * sinaX
        z = y2 * sinaX + z * cosaX

        rad = math.radians(roty)
        cosaY = math.cos(rad)
        sinaY = math.sin(rad)

        z2 = z
        z = z2 * cosaY - x * sinaY
        x = z2 * sinaY + x * cosaY

        rad = math.radians(rotz)
        cosZ = math.cos(rad)
        sinZ = math.sin(rad)

        x2 = x
        x = x2 * cosZ - y * sinZ
        y = x2 * sinZ + y * cosZ

        #print xy, (x + xpos,y+ ypos)
        return (x + xpos,y+ ypos)
        '''
        to understand why it get negative Y
        
        # 3D to 2D projection
        factor = 4 * gstt.cc[22] / ((gstt.cc[21] * 8) + z)
        print xy, (x * factor + xpos,  - y * factor + ypos )
        return (x * factor + xpos,  - y * factor + ypos )
        '''

def rLineTo(xy, c, layer , xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0):

    layers[layer ].append((Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz) + (c,)))


def rLine(xy1, xy2, c, layer ,  xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0):
    
    LineTo(Pointransf(xy1, xpos, ypos, resize, rotx, roty, rotz),0, layer )
    LineTo(Pointransf(xy2, xpos, ypos, resize, rotx, roty, rotz),c, layer )



# Send 2D point list around 0,0 with 3D rotation resizing and reposition around xpos ypos
#def rPolyLineOneColor(self, xy_list, c, layer , closed, xpos = 0, ypos =0, resize =1, rotx =0, roty =0 , rotz=0):
def rPolyLineOneColor(xy_list, c, layer , closed, xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0):
    xy0 = None      
    for xy in xy_list:
        if xy0 is None:
            xy0 = xy
            LineTo(Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz),0, layer )
            LineTo(Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz),c, layer )
        else:
            LineTo(Pointransf(xy, xpos, ypos, resize, rotx, roty, rotz),c, layer )
    if closed:
        LineTo(Pointransf(xy0, xpos, ypos, resize, rotx, roty, rotz),c, layer )


def LineRGBTo(xy, red, green, blue, layer ):
 
    LineTo(xy, int('0x%02x%02x%02x' % (red,green,blue),0), layer )   

def LineRGB(xy1, xy2, red,green,blue, layer ):

    LineTo(xy1, 0, layer )
    LineTo(xy2,  int('0x%02x%02x%02x' % (red,green,blue),0) , layer )
    

def PolyLineRGB(xy_list, red, green, blue, layer , closed ):

    PolyLineOneColor(xy_list, int('0x%02x%02x%02x' % (red,green,blue),0), layer , closed )

def rPolyLineRGB(xy_list, red, green, blue, layer , closed, xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0):
     
     rPolyLineOneColor(xy_list, int('0x%02x%02x%02x' % (red,green,blue),0), layer , closed, xpos = 0, ypos =0, resize =0.7, rotx =0, roty =0 , rotz=0)
 


def Lineslayer(layer):
    print("Stupido !! your code is to old : use Drawlayer() instead of LinesPL()")
    Drawlayer(layer )


def Draw(layer ):
    #print '/pl/0/'+str(layer), str(layers[layer])
    if r.set('/pl/'+str(ClientNumber)+'/'+str(layer), str(layers[layer])) == True:
        #print '/pl/'+str(ClientNumber)+'/'+str(layer), str(layers[layer])
        layers[layer] = []
        return True
    else:
        return False

def Resetlayer(self, layer):
    layers[layer] = []


# 
#  "Destinations" management for layers
#


# Add a destination for a given layer
def Addest(layer, scene, laser):

    print (name,'adding',layer,scene,laser,'?')
    if Findest(layer, scene, laser) == -1:
        newdest = DestsObjects.counter + 1
        Dest0 = lj.DestObject(str(newdest), newdest, True, layer , scene, laser)
        print("New destination added with number", newdest)
    else:
        print("Destination already existed")


# OSC add a destination for a given layer 
# /pluginame/dest layer, scene, laser  
def OSCadddest(path, tags, args, source):

    Addests(int(args[0]),int(args[1]),int(args[2]))


# Find layer destination with its parameters in destinations dictionnary
def Findest(layer, scene, laser):

    print(name, 'searching layer,scene,laser',layer,scene,laser)
    for item in DestObjects.getinstances():
        #print(item)
        if item.layer == layer and item.scene == scene and item.laser == laser:
            #Dests.append(item[0])
            print('found number',item.number)
            return item.number
        else:
            print('no destination found')
            return -1
    '''
    #Dests = list()
    allDests = Dests.items()
    for item in allDests:
        print(item)
        if item[1] == layer and item[2] == scene and item[3] == laser:
            #Dests.append(item[0])
            return Dests[item[0]]
        else:
            return -1
    '''

# Find and remove a layer destination with its parameters in destinations dictionnary
def Deldest(layer, scene, laser):

    Destnumber = Findest(layer, scene, laser)
    print(name,'deleting Destination layer, scene, laser', layer,scene, laser)

    if Destnumber != -1:
        print('found DestObject', Destnumber)
        delattr(DestObjects, str(Destnumber))
        print("Destination", Destnumber,"was removed")
    else:
        print("Destination was not found")


# OSC Delete a destination for a given layer
# /pluginame/deldests layer, scene, laser  
def OSCdeldest(path, tags, args, source):

    Deldests(args[0],args[1],args[2])


# Replace Drawlayer if Destinations paradigm is implemented in plugin code
def DrawDests():

    # Objects style

    #print("DrawDest")

    for destination in DestObject.getinstances():
        #print (destination.name, destination.number, destination.active, destination.layer, destination.scene, destination.laser, layers[destination.layer] )

        #print(Dests[str(destination)])
        #print('/pl/'+str(Dests[str(destination)]["scene"])+'/'+str(Dests[str(destination)]["laser"]), ":", str(layers[Dests[str(destination)]["PL"]]))
        #print(len(layers[destination.layer]))
        if destination.active == True:
           if r.set('/pl/'+str(destination.scene)+'/'+str(destination.laser), str(layers[destination.layer])) == True:
               #print ('layer', destination.layer, '/pl/'+str(destination.scene)+'/'+str(destination.laser), str(layers[destination.layer]))
               pass
           else:
               print('Redis key modification failed')
    
    # Maybe one layer can be sent to multiple destination so they are all reset *after* all sending. 
    for layerss in range(4):

        layers[layerss] = []

    '''
    # Dictionnary style
    
    #print(Dests)
    for destination in range(len(Dests)):
        #print(Dests[str(destination)])
        #print('/pl/'+str(Dests[str(destination)]["scene"])+'/'+str(Dests[str(destination)]["laser"]), ":", str(layers[Dests[str(destination)]["layer"]]))
        if r.set('/pl/'+str(Dests[str(destination)]["scene"])+'/'+str(Dests[str(destination)]["laser"]), str(layers[Dests[str(destination)]["layer"]])) == True:
            #print '/pl/'+str(ClientNumber)+'/'+str(layer), str(layers[layer])
            pass
        else:
            print('Redis key modification failed')
    
    # Maybe one layer can be sent to multiple destination so they are all reset *after* all sending. 
    for destination in range(len(Dests)):

        layers[Dests[str(destination)]["layer"]] = []
    '''
'''
scenes = 4

def DrawDestslayer(layer):
    
    for scene in range(scenes):

        if Dests[laser]["scene"] != -1:
            if r.set('/pl/'+str(Dests[laser]["scene"])+'/'+str(Dests[laser]["laser"]), str(layers[Dests[laser]["laser"]])) == True:
            if r.set('/pl/'+str(ClientNumber)+'/'+str(layer), str(layers[layer])) == True:
                #print '/pl/'+str(ClientNumber)+'/'+str(layer), str(layers[layer])
                layers[Dests[laser]["laser"]] = []
                return True
            else:
                return False

'''

#
# High level drawing functions
# 


# Font1


ASCII_GRAPHICS = [

#implementé

    [(-50,30), (-30,-30), (30,-30), (10,30), (-50,30)],                         # 0
    [(-20,30), (0,-30), (-20,30)],                                              # 1
    [(-30,-10), (0,-30), (30,-10), (30,0), (-30,30), (30,30)],                  # 2
    [(-30,-30), (0,-30), (30,-10), (0,0), (30,10), (0,30), (-30,30)],           # 3
    [(30,10), (-30,10), (0,-30), (0,30)],                                       # 4
    [(30,-30), (-30,-30), (-30,0), (0,0), (30,10), (0,30), (-30,30)],           # 5
    [(30,-30), (0,-30), (-30,-10), (-30,30), (0,30), (30,10), (30,0), (-30,0)], # 6
    [(-30,-30), (30,-30), (-30,30)],                                            # 7
    [(-30,30), (-30,-30), (30,-30), (30,30), (-30,30), (-30,0), (30,0)],        # 8
    [(30,0), (-30,0), (-30,-10), (0,-30), (30,-30), (30,10), (0,30), (-30,30)], # 9

# A implementer 
    [(-30,10), (30,-10), (30,10), (0,30), (-30,10), (-30,-10), (0,-30), (30,-10)], #:
    [(-30,-10), (0,-30), (0,30)], [(-30,30), (30,30)],                          # ;
    [(-30,-10), (0,-30), (30,-10), (30,0), (-30,30), (30,30)],                  # <
    [(-30,-30), (0,-30), (30,-10), (0,0), (30,10), (0,30), (-30,30)],           # =
    [(30,10), (-30,10), (0,-30), (0,30)],                                       # >
    [(30,-30), (-30,-30), (-30,0), (0,0), (30,10), (0,30), (-30,30)],           # ?
    [(30,-30), (0,-30), (-30,-10), (-30,30), (0,30), (30,10), (30,0), (-30,0)], # @

# Implementé
    

    [(-30,30), (-30,-30), (30,-30), (30,30), (30,0), (-30,0)],              # A
    [(-30,30), (-30,-30), (30,-30), (30,30), (30,0), (-30,0)],              # A
    [(-30,30), (-30,-30), (30,-30), (30,30), (-30,30), (-30,0), (30,0)],    # B
    [(30,30), (-30,30), (-30,-30), (30,-30)],                               # C
    [(-30,30), (-30,-30), (30,-30), (30,30), (-30,30)],                     # D
    [(30,30), (-30,30), (-30,-0), (30,0), (-30,0), (-30,-30), (30,-30)],    # E
    [(-30,30), (-30,-0), (30,0), (-30,0), (-30,-30), (30,-30)],             # F
    [(0,0), (30,0), (30,30), (-30,30), (-30,-30),(30,-30)],                 # G
    [(-30,-30), (-30,30), (-30,0), (30,0), (30,30), (30,-30)],              # H
    [(0,30), (0,-30)],                                                      # I
    [(-30,30), (0,-30), (0,-30), (-30,-30), (30,-30)],                      # J
    [(-30,-30), (-30,30), (-30,0), (30,-30), (-30,0), (30,30)],             # K
    [(30,30), (-30,30), (-30,-30)],                                         # L
    [(-30,30), (-30,-30), (0,0), (30,-30), (30,30)],                        # M
    [(-30,30), (-30,-30), (30,30), (30,-30)],                               # N
    [(-30,30), (-30,-30), (30,-30), (30,30), (-30,30)],                     # O
    [(-30,0), (30,0), (30,-30), (-30,-30), (-30,30)],                       # P
    [(30,30), (30,-30), (-30,-30), (-30,30), (30,30),(35,35)],              # Q
    [(-30,30), (-30,-30), (30,-30), (30,0), (-30,0), (30,30)],              # R
    [(30,-30), (-30,-30), (-30,0), (30,0), (30,30), (-30,30)],              # S
    [(0,30), (0,-30), (-30,-30), (30,-30)],                                 # T
    [(-30,-30), (-30,30), (30,30), (30,-30)],                               # U
    [(-30,-30), (0,30), (30,-30)],                                          # V
    [(-30,-30), (-30,30), (0,0), (30,30), (30,-30)],                        # W
    [(-30,30), (30,-30), (-30,-30), (30,30)],                               # X
    [(0,30), (0,0), (30,-30), (0,0), (-30,-30)],                            # Y
    [(30,30), (-30,30), (30,-30), (-30,-30)],                               # Z
    
                # A implementer 

    [(-30,-10), (0,-30), (0,30)], [(-30,30), (30,30)],                      # [
    [(-30,-10), (0,-30), (30,-10), (30,0), (-30,30), (30,30)],              # \
    [(-30,-30), (0,-30), (30,-10), (0,0), (30,10), (0,30), (-30,30)],       # ]
    [(30,10), (-30,10), (0,-30), (0,30)],                                   # ^
    [(30,-30), (-30,-30), (-30,0), (0,0), (30,10), (0,30), (-30,30)],       # _
    [(30,-30), (0,-30), (-30,-10), (-30,30), (0,30), (30,10), (30,0), (-30,0)], # `
    
            # Implementé
    
    [(-20,20), (-20,-20), (20,-20), (20,20), (20,0), (-20,0)],              # a
    [(-20,20), (-20,-20), (20,-20), (20,20), (-20,20), (-20,0), (20,0)],    # b
    [(20,20), (-20,20), (-20,-20), (20,-20)],                               # c
    [(-20,20), (-20,-20), (20,-20), (20,20), (-20,20)],                     # d
    [(20,20), (-20,20), (-20,-0), (20,0), (-20,0), (-20,-20), (20,-20)],    # e
    [(-20,20), (-20,-0), (20,0), (-20,0), (-20,-20), (20,-20)],             # f
    [(0,0), (20,0), (20,20), (-20,20), (-20,-20),(20,-20)],                 # g
    [(-20,-20), (-20,20), (-20,0), (20,0), (20,20), (20,-20)],              # h
    [(0,20), (0,-20)],                                                      # i
    [(-20,20), (0,-20), (0,-20), (-20,-20), (20,-20)],                      # j
    [(-20,-20), (-20,20), (-20,0), (20,-20), (-20,0), (20,20)],             # k
    [(20,20), (-20,20), (-20,-20)],                                         # l
    [(-20,20), (-20,-20), (0,0), (20,-20), (20,20)],                        # m
    [(-20,20), (-20,-20), (20,20), (20,-20)],                               # n
    [(-20,20), (-20,-20), (20,-20), (20,20), (-20,20)],                     # o
    [(-20,0), (20,0), (20,-20), (-20,-20), (-20,20)],                       # p
    [(20,20), (20,-20), (-20,-20), (-20,20), (20,20),(25,25)],              # q
    [(-20,20), (-20,-20), (20,-20), (20,0), (-20,0), (20,20)],              # r
    [(20,-20), (-20,-20), (-20,0), (20,0), (20,20), (-20,20)],              # s
    [(0,20), (0,-20), (-20,-20), (20,-20)],                                 # t
    [(-20,-20), (-20,20), (20,20), (20,-20)],                               # u
    [(-20,-20), (0,20), (20,-20)],                                          # v
    [(-20,-20), (-20,20), (0,0), (20,20), (20,-20)],                        # w
    [(-20,20), (20,-20)], [(-20,-20), (20,20)],                             # x
    [(0,20), (0,0), (20,-20), (0,0), (-20,-20)],                            # y
    [(20,20), (-20,20), (20,-20), (-20,-20)],                               # z

    [(-2,15), (2,15)]                                                       # Point a la place de {
]


def DigitsDots(number,color):
    dots =[]
    for dot in ASCII_GRAPHICS[number]:
        #print dot
        dots.append((gstt.xy_center[0]+dot[0],gstt.xy_center[1]+dot[1],color))
        #self.point_list.append((xy + (c,)))
    return dots

def CharDots(char,color):

    dots =[]
    for dot in ASCII_GRAPHICS[ord(char)-46]:
        dots.append((dot[0],dot[1],color))
    return dots

def Text(message,c, layer, xpos, ypos, resize, rotx, roty, rotz):

    dots =[]

    l = len(message)
    i= 0
    #print()
    # print (message)
    
    for ch in message:
        
        #print ""
        # texte centre en x automatiquement selon le nombre de lettres l
        x_offset = 26 * (- (0.9*l) + 3*i)
        # Digits
        if ord(ch)<58:
            char_layer_list = ASCII_GRAPHICS[ord(ch) - 48]
        else: 
            char_layer_list = ASCII_GRAPHICS[ord(ch) - 46]

        char_draw = []
        #dots.append((char_layer_list[0][0] + x_offset,char_layer_list[0][1],0))

        for xy in char_layer_list:
            char_draw.append((xy[0] + x_offset,xy[1],c))
        i +=1
        #print ch,char_layer_list,char_draw            
        rPolyLineOneColor(char_draw, c, layer , False, xpos, ypos, resize, rotx, roty, rotz)
        #dots.append(char_draw)

def TextRGB(message,c, layer, xpos, ypos, resize, rotx, roty, rotz):

    Text(message,int('0x%02x%02x%02x' % (red,green,blue),0), layer, xpos, ypos, resize, rotx, roty, rotz)






    