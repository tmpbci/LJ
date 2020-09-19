LJ v0.8.2

By Sam Neurohack, Loloster, Cocoa

LICENCE : CC BY


![LJ](http://www.teamlaser.tk/lj/images/lj2.png)

A software laser framework with GUI, for up to 4 lasers live actions with ethedreams DACs. Think creative like Laser "battles", planetarium, sharing available lasers in demoparties for competition, ... 

 

LJ has 5 main components : 

- "Plugins" are points generators (to one or more lasers). Lot examples comes with LJ : planetarium, 3D anaglyph animations,... See plugins directory.
- A "tracer" per etherdream/laser that take its given point list, correct geometry, recompute in laser controller coordinates, send it to its controller and report its status to the "manager".
- A "manager" that talk to all tracers (which client number point lists to draw, new geometry correction,...), handle IOs (webui functions, OSC commands,...) and plugins.
- A web GUI in html, css, and vanilla js. No html server or js framework here : it's complex enough. This GUI has a (currently slow) simulator, but one can also use an etherdream/laser emulator (from nannou) to work without physical lasers !! 
- A network available database (redis). "Plugins" can send directly their pointlists to redis and each "tracer" is instructed to get one of the avalaible pointlist in redis.


![Scenes](http://www.teamlaser.tk/lj/images/scenes.png)

LJ accept up to 4 groups = virtual "scenes" of 4 "pointlists" each (= one pointlist per laser), so up to 16 pointlists can be sent to redis at anytime from anywhere in the network. The idea behind this is to easily share actual lasers. Imagine in demo party :

Erica needs 4 lasers, that's the 4 pointlists of "scene" 0.
Paula and Jennifer use only 2 lasers each, so they can share "scene" 1.
And so on..

The server/network/webUI idea allows to spread cpu intensive tasks on different cpu cores and especially give tracers enough cpu to feed etherdreams DACs smoothly. Of course all this can happen in one computer. There is no real limits : 4 everything is tested and works smoothly if *you have enough cpu/computers/network ressources*. 

It's obviously overkill for one laser in a garage, but for several laserS games events, laserS art, laserS competition, laserS planetarium,... LJ will handle the complexity. Content providers like artists, demomakers,... just need create plugin in whatever langage, send the points to redis. 

To change current scene used by lasers/tracers use the command : /scene/scenenumber/start 1 


Registering the plugin in LJ.conf is absolutely not mandatory. 

Needs at least : an etherdream DAC connected to an ILDA laser, RJ 45 IP network (gigabits only !! wifi and wired 100 mpbs doesn't work well with several lasers). Seriously : if you experience frame drops you need to upgrade your network and use a dedicated computer to run seperately main program from plugins, youtube,...

LJ is tested with Firefox, supports Linux and OS X. Windows is unkown but welcome, if someone want to jump in. 

LJ is in dev : versions in this repository will always be core functionnal : accept and draw pointlists. New features can be not fully implemented, wait for the next commit. Any feedback is welcome at any time.



#
# Features among many others.
# 

(Doc in progress)

- Intensity and kpps live modification.
- Some Lasermapping ('alignment') like in videomapping.
- OSC and websocket commands. Very cool : LJ can script or be scripted.
- Python3 
- Web User Interface in your browser : open www/index.html. Javascript is needed. By default it connect to localhost. If you want to control remotely, you need to change the uri line in LJ.js.
- Live WebUI extras : change debug level, restart plugin, rescan DACs,...
- Status update every 0.5 seconds : every etherdream DAC state, number of buffer points sent,...
- "Optimisation" points automatically added, can be changed live for glitch art. Search "resampler" commands.
- A compiled version for os x and linux of nannou.org etherdream+laser emulator is included. For more informations, like license see https://github.com/nannou-org/ether-dream
- Some fancy examples are available : 3D anaglyph, Laser Pong,...
- Midi and audio reactive, look midigen.py and fft3.py
- Webcam live face display (trckr). Openpose skeletons animations laser player.
- Resolume OSC client.
- Another project (bhorpad) has been merged in LJ : so if you have a led matrix, like Launchpad mini or bhoreal, plug it and you may define, launch macros as pushing on leds or use them to display informations.
- Artnet receiver plugin, another possibity to script LJ.
- Ableton link time synchro support.
- Maxwell laser synth emulation plugin. Work in progress
- Plugins list auto start, see line in LJ.conf : autostart = artnet
- user.py plugin code example


#
# Install 
#

With Linux, in LJ directory, type in a terminal window :

cd server 
./install.sh

Server directory also contains config files for optionnal nginx, supervisorctl and syncthing.


For OS X, you need brew already installed, then :

brew update
brew upgrade
brew install redis
type all install.sh commands beginning line 4. An OS X install script soon !!

For Linux and OS X :

You probably want redis bound to all network interfaces : comment the bind line in /etc/redis/redis.conf and restart it.

WebUI pages needs to know the LJ IP address. So you need to change the line wwwIP = "192.168.2.43" in updateUI.py then run python updateUI.py 

Using the same idea check all ip address in LJ.conf.

There is a nice websocket debug tool : websocat.



#
# To run
#

Correct launch order is :

- Switch on Dac/Laser (emulator or IRL)
- Redis server, usually automatically start at boot if redis is a service or you launched manually : redis-server &
- This program. see below.
- Load/reload webUI page from disk in a browser (www/index.html). Javascript must be enabled. 
- Run a builtin plugin or your generator, to send pointlists in redis. See in clients/plugins folder for examples.


A typical LJ start is :

python3 main.py -L numberoflasers. 

Use also -h to display all possible arguments, like -v for debug informations. 


CASE 1 : the laser server computer, where LJ runs, is the same that the computer running a generator/plugin :


1/ Run LJ

python3 main.py -L 1

2/ Check in your client code if the laser server IP is the good one

Run your client

3/ to monitor redis server, there is an app for that (redis-manager/medis/...) or :
redis-cli monitor 
redis-cli --stat
redis-cli  then ask for the key you want like : get /pl/0/0


CASE 2 : Server and Client computers are different :


1/ Say the laser server computer (running LJ) IP is 192.138.1.13, the client computer is 192.168.1.52, First remember to check on the server computer, if the redis server is listening to the right IP :

edit /etc/redis/redis.conf

2/ Launch LJ with -r argument :
python3 main.py -r 192.168.1.13 -L 1

3/ If the webUI is launched on "client" computer, update uri line in LJ.js

4/ run a client/plugin on client computer, like :

node nodeclient.js

5/ to monitor redis server use redis-manager/medis/... or :

redis-cli -h redisserverIP monitor


#
# Plugin
#

A "plugin" is a software that send any number of pointlist(s). LJ comes with different plugins in python 3 :

- artnet receiver : port 6454
- Aurora : Fill the input form and it's displayed. One word / laser.

#
# Client Side : Program your own "plugin" 
#

The server approach is based on redis, so you can write and run your laser client software in any redis capable programming langage (50+ : https://redis.io/clients). An external program that just send pointlists is a "client". If you want some interactions from the webUI, like text status area support, crash detection, launch,... it's a "plugin" and some default code is needed. See custom1.py, a basic plugin you can modiffy. LJ and plugins signaling is mainly over OSC.

- Read all this readme ;-)
- Generate at least one pointlist array (say a square) with *enough points*, one point is likely to fail for buffering reason. See command reference below for more.
- Feed your point list array in string format to redis server. i.e use "/pl/0/1" redis key to feed scene 0, laser 1.
- Tell LJ.conf your plugin configuration : OSC port and command line to start it.
- At least a plugin must reply /pong to OSC request /ping.

Currently the WebUI (www/index.html) is static. 

#
# Client side dope mode : How to use lj23 (python3)
# 

lj23 have many very useful functions to not reinvent the wheel for advanced points generation "client" side : layers, sprites, built in rotations,..
 

4 Great TRICKS with lj23 :

First open square.py and learn how to declare different objects. square.py is a 2D shape example in 3D rotation (red/green anaglyph rendering) that use 2 layers : one for left eye and one for right eye.


1/ How to have another laser drawing the same thing ?

That's a destination problem : just add another destination !

Dest1 = lj.DestObject('1', 1, True, 0 , 1, 1)	# Dest1 will also send layer 0 points to scene 1, laser 1 


![Layers](http://www.teamlaser.tk/lj/images/layer.png)

2/ Different layers to different lasers ?

Say because of too much points you want Left element drawn by scene 0, laser 0 and right element by scene 0, laser 1

First define a different object/layer for each drawn element :

Leftsquare = lj.FixedObject('Leftsquare', True, 255, [], red, 255, 0, 0, 0 , True)		 # Left goes to layer 0

Rightsquare = lj.FixedObject('Rightsquare', True, 255, [], green, 0, 255, 0, 1 , True)	 # Right goes to layer 1

Define 2 destinations :

Dest0 = lj.DestObject('0', 0, True, 0 , 0, 0) 	# Dest0 will send layer 0 points to scene 0, laser 0 

Dest1 = lj.DestObject('1', 1, True, 1 , 0, 1)	# Dest1 will send layer 1 points to scene 0, laser 1 



3/ Different layers to one laser ?

You should consider adding all your points to one layer, but same as 1/ it's a destination problem, just add another destination with the same scene/laser for this layer

Dest1 = lj.DestObject('1', 1, True, 1 , 0, 0)	# Dest1 will also send layer 1 points to scene 0, laser 0 



4/ I want to animate/modify anything on the fly : I'm doing a game and suddenly my hero change color.

It's a drawn object problem : there is two kind of drawn ojects : 

- "Fixed" objects : you generate points in 2D from 0,0 top left and 500,500 is bottom right. Say Hero is a Fixed Object, you can directly change value of 

Hero.name, Hero.active, Hero.intensity, Hero.xy, Hero.color, Hero.red, Hero.green, Hero.blue, Hero.layer, Hero.closed

- "Relative" Object : is a kind of laser sprite : your points in 'objectname.xy' has to be around 0,0,0. The other properties let you describe the actual position (xpos, ypos), resize,..

i.e for a character "PNC" vanishing in one point declared as a "Relative" Object, you can decrease resize parameter : PNC.resize

PNC.name, PNC.active, PNC.intensity, PNC.xy, PNC.color, PNC.red, PNC.green, PNC.blue, PNC.layer, PNC.closed, PNC.xpos, PNC.ypos, PNC.resize, PNC.rotx, PNC.roty, PNC.rotz



Same for Dest0 if it's a destObject, properties are :
Dest0.name, Dest0.number, Dest0.active, Dest0.layer, Dest0.scene, Dest0.laser


DrawDests() will take care of all your declared drawn elements/"objects" and Destinations to generate a point list per scene/laser sent to redis. In client point of view a "pointlist" is the sum of all its declared "layers".


#
# Nannou etherdeam simulator
#

2 compiled nannou visualisers are included, one for Linux, one for macOS. It's pretty old version but much more compatible with "old" builtin processors GPU. 


#
# Todo
#

(Doc in Progress)

- A grid style warp correction process in webUI.
- IP change should not need a LJ relaunch
- Way faster WebUI simulator.


#
# Networking
#


LJ is network based and this is *critical and flickering reason #1* if not managed properly, especially if you have several lasers.

Our "always working solution", as we regularly move our gear for different venues :

- We use static network configuration. Our Etherdreams controllers have static IPs defined in their SDcard from 192.168.1.1 to 192.168.1.9. 

- Because wifi will always finally sucks for many reasons, our computers (LJ server and plugins) are *gigabits wired* with IP 192.168.1.10 and after. Don't trust end user gear marketing on wifi. We have a big gigabits switch for the *laser only lan*. We provide Internet through wifi on a different network like 192.168.2.x if really needed.

- Again, even if etherdreams are 100 Mbits, we use *gigabits* gear.


By default LJ uses on 127.0.0.1 (localhost) :

- A websocket on port 9001 for WebUI interaction.
- The redis server on port 6379 ('ljayserverip').
- An OSC server on port 8002 for remote control via OSC and plugins.
- Some OSC clients defined in LJ.conf to forward commands to defined plugins.


You need to update LJ.conf to your network/etherdreams IPs and be sure to check command arguments : python3 main.py --help

The need for a dedicated computer to act as "laser server" usually depends on how many lasers you want to control and your main computer load. If you seen flickering with small point lists, try the dedicated computer idea and/or stop process interfering like redis monitoring,...

# 
# Glitch art 
#

For nice lines and angles all user pointlists are automatically resampled by tracers. There is 2 cases defined for resampling strategy : short and long distance between 2 points.


short distance : has one step : (1.0, number repetition at destination position). 1.0 = 100% = end of the line between the 2 points. For example : (1.0, 8) means the end point will be repeated 8 times.

long distance has 3 steps : (0.25, 3), (0.75, 3), (1.0, 10) : means an extra point at 25% is created and repeated 3 times, another at 75% repeated also 3 times and destination point is repeated 10 times. 

For glitching experience you can change resampling strategy live with "resampler" command. See command reference. [short distance, long distance] = [(1.0, 8),(0.25, 3), (0.75, 3), (1.0, 10)]

# 
# Colors
#

LJ is compatible with TLL and analog modulation. Each point color if an int value, wich is simply the hex color in decimal. Example : white #fffff will be 65535.

# 
# Ether dream configuration
#

![Etherdream Laser DAC](https://www.ether-dream.com/ed2-external.jpg)

This program suppose that the ether dream is configured in a certain way especially for its IP address. We write an autoplay.txt file inside an SD Card within the ether dream DAC, with the following lines you can adjust i.e for pps or fps. Yes, there is a builtin DHCP client in the ether dream DAC but if you run multiple lasers, having a fixed dedicated network makes you focus on laser stuff.

/net/ipaddr 192.168.1.3

/net/netmask 255.255.255.0

/net/gateway 192.168.1.10

/ilda/pps 25000

/ilda/fps 25

About hardware setup, especially if you have several lasers : ILDA cables are insanely expensive. You may consider the Power Over Ethernet 'POE' option. Buy a very small ILDA cable, a POE splitter and connect everything to the ether dream fixed near your laser. You can have then a simple and very long network cable and use a Power Over Ethernet injector or switch close to the driving computer. Beware some vendors use 24V POE Injector : POE injectors and splitters must match.


# 
# LJ commands reference
#

All commands are available via OSC or websocket.

8002 OSC incoming

9001 Websocket 


/pl/scenenumber/lasernumber value : value is the pointlist to draw as string. Example : 
/pl/0/0 "[(150.0, 230.0, 65280), (170.0, 170.0, 65280), (230.0, 170.0, 65280), (210.0, 230.0, 65280), (150.0, 230.0, 65280)]"


/scale/X/lasernumber value   

/scale/Y/lasernumber value

/swap/X/lasernumber value (0 or 1) 

/swap/Y/lasernumber value (0 or 1) 

/angle/lasernumber value : increase/decrease angle correction for given laser by value

/loffset/X/lasernumber value : change X offset of given laser by value

/loffset/Y/lasernumber value : change Y offset of given laser by value


/kpps/lasernumber value : live change of kpps
/intens/lasernumber value : increase/decrease intensity for given laser by value. Needs analog modulation laser


/client or /noteon < 8 : change client displayed for Current Laser
23 < /noteon < 32 : PL number displayed on webUI simulator    

/grid/lasernumber value (0 or 1) : switch given laser with grid display on or off

/black/lasernumber value (0 or 1) : set given laser to black on or off

/ip/lasernumber value : change given laser IP i.e '192.168.1.1'

/resampler/lasernumber lsteps : change resampling strategy (see glitch art), for given laser
lsteps is a string like "[ (1.0, 8),(0.25, 3), (0.75, 3), (1.0, 10)]"
 
/scene/scenenumber/start 0 or 1 : tell all tracers to use given scene

/regen : regen webui index html page.

/scim : change webui simulated laser.


All command beginning with a declared plugin name are forwarded automatically to given plugin : "/nozoid whatever" will be forwarded to nozoid client.


/forwardui "uicommand arg" : display *one* word on webui. There is 2 lines, first line (/status or /redstatus)
and second line (/line1 or /redline1). Examples of "uicommand arg" :

/status hello
/redline1 Error
/laser 0

![LJ Display](https://www.teamlaser.tk/lj/images/display.png)

Leds colors for each DACs

DAC state "stt" :
Laser not requested -> led is not lit
IDLE -> blue
PREPARE -> cyan
PLAYING  -> green

DAC answers (ack) :
replied ACK -> green
replied FULL -> orange
replied INVALID -> yellow

no connection to dac -> leds are red (6)

![LJ](http://www.teamlaser.tk/lj/images/calig.png)