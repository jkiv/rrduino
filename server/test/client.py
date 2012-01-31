import socket
import os, sys
import hmac, hashlib
import cPickle as pickle
import logging

logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 3:
   print "Usage: {0} host port".format(sys.argv[0])
   sys.exit(2)

HOST, PORT = sys.argv[1], int(sys.argv[2])

client_id = 'test' 
profile = {'key' : 'test'}

def send_hello(sock, client_id):
    """
    Send a 'hello' message
    """
    sock.send("h {0}\n".format(client_id))

    # Server should provide 32 bytes of key material
    key_material = sock.recv(32)

    logging.debug("key_material={0}".format([key_material]))

    return key_material

def send_update(sock, session_key, **kwargs):
    """
    Send an 'update' message
    """
    data = "u " + ' '.join(str(k) + ' ' + str(v) for k,v in kwargs.iteritems())
    our_hmac = hmac.new(session_key, data, hashlib.sha256).hexdigest()
    logging.debug("Sending '{0} {1}\\n'".format(data, our_hmac))
    sock.send("{0} {1}\n".format(data, our_hmac))

def rollover_key(key):
    """
    Move session key forward
    """
    return hmac.new(key, key, hashlib.sha256).digest()

def generate_session_key(master_key, key_material):
    """
    Turn key material into the session key
    """
    for i in range(4096):
        key_material = hmac.new(master_key, key_material, hashlib.sha256).digest()

    logging.debug("session_key={0}".format([key_material]))

    return key_material # (sorry cryptographers)

if __name__ == "__main__":

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
    
        # Send 'hello', get key material
        key_material = send_hello(sock, client_id)
    
        # Generate session key
        session_key = generate_session_key(profile['key'], key_material) 
        raw_input('Press any key to continue...')
    
        # Send an update message
        data = {'temperature': 10.0}
        send_update(sock, session_key, **data)
        session_key = rollover_key(session_key)
        raw_input('Press any key to continue...')
    
        # Send an update message
        data = {'temperature': 20.0}
        send_update(sock, session_key, **data)
        session_key = rollover_key(session_key)
        raw_input('Press any key to continue...')
    
        # Send an update message
        data = {'temperature': 30.0}
        send_update(sock, session_key, **data)
        session_key = rollover_key(session_key)
        raw_input('Press any key to continue...')
    
    finally:
        sock.close()
