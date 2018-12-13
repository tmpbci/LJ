
#!/usr/bin/env python
# coding=UTF-8
"""

TCP server for rebol links like from Amiga
Forward /pl/lasernumber pointslist to redis server


by Sam Neurohack 
from /team/laser

"""	

import socket, time,random, redis


r = redis.StrictRedis(host=gstt.LjayServerIP, port=6379, db=0)



# TCP listener
   
TCP_IP = '127.0.0.1'
TCP_PORT = 13857
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connection address:', addr


while 1:
       data = conn.recv(BUFFER_SIZE)
       if not data: break
       #print "received data:", data
       commands = data.split()
       nb_oscargs = len(commands)
       print commands

	   #r.set('/pl/'+str(PL), str(something to code with commands, nb_oscargs))
       #conn.send(data)  # echo
       
       
conn.close()