import socket, select
import os, sys, signal
import hashlib, hmac
import logging

import profile
from RRDuinoHandler import * 

class RRDuinoServer:
    def __init__(self, host, port, HandlerClass = RRDuinoHandler):
        # Create, bind, listen socket
        self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.listening_socket.bind( (host, port) )
        self.listening_socket.listen(5)

        self.open_sockets = []
        self.HandlerClass = HandlerClass
        self.sessions = {}
        self.running = False

    def serve_forever(self):
        self.running = True
        while self.running:
            self._select()

        for s in self.open_sockets:
            _cleanup_socket(s)


    def stop(self):
        self.running = False

    def _cleanup_socket(self, s):
        # Remove connection
        logging.debug("Cleaning up socket {0}".format(s))
        s.shutdown(socket.SHUT_RDWR)
        self.open_sockets.remove(s)
        del self.sessions[s.fileno()]

    def _select(self):
        rlist, wlist, xlist = select.select( [self.listening_socket] + self.open_sockets, [], [])

        logging.debug("# of sessions:     {0}".format(len(self.sessions)))
        logging.debug("# of open sockets: {0}".format(len(self.open_sockets)))

        # Handle ready sockets:
        # .. ready to read
        for s in rlist:
        
            if s is self.listening_socket:
                # Accept new connection
                new_socket, addr = self.listening_socket.accept()
                self.open_sockets.append(new_socket)

                # Initialize empty session for user
                self.sessions[new_socket.fileno()] = {'id'      : None,
                                                      'key'     : None,
                                                      'profile' : None}
            else:
                # Get connection's session data
                session = self.sessions[s.fileno()]

                # Handle the request
                try:
                    handler = self.HandlerClass(s, session)
                    handler.handle()
                except Exception as e:
                    # Something went wrong... disconnect the client!
                    logging.error(e)
                    self._cleanup_socket(s)
		    #raise


