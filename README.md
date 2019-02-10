LJ v0.7.1

By Sam Neurohack, Loloster, Cocoa

LICENCE : CC BY


![LJ](http://www.teamlaser.fr/thsf/images/fulls/THSF9-33.jpg)

A software laser server with GUI for up to 4 lasers live actions. Think creative like Laser "battles", planetarium,... 

LJ has 3 main components : 

- A "tracer" per etherdream/laser that take its point list, correct geometry, recompute in etherdreams coordinates, send it to its controller,... and report etherdream status to the manager.
- A "manager" that talk to all tracers (which client number point lists to draw, new geometry correction,...), handle the webui functions, OSC commands,...
- Up to ten clients, that simultaneously send one point list per laser.

Needs at least : an etherdream DAC connected to an ILDA laser, RJ 45 IP network (gigabits only !!  no wifi, 100 mpbs doesn't work well with several lasers)

LJ supports Linux and OS X. Windows is unkown but welcome, if someone want to jump in and care about it.



#
# Features among many others.
# 

(Doc in progress)

- OSC and websocket commands. Very cool : LJ can script or be scripted.
- Web ui : In your browser open webui/index.html. Javascript is needed. By default it connect to localhost. If you want to control a remote server, you need to change the uri line in LJ.js.
- Status update every 0.5 seconds : every etherdream DAC state, number of buffer points sent,...
- "Optimisation" points automatically added, can be changed live for glitch art. Search "resampler" commands.
- A compiled version for os x and linux of nannou.org etherdream+laser emulator is included. For more informations, like license see https://github.com/nannou-org/ether-dream
- Some fancy examples are available : 3D anaglyph, Laser Pong, Laser Wars 



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

In webui/index.html change the ws ip adress to the server IP if needed.

Using the same idea check all ip address in LJ.conf.

There is a nice ws debug tool websocat.



#
# To run
#

Order is :

- Dac/Laser (emulator or IRL)
- Redis server once.
- This server. see below.
- Load/reload webUI page from disk in a browser (webui/index.html). Javascript must be enabled.
- Run a client, see in clients folder for examples.


A typical start is python main.py -L numberoflasers. Use -h to display all possible arguments. 

Case 1 : the laser server computer is the same that the computer running a client :

python main.py

Check in your client code if the laser server IP is the good one

Run your client

to monitor redis server :

redis-cli monitor


Case 2 : Server and Client computers are different :


Say the laser server computer (running LJ) IP is 192.138.1.13, the client computer is 192.168.1.52 

On the server computer :
edit /etc/redis/redis.conf
use -r argument :
python main.py -r 192.168.1.13

run the client on client computer, like :

node testredis.js

to monitor redis server :

redis-cli -h redisserverIP monitor



#
# Program your own "Client" 
#


The server approach is based on redis, so you write and run your laser client software in any redis capable programming langage (50+ : https://redis.io/clients).

- Read the Introduction part in this readme.
- There is a clients folders with examples in different languages.
- Generate at least one point list array (say a square). 
- Feed your point list array in string format to redis server.
- 


#
# Todo
#

(Doc in Progress)

- kpps live modification for glitch art.
- A grid style warp correction process in webUI


#
# Networking
#


LJ is network based and this is *critical and flickering reason #1* if not managed properly, especially if you have several lasers.

Our "always working solution", as we regularly move our gear for different venues :

We use static network configuration. Our Etherdreams controllers have static IPs defined in their SDcard from 192.168.1.1 to 192.168.1.9. Because wifi will always finally sucks for many reasons, our computers (laser server and clients) are *gigabits wired connected* with 192.168.1.10 and after. Don't trust end user gear marketing on wifi, we have a big gigabits switch for laser only stuff. We provide Internet through wifi on different network like 192.168.2.x

Even if etherdreams are 100 Mbits, we use gigabits gear.


By default LJ uses on 127.0.0.1 (localhost) :

- A websocket on port 9001 for WebUI interaction.
- The redis server on port 6379 ('ljayserverip')
- An OSC server on port 8002.
- An OSC client as output on port 8001.
- An OSC client for Nozoids support on 'nozoscIP', port 8003.

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
