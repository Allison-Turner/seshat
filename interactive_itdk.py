#! /usr/bin/env python3

from http.server import *

# creating a class for handling basic Get and Post Requests
class Interactive_ITDK(BaseHTTPRequestHandler):
    # for Get Request
    def do_GET(self):
        # Success Response --> 200
        self.send_response(200)
        
        self.send_header('content-type', 'text/html')
        self.end_headers()
        
        self.wfile.write('<h1>Interactive ITDK</h1>'.encode())

    def do_POST(self):
        self.send_response(200)


port = HTTPServer(('', 5555), Interactive_ITDK)
  
port.serve_forever()