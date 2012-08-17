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
        self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        self.DEFAULT_SESSION = {'id'      : None,
                                'key'     : None, # session key
                                'handler' : None,
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
        try:
          s.shutdown(socket.SHUT_RDWR)
        except:
          pass # FIXME

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
                self.sessions[new_socket.fileno()] = self.DEFAULT_SESSION.copy()

            else:
                # Get connection's session data
                session = self.sessions[s.fileno()]

                # Handle the request
                try:
                    # If the session doesn't have a profile use a temporary BaseHandler.
                    # If the session has a profile, use the existing handler or create it.
                    if session['profile']:
                      if session['handler']:
                        handler = session['handler']
                      else:
                        handler = self.HandlerClass(s, session, **session['profile']['handler_options'])
                    else:
		      handler = BaseHandler(s, session)
                    
                    # Handle the client
                    handler.handle()

                except Exception as e:
                    # Something went wrong. Let's disconnect the client as
                    # a result.
                    logging.error(e)
                    self._cleanup_socket(s)
          	    #raise
