
#!/usr/bin/env python
# coding=UTF-8
"""

Http server for red 0.6.4
Forward /pl/lasernumber pointslist to redis server

by Sam Neurohack 
from /team/laser

"""	


import redis

r = redis.StrictRedis(host=gstt.LjayServerIP, port=6379, db=0)

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		
		# Send the html message
		self.wfile.write("Hello World !")
		
		# r.set('/pl/'+str(PL), str(self.grid_points))
		
		return

try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
server.socket.close()






