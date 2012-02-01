import os
import socket
import logging
import hashlib, hmac

import profile
import config

class InvalidRequest(Exception):
    pass

class RRDuinoHandler:
    """
    Updates an rrdtool database for the connected client.
    """

    # "Default buffer sizes for rfile, wfile.
    # We default rfile to buffered because otherwise it could be
    # really slow for large data (a getc() call per byte); we make
    # wfile unbuffered because (a) often after a write() we want to
    # read and we need to flush the line; (b) big writes to unbuffered
    # files are typically optimized by stdio even when big reads
    # aren't."
    #
    # -- Source: http://svn.python.org/projects/python/trunk/Lib/SocketServer.py
    rbufsize = -1
    wbufsize = 0

    def __init__(self, sock, session):
        self.session = session
        self.socket = sock
        self._rfile_up()

        # Handler functions
        self.handlers = {'h': self.handle_hello,
                         'u': self.handle_update}
    
    def readline(self):
        return self.rfile.readline()

    def _rfile_up(self):
        self.rfile = self.socket.makefile('rb', self.rbufsize)

    #def _wfile_up(self):
    #    self.wfile = self.socket.makefile('wb', self.wbufsize)

    #def _wfile_down(self):
    #    if not self.wfile.closed:
    #        self.wfile.flush()
    #    self.wfile.close()

    def update(self, path, **kwargs):
        """
        Update the database given **kwargs
        """
        pass

    def create(self, path):
        """
        Implemented to create the rrd database if it does not exist.
        """
        pass

    def handle_hello(self, data):
        logging.debug('Handling hello: {0}'.format(data))

        # Read client ID
        client_id = data.strip()

        if len(client_id) == 0:
            logging.debug("Empty client ID")
            raise InvalidRequest("Empty client ID")

        self.session['id'] = client_id

        # Load client profile
        self.session['profile'] = profile.load(client_id)

        # Generate key material and key
        key_material = os.urandom(32)

        # Send key material for the session
        self.socket.send(key_material)

        # Generate session key
        for i in range(128):
            key_material = hmac.new(self.session['profile']['key'], key_material, hashlib.sha256).digest()

        self.session['key'] = key_material # (sorry cryptographers)

    def handle_update(self, data):
        logging.debug('Handling update: {0}'.format(data))

        # Split up the request into its parts
        request = data.split(' ')

        if (len(request) % 2) == 0:
            raise InvalidRequest("Malformed update request")

        # Split up update request
        sources = request[0:-1:2]
        data = request[1:-1:2]
        their_hmac = request[-1]

        if '' in sources:
            raise InvalidRequest("Malformed data source")

        if '' in data:
            raise InvalidRequest("Malformed data")

        if len(their_hmac) != 64:
            raise InvalidRequest("Malformed HMAC")

        # Check HMAC
        canonical_string = 'u ' + ' '.join(request[:-1])
        logging.debug("canonical_string={0}".format([canonical_string]))
        our_hmac = hmac.new(self.session['key'], canonical_string, hashlib.sha256).hexdigest()

        if our_hmac != their_hmac:
            raise InvalidRequest("Could not verify HMAC:\n  ours:   {0}\n  theirs: {1}".format(our_hmac, their_hmac))

        # Advance key
        self.session['key'] = hmac.new(self.session['key'], self.session['key'], hashlib.sha256).digest()

        # Update rrd database
        self.update(self.session['profile']['rrd'], **dict(zip(sources, data)))

    def handle(self):
        # Get message
        message = self.readline()

        logging.debug("({0}) '{1}'".format(len(message), message))

        if not message:
            raise socket.error("Client disconnected")

        message_type, data = message.rstrip().split(' ', 1)

        logging.debug(self.session)
        logging.debug("Received message: {0} {1}".format(message_type, data))

        # Handle message type
        self.handlers[message_type](data)
