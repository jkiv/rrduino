#!/usr/bin/env python

import os, sys, signal
import socket
import hashlib, hmac
import logging
import getopt
#import rrdtool

import rrduino
from rrduino.BaseServer import BaseServer

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
    print "See rrduino/config.py for server configuration."
    
if __name__ == "__main__":  

    # Get command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hvd",
                                   ["help","verbose","debug"])
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
        #elif o in ('--profile-dir'):
        #    rrduino.config.PROFLIE_DIR = a
        #elif o in ('--rrds'):
        #    rrduino.config.RRD_DIR = a
        else:
            assert False, "Unhandled option: {0}".format(o) 

    # Make sure our directories exist
    if not os.path.exists(rrduino.config.PROFILE_DIR):
        os.makedirs(rrduino.config.PROFILE_DIR)

    # Start the server
    logging.info("RRDuino server running on {0}:{1}".format(rrduino.config.HOST, rrduino.config.PORT))
    server = BaseServer(rrduino.config.HOST,
                        int(rrduino.config.PORT),
                        rrduino.config.DEFAULT_HANDLER)

    server.serve_forever()
