#!/usr/bin/env python

import os, sys, signal
import socket
import hashlib, hmac
import logging
import getopt
#import rrdtool

import rrduino
from rrduino.RRDuinoServer import RRDuinoServer

def usage():
    print "rrduino server" 
    print "Usage:"
    print "   Running the server:"
    print "       {0} [-v|--verbose|-d|--debug]".format(sys.argv[0])
    print ""
    print "  -v, --verbose   Verbose output"
    print "  -d, --debug     Very verbose output (DEBUG ONLY)"
    print "  -h, --help      Show this message."
    print ""
    print "  Creating a profile:"
    print "      {0} -c profile_name -k|--key profile_key".format(sys.argv[0])
    print ""
    print "  -c, --create    Specifies the name of the profile to create."
    print "                    --key is required"
    print "                    --rrd is optional"
    print "                  The server will not run."
    print "  -k, --key       The key for the new profile"
    print ""
    print "See rrduino/config.py for server configuration."
    
if __name__ == "__main__":  
    # Defaults
    # .. logging
    logging.basicConfig(level=logging.ERROR)

    # .. new profile
    new_profile = {'id'     : None,
                   'profile': rrduino.config.DEFAULT_PROFILE.copy()}
                   
    # Get command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "h:c:k:r:vd",
                                   ["help","create","key","rrd","verbose","debug"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    # Manage command line options
    for o, a in opts:
        if o in ('-v', '--verbose'):
            logging.basicConfig(level=logging.INFO)
        elif o in ('-d', '--debug'):
            logging.basicConfig(level=logging.NOTSET)
        elif o in ('-h', '--help'):
            usage()
            sys.exit()

        # Server settings
        #elif o in ('-h', '--host'):
        #    rrduino.config.HOST = a
        #elif o in ('-p', '--port'):
        #    rrduino.config.PORT = a
        #elif o in ('--profiles'):
        #    rrduino.config.PROFLIE_DIR = a
        #elif o in ('--rrds'):
        #    rrduino.config.RRD_DIR = a

        # Creating profile
        elif o in ('-c', '--create'):
            new_profile['id'] = a
        elif o in ('-k', '--key'):
            new_profile['profile']['key'] = a
        elif o in ('-r', '--rrd'):
            new_profile['profile']['rrd'] = a
        else:
            assert False, "Unhandled option: {0}".format(o) 

    if new_profile['id']:
        # Make sure we specify a key
        while not new_profile['profile']['key']:
            new_profile['profile']['key'] = raw_input("Enter pre-shared key: ")

        # Validate our new profile
        rrduino.profile.validate(new_profile['profile'])        

        # Create the new profile
        rrduino.profile.create(new_profile['id'], **(new_profile['profile']))
    else:
        # Make sure our directories exist
        if not os.path.exists(rrduino.config.PROFILE_DIR):
            os.makedirs(rrduino.config.PROFILE_DIR)

        # Start the server
        logging.info("RRDuino server running on {0}:{1}".format(rrduino.config.HOST, rrduino.config.PORT))
        server = RRDuinoServer(rrduino.config.HOST,
                               int(rrduino.config.PORT),
                               rrduino.config.HANDLER)
        server.serve_forever()
