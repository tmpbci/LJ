LJ v0.8.1

By Sam Neurohack, Loloster, Cocoa

LICENCE : CC BY


![LJ](http://www.teamlaser.fr/thsf/images/fulls/THSF9-33.jpg)

A software laser server with GUI for up to 4 lasers live actions. Think creative like Laser "battles", planetarium, sharing available lasers in demoparties for competition, ... 

 

LJ has 5 main components : 

- A "tracer" per etherdream/laser that take its given point list, correct geometry, recompute in laser controller coordinates, send it to its controller and report its status to the "manager".
- A "manager" that talk to all tracers (which client number point lists to draw, new geometry correction,...), handle the webui functions, OSC commands,...
- To share the lasers between people/computers, LJ accept up to 4 virtual "clients" that can simultaneously send one point list per laser. You select in WebUI wich "client" should be used by tracers.
- A web GUI in html, css, and vanilla js. No html server or js framework here : it's complex enough. This GUI has a (currently slow) simulator, but one can used a builtin python simulator (pysimu) or an etherdream/laser emulator (from nannou) to work without physical lasers !! 
- A network available database (redis). "Clients" send directly their pointlists to redis and each "tracer" is instructed to get a given pointlist in redis. 


4 clients can send 4 pointlists so up to 16 pointlists can be accessed at anytime from anywhere in the network. The server/network/webUI idea allows to share cpu intensive tasks and especially give tracers enough cpu to draw smoothly. Of course all this can happen in one computer. There is no real limits : 4 everything is tested and works smoothly if *you have enough cpu/computers/network ressources*. 

It's obviously overkill for one laser in a garage, but for several laserS game events, laserS art, laserS competition, laserS planetarium,... LJ will handle the complexity. Content providers like artists, demomakers,... just need to send points.

Needs at least : an etherdream DAC connected to an ILDA laser, RJ 45 IP network (gigabits only !!  no wifi, 100 mpbs doesn't work well with several lasers)

LJ is tested with Firefox, supports Linux and OS X. Windows is unkown but welcome, if someone want to jump in and care about it. 

LJ is in dev : versions in this repository will always be core functionnal : accept and draw pointlists. New features can be not fully implemented, wait for the next commit. Any feedback is welcome at any time.



#
# Features among many others.
# 

(Doc in progress)

- Laser alignment like in laser mapping.
- OSC and websocket commands. Very cool : LJ can script or be scripted.
- Web ui : In your browser open webui/index.html. Javascript is needed. By default it connect to localhost. If you want to control a remote server, you need to change the uri line in LJ.js.
- Status update every 0.5 seconds : every etherdream DAC state, number of buffer points sent,...
- "Optimisation" points automatically added, can be changed live for glitch art. Search "resampler" commands.
- A compiled version for os x and linux of nannou.org etherdream+laser emulator is included. For more informations, like license see https://github.com/nannou-org/ether-dream
- Some fancy examples are available : 3D anaglyph, Laser Pong,...




#
# Install 
#

With Linux, type in a terminal window :

./install.sh

For OS X, you need brew already installed, then :

brew update
brew upgrade
brew install redis
type all install.sh commands beginning line 4. An OS X install script soon !!

For Linux and OS X :

You probably want redis bound to all network interfaces : comment the bind line in /etc/redis/redis.conf and restart it.

In webui/index.html change the websocket (ws) ip adress to the server IP if needed.

Using the same idea check all ip address in LJ.conf.

There is a nice websocket debug tool : websocat.



#
# To run
#

Correct launch order is :

- Dac/Laser (emulator or IRL)
- Redis server once.
- This server. see below.
- Load/reload webUI page from disk in a browser (webui/index.html). Javascript must be enabled.
- Run a plugin, see in clients/plugins folder for examples.


A typical server start is python main.py -L numberoflasers. 
Use also -h to display all possible arguments, like -v for debug informations.


CASE 1 : the laser server computer is the same that the computer running a client :


1/ Run LJ

python main.py -L 1

2/ Check in your client code if the laser server IP is the good one

Run your client

3/ to monitor redis server, there is an app for that (redis-manager/medis/...) or :
redis-cli monitor



CASE 2 : Server and Client computers are different :


1/ Say the laser server computer (running LJ) IP is 192.138.1.13, the client computer is 192.168.1.52, First remember to check on the server computer if the redis server is listening to the right IP :

edit /etc/redis/redis.conf

2/ Launch LJ with -r argument :
python main.py -r 192.168.1.13 -L 1

3/ run a client/plugin on client computer, like :

node nodeclient.js

4/ to monitor redis server use redis-manager/medis/... or :

redis-cli -h redisserverIP monitor


#
# Plugins 
#

A "plugin" is a software that send any number of pointlist(s). LJ comes with different plugins in python 3 :

- LiveWords 	: Fill the input form and it's displayed. One word / laser.
- Textcycl		: Cycle some words with adjustable length on one laser.
- Anaglyph  	: A green/red rotating cube. Try it with green/red 3D glasses !
- Planetarium 	: A 4 lasers planetarium.
- pySimu 		: A full speed laser simulator (pygame, python 2.7)
- LaserPong		: Our laser Pong is back ! (python 2.7)


#
# Program your own "plugin" 
#


The server approach is based on redis, so you write and run your laser client software in any redis capable programming langage (50+ : https://redis.io/clients). If you want some interaction with GUI, like in text status area, you also need OSC.

- Read all this readme ;-)
- There is a client and plugin folders with examples in different languages. If you want to do game especially with pygame, see ljpong in plugins/games directory.
- Generate at least one point list array (say a square) with *enough points*, one point is likely to fail for buffering reason.
- Feed your point list array in string format to redis server. i.e use "/pl/0/1" redis key to feed client 0, pointlist 1.
- Tell LJ.conf your plugin configuration : OSC port and command line to start it.
- lj3.py (python 3) and lj.py (python 2.7) have many very useful functions to not reinvent the wheel. Maybe it's better to symlink them in your directory than having a separated copy, to get future enhancements transparently. 


#
# Nannou etherdeam simulator
#

(Doc in Progress)


#
# Todo
#

(Doc in Progress)

- kpps live modification for glitch art.
- A grid style warp correction process in webUI.
- IP change should not need a LJ relaunch
- Way faster WebUI simulator. Use pysimu plugin for full speed.


#
# Networking
#


LJ is network based and this is *critical and flickering reason #1* if not managed properly, especially if you have several lasers.

Our "always working solution", as we regularly move our gear for different venues :

- We use static network configuration. Our Etherdreams controllers have static IPs defined in their SDcard from 192.168.1.1 to 192.168.1.9. 

- Because wifi will always finally sucks for many reasons, our computers (laser server and clients) are *gigabits wired* with 192.168.1.10 and after. Don't trust end user gear marketing on wifi. We have a big gigabits switch for the *laser only lan*. We provide Internet through wifi on a different network like 192.168.2.x if really needed.

- Again, even if etherdreams are 100 Mbits, we use *gigabits* gear.


By default LJ uses on 127.0.0.1 (localhost) :

- A websocket on port 9001 for WebUI interaction.
- The redis server on port 6379 ('ljayserverip')
- An OSC server on port 8002 for remote control via OSC and plugins.
- Some OSC clients defined in LJ.conf to forward commands to defined plugins


You need to update LJ.conf to your network/etherdreams IPs and be sure to check command arguments : python main.py --help

The need for a dedicated computer to act as "laser server" usually depends on how many lasers you want to control and your main computer load. If you seen flickering with small point lists, try the dedicated computer option and/or stop process interfering like redis monitoring,...



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
