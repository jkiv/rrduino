import socket, select
import os, sys, signal
import hashlib, hmac
import logging

import profile
from BaseHandler import * 

class BaseServer:
    def __init__(self, host, port, HandlerClass = BaseHandler):
        # Create, bind, listen socket
        self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.listening_socket.bind( (host, port) )
        self.listening_socket.listen(5)

        self.running = False              # Whether the server is running or not
        
        self.open_sockets = []            # All open sockets (to select() on)
        
        self.HandlerClass = HandlerClass  # An instance of this class is created
                                          # to handle a server message
                                          # TODO: client-specific handler classes

        self.sessions = {}                # Persistent data storage for each connection
                                          # (which we refer to as a "session")

        # Default session state
        self.default_session = {'id'      : None,
                                'key'     : None,
                                'profile' : None}

    def serve_forever(self):
        self.running = True

        # Main server loop
        while self.running:
            self._select()

        for s in self.open_sockets:
            _cleanup_socket(s)

    def stop(self):
    	# Should cause server loop to exit
        self.running = False

    def _cleanup_socket(self, s):
        logging.debug("Cleaning up socket {0}".format(s))

        # Shutdown connection (in a TCP sense)
        s.shutdown(socket.SHUT_RDWR)

        # Remove forget socket and session information
        self.open_sockets.remove(s)
        del self.sessions[s.fileno()]

    def _select(self):
    	# select() on all known sockets (for reading)
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
                self.sessions[new_socket.fileno()] = self.default_session.copy()

            else:
                # Get connection's session data
                session = self.sessions[s.fileno()]

                # Handle the request
                try:
                    # We use self.HandlerClass to handle the ready socket.
                    # In practise, a subclass of BaseHandler is written for
                    # the user's particular needs.
                    # TODO: HandlerClass is specified on a connection-by-
                    #       connection basis allowing different devices to
                    #       send different types of messages.
                    handler = self.HandlerClass(s, session)
                    handler.handle()

                except Exception as e:
                    # Something went wrong. Let's disconnect the client as
                    # a result.
                    logging.error(e)
                    self._cleanup_socket(s)
		    #raise
