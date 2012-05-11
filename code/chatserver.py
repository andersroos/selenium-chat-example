#!/usr/bin/env python

import os
import re
import sys
import time
import socket  
import threading
import SocketServer

http_400 = "\
HTTP/1.1 400 Bad Request\r\n\
\r\n\
ERROR"

http_404 = "\
HTTP/1.1 404 Not Found\r\n\
\r\n\
Could not find file: "

http_200_html = "\
HTTP/1.1 200 OK\r\n\
Content-Type: text/html\r\n\
\r\n\
"
http_101_websocket = "\
HTTP/1.1 101 Switching Protocols\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n\
\r\n\
"

filedir = os.path.dirname(os.path.abspath(__file__)) + '/static'

class HttpHandler(SocketServer.BaseRequestHandler):

    chat_clients = list()
    char_clients_lock = threading.Lock()

    def handle(self):
        
        # Wait for end of HTTP header.
        
        data = ""
        while '\r\n\r\n' not in data:
            data += self.request.recv(1024)

        # Get path from header
            
        header, data = data.split('\r\n\r\n', 1)

        m = re.match('GET ([^ ]*) HTTP/1.1', header)
        if not m:
            self.request.send(http_404)
            return

        path = m.group(1)

        # Handle files.
        
        if path != '/chat':
            if not os.path.exists(filedir + path):
                self.request.send(http_404 + filedir + path)
                return
            self.request.send(http_200_html + open(filedir + path, 'r').read())
            return

        # Handle chat.
        
        self.request.send(http_101_websocket)
        while True:
            self.request.recv(1024)
        
                
class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    server = Server(('127.0.0.1', 8080), HttpHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    try:
        while True:
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        pass
