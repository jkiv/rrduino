import os
import socket
import logging
import hashlib, hmac

import profile

class InvalidRequest(Exception):
    pass

class BaseHandler:
    """
    Base class of all handlers.
    This class implements the 'hello' handler as well as providing the foundation for general message verification.
    Subclasses can register their own handling functions in __init__ using register_message_type.
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

    # Number of times to hash key material
    key_gen_rounds = 128
    
    def __init__(self, sock, session, **options):
        self.session = session
        self.socket = sock
        self.rfile_up()
        self.handlers = {}
        self.message_uses_hmac = [] 
        
        # Register standard messages
        self.register_message_type('h', self.handle_hello, False)

    @classmethod
    def validate_options(cls, opts):
      ''' Validates optional **kwargs passed to handler. 
          Should be implemented by derived classes.
          If a derived class wants to pass validations to its base class
          then it should use super() or similar.
      '''
      pass

    def register_message_type(self, message_type, handler_function, requires_hmac = False):
        """
        Registers a handler function for messages beginning with
        'message_type'. Handler functions should accept a single
        parameter (e.g 'data') which is the received message with the
        'message_type' and HMAC removed. If the message type requires
        authentication, the parameter 'requires_hmac' should be set to True.
        """
        
        # Register the handler
        self.handlers.update({message_type: handler_function})
        
        # Make sure we check HMAC for those messages that require it
        if requires_hmac:
          self.message_uses_hmac.append(message_type)
    
    def readline(self):
        return self.rfile.readline()

    def rfile_up(self):
        self.rfile = self.socket.makefile('rb', self.rbufsize)

    #def wfile_up(self):
    #    self.wfile = self.socket.makefile('wb', self.wbufsize)

    #def wfile_down(self):
    #    if not self.wfile.closed:
    #        self.wfile.flush()
    #    self.wfile.close()

    def handle_hello(self, data):
        """
        Handles the 'hello' message.
        """
        logging.debug('Handling hello: {0}'.format(data))

        # Read client ID
        client_id = data.strip()

        if len(client_id) == 0:
            logging.debug("Empty client ID")
            raise InvalidRequest("Empty client ID")

        self.session['id'] = client_id

        # Load client profile
        self.session['profile'] = profile.load_for(client_id)
        self.session['profile']['key'] = hashlib.sha256(self.session['profile']['key']).digest()

        # Generate key material and key
        key_material = os.urandom(32)

        # Send key material for the session
        self.socket.send(key_material)
 
        logging.debug("key_material={0}".format([key_material]))
        logging.debug("master_key={0}".format([self.session['profile']['key']]))

        # Generate session key
        for i in range(self.key_gen_rounds):
	  key_material = hmac.new(self.session['profile']['key'], key_material, hashlib.sha256).digest()

        self.session['key'] = key_material # (sorry cryptographers)

        logging.debug("session_key={0}".format([self.session['key']]))

    def verify_hmac(self, message):
        """
        Verifies a message's HMAC. Throws an InvalidRequest on a bad HMAC.
        """
        # Split up update request
        parts = message.split(' ')

        their_hmac = parts[-1]
        canonical_string = ' '.join(x for x in parts[:-1])

        if len(their_hmac) != 64:
            raise InvalidRequest("Malformed HMAC")

        # Check HMAC
        our_hmac = hmac.new(self.session['key'], canonical_string, hashlib.sha256).hexdigest()
        
        if our_hmac != their_hmac:
            logging.debug("Could not verify HMAC:\n  ours:   {0}\n  theirs: {1}".format(our_hmac, their_hmac))
            raise InvalidRequest("Bad HMAC")
        
    def advance_session_key(self):
        self.session['key'] = hmac.new(self.session['profile']['key'], self.session['key'], hashlib.sha256).digest()
    
    def handle(self):
        """
        Determines the message content and delivers the message to the
        appropriate (registered) handler function for further processing.
        If the message type requires HMAC authentication, then the message
        is automagically verified. If the message is not authenticated,
        an error will be raised. See verify_hmac() for details.
        """
        # Get message
        message = self.readline().rstrip()

        logging.debug("({0}) '{1}'".format(len(message), message))

        if not message:
            raise socket.error("Client disconnected")

        # Split message into the type and the data(/body)
        message_type, data = message.split(' ', 1)
         
        # Authenticate message if required
        if message_type in self.message_uses_hmac:
            logging.debug("session_key={0}".format([self.session['key']]))
            # Verify HMAC
            self.verify_hmac(message)
            
            # Advance key
            self.advance_session_key()
            
            # Remove hmac from data
            data = data.rsplit(' ', 1)[0]

        logging.debug(self.session)
        logging.debug("Received message: {0} {1}".format(message_type, data))

        # Handle message type
        self.handlers[message_type](data)
