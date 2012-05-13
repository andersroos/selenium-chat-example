#!/usr/bin/env python

import os
import re
import sys
import time
import socket  
import threading
import SocketServer
import base64
import struct
import hashlib

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
Sec-WebSocket-Accept: %s\r\n\
\r\n\
"

WebSocketGUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

filedir = os.path.dirname(os.path.abspath(__file__)) + '/static'
        
class HttpHandler(SocketServer.BaseRequestHandler):

    chat_clients = list()
    chat_clients_lock = threading.Lock()

    def get_message(self):
        message = ""
        while True:
            
            # add chunks to data while connected
            
            chunk = self.request.recv(1024)
            if not chunk: return None
            self.data += chunk
            
            # wait for full header
            
            if len(self.data) < 2: continue

            (b1, b2) = struct.unpack("!BB", self.data[:2])
            finflag = b1 & 0x01
            opcode = (b1 & 0xf0) >> 4
            maskflag = (b2 & 0xff) >> 7
            payloadlen = b2 & 0x7f

            if maskflag != 1: return

            headlen = 6
            if len(self.data) < headlen: continue
            
            if payloadlen == 126:
                headlen = 8
                if len(self.data) < headlen: continue
                payloadlen, = struct.unpack("!H", self.data[2:4])
            elif payloadlen == 127:
                headlen = 14
                if len(self.data) < headlen: continue
                payloadlen, = struct.unpack("!Q", self.data[2:10])
                
            if len(self.data) < headlen + payloadlen: continue
            
            mask = map(ord, self.data[(headlen - 4):headlen])
            self.data = self.data[headlen:]

            part = map(ord, self.data[:payloadlen])
            self.data = self.data[payloadlen:]
            
            for i in range(len(part)):
                part[i] = chr(part[i] ^ mask[i % 4])

            message += ''.join(part)

            if finflag: break
            
        return message

    @staticmethod
    def send_message(client, message):
        length = len(message)
        header = []
        header.append(chr(0x81))
        if length < 126:
            header.append(chr(length))
        elif length < 2**16:
            header.append(chr(126))
            header.append(struct.pack("!H", length))
        else:
            header.append(chr(127))
            header.append(struct.pack("!Q", length))
        data = "".join(header) + message

        client.send(data)
    
    def handle(self):
        
        # wait for end of HTTP header
        
        self.data = ""
        while '\r\n\r\n' not in self.data:
            self.data += self.request.recv(1024)

        # get path from header
            
        header, self.data = self.data.split('\r\n\r\n', 1)

        m = re.match('GET ([^ ]*) HTTP/1.1', header)
        if not m:
            self.request.send(http_404)
            return

        path = m.group(1)

        # handle files
        
        if path != '/chat':
            if not os.path.exists(filedir + path):
                self.request.send(http_404 + filedir + path)
                return
            self.request.send(http_200_html + open(filedir + path, 'r').read())
            return

        # handle chat
        
        headers = dict([h.split(': ') for h in re.split('\r\n', header)[1:] if ': ' in h])
        
        key = hashlib.sha1()
        key.update(headers['Sec-WebSocket-Key'].strip() + WebSocketGUID)
        accept = base64.b64encode(key.digest())
        self.request.send(http_101_websocket % accept)

        with self.chat_clients_lock:
            my_id = len(self.chat_clients)
            self.chat_clients.append(self.request)

        print "client %d connected" % my_id

        print "  sending hello to client %d" % my_id
        self.send_message(self.request, "Welcome to the chat!!")
        
        while True:
            message = self.get_message()
            if None == message: break

            print "client %d got message '%s'" % (my_id, message)

            with self.chat_clients_lock:
                for i in range(len(self.chat_clients)):
                    if i != my_id and None != self.chat_clients[i]:
                        print "  sending '%s' to client %d" % (message, i)
                        self.send_message(self.chat_clients[i], message)

        with self.chat_clients_lock:
            self.chat_clients[my_id] = None
            
        print "client %d disconnected" % my_id
            
        
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
