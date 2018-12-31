LJ v0.7.0

By Sam Neurohack, Loloster, Cocoa

LICENCE : CC BY


![LJ](http://www.teamlaser.fr/thsf/images/fulls/THSF9-33.jpg)

A software laser server with GUI for up to 4 lasers live actions. Think creative like Laser "battles", planetarium,... 

LJ has 3 main components : 

- A tracer per etherdream/laser that take current client point list, correct geometry, recompute in etherdreams coordinates, send it to its controller,... and report etherdream status to the manager.
- A manager that talk to all tracers (which client number point lists to draw, new geometry correction,...), handle the webui functions, OSC commands,...
- Up to ten clients, that simultaneously send one point list per laser.

You run and write your clients in any redis capable programming langage (50+ : https://redis.io/clients).

Needs at least : an etherdream DAC connected to an ILDA laser, RJ 45 IP network (gigabits only !!  no wifi, 100 mpbs doesn't work well with several lasers)

The server approach is based on redis.

LJ supports Linux and OS X. Windows is unkown but welcome, if someone want to jump in and care about it.



#
# Features among many others.
# 

(Doc in progress)

- OSC and websocket commands. Very cool : LJ can script or be scripted.
- Interactive (mouse style) warp correction for each laser.
- Web ui : In your browser open webui/index.html. Javascript is needed.
- Status update every 0.5 seconds : every etherdream DAC state, number of buffer points sent,...
- "Optimisation" points automatically added, can be changed live for glitch art. Search "resampler" commands.
- A compiled version for os x and linux of nannou.org etherdream+laser emulator is included. For more informations, like license see https://github.com/nannou-org/ether-dream
- A 3D anaglyph client example

#
# External devices 
#

(Doc in Progress)



#
# Networking
#


LJ is network based and this is *critical and flickering reason #1* if not managed properly, especially you have several lasers.

Our "always working solution", as we regularly move our gear for different venues :

We use static network configuration. Our Etherdreams controllers have static IPs defined in their SDcard from 192.168.1.1 to 192.168.1.9. Because wifi will always finally sucks for many reasons, our computers (laser server and clients) are *gigabits wired connected* with 192.168.1.10 and after. Don't trust end user gear marketing on wifi, we have a big gigabits switch for laser only stuff. We provide Internet through wifi on different network like 192.168.2.x

Even if etherdreams are 100 Mbits, we use gigabits gear.


By default LJ uses on 127.0.0.1 (localhost) :

- A websocket on port 9001 for WebUI interaction.
- The redis server on port 6379 ('ljayserverip')
- An OSC server on port 8002.
- An OSC client for 'bhoroscIP' port 8001.
- An OSC client for Nozoids support on 'nozoscIP', port 8003.

You need to update LJ.conf to your network/etherdreams IPs and be sure to check command arguments : python main.py --help

A dedicated computer to act as "laser server" usually depends on how many lasers you want to control and your main computer load. If you seen flickering with small point lists, try the dedicated computer option and/or stop process interfering like redis monitoring,...



Program your own "Client" :
-------------------------

- Read the Introduction part in this readme.
- Carefully read all comments in clients examples.
- Generate at least one point list array (say a square). 
- Feed your point list array in string format to redis server.



#
# Install 
#

With Linux, type in a terminal window :

./install.sh

For OS X, you need brew already installed, then :

brew update
brew upgrade
brew install redis
type all install.sh commands beginning line 4.

For Linux and OS X :

Check the bind line in /etc/redis/redis.conf :

- If client and laser servers computers are the same, use 127.0.0.1
- Client and laser server are different, use the laser server computer IP.

In webui/index.html change the ws ip adress to the server IP or 127.0.0.1 if client computer = laser server computer.

Using the same idea check all ip address in LJ.conf.



#
# To run
#

A typical start is python main.py -L numberoflasers. Use -h to display all possible arguments. 
Always start the redis server first, then laser server, maybe those two should run on the same computer, then your client.

Case 1 : the laser server computer is the same that the computer running a client :

python main.py

Open/reload in browser webui/index.html. (javascript must be enabled)

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
# Todo
#

(Doc in Progress)

- kpps live modification for glitch art.
- Improve Bhoreal & LaunchPad inputs 
- Improve WebUI with simulator.
- Warp corrections should not used warpdestinations default values in conf file.



# 
# Ether dream configuration
#

![Etherdream Laser DAC](https://www.ether-dream.com/ed2-external.jpg)

This program suppose that the ether dream is configured in a certain way especially for its IP address. For ether dream 1 : write an autoplay.txt file inside an SD Card within the ether dream DAC, with the following lines you can adjust i.e for pps or fps. Yes, there is a builtin DHCP client in the ether dream DAC but if you run multiple lasers, having a fixed dedicated network makes you focus on laser stuff.

/net/ipaddr 192.168.1.3

/net/netmask 255.255.255.0

/net/gateway 192.168.1.1

/ilda/pps 25000

/ilda/fps 25

About hardware setup, especially if you have several lasers : ILDA cables are insanely expensive. You may consider the Power Over Ethernet 'POE' option. Buy a very small ILDA cable, a POE splitter and connect everything to the ether dream fixed near your laser. You can have then a simple and very long network cable and use a Power Over Ethernet injector or switch closed to the driving computer. Beware some vendors use 24V POE Injector : POE injectors and splitters must match.


#
# Coordinates if you use the proj() function
#

3D points (x,y,z) has *0,0,0 in the middle* 
A square centered around origin and size 200 (z =0 is added automatically) :
([-200, -200, 0], [200, -200, 0], [200, 200, 0], [-200, 200, 0], [-200, -200, 0])

Pygame screen points are 2D. *0,0 is top left*
with no 3D rotations + 3D -> 2D Projection  + translation to top left:
[(300.0, 400.0), (500.0, 400.0), (500.0, 200.0), (300.0, 200.0), (300.0, 400.0)]


Pygame points with color is fed to laser renderer
[(300.0, 400.0, 0), (500.0, 400.0, 16776960), (500.0, 200.0, 16776960), (300.0, 200.0, 16776960), (300.0, 400.0, 16776960)]


Laser points traced

Because of blanking many points are automatically added and converted in etherdream coordinates system -32765 to +32765 in x and y axis.

16 (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 65280, 65280, 0), (-1500.0, 1500.0, 0, 0, 0), (-1500.0, 1500.0, 0, 0, 0), (-1500.0, 1500.0, 0, 0, 0), (-1500.0, 1500.0, 0, 0, 0), (-1500.0, 1500.0, 0, 0, 0), (-1500.0, 1500.0, 0, 0, 0), (-1500.0, 1500.0, 0, 0, 0), (-1500.0, 1500.0, 0, 0, 0)
8 (1500.0, 1500.0, 65280, 65280, 0), (1500.0, 1500.0, 65280, 65280, 0), (1500.0, 1500.0, 65280, 65280, 0), (1500.0, 1500.0, 65280, 65280, 0), (1500.0, 1500.0, 65280, 65280, 0), (1500.0, 1500.0, 65280, 65280, 0), (1500.0, 1500.0, 65280, 65280, 0), (1500.0, 1500.0, 65280, 65280, 0)
8 (1500.0, -1500.0, 65280, 65280, 0), (1500.0, -1500.0, 65280, 65280, 0), (1500.0, -1500.0, 65280, 65280, 0), (1500.0, -1500.0, 65280, 65280, 0), (1500.0, -1500.0, 65280, 65280, 0), (1500.0, -1500.0, 65280, 65280, 0), (1500.0, -1500.0, 65280, 65280, 0), (1500.0, -1500.0, 65280, 65280, 0)
8 (-1500.0, -1500.0, 65280, 65280, 0), (-1500.0, -1500.0, 65280, 65280, 0), (-1500.0, -1500.0, 65280, 65280, 0), (-1500.0, -1500.0, 65280, 65280, 0), (-1500.0, -1500.0, 65280, 65280, 0), (-1500.0, -1500.0, 65280, 65280, 0), (-1500.0, -1500.0, 65280, 65280, 0), (-1500.0, -1500.0, 65280, 65280, 0)
