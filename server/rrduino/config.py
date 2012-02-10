"""
rrduino Server Configuration
"""

# If you make a custom handler, place it in the rrduino/
# folder and include it here
from ExampleRRDHandler import *

# You can write your own handler;
# import it correctly and change
# the class name here
HANDLER = ExampleRRDHandler

# No need to change unless you've
# extended the use of the profile.
DEFAULT_PROFILE = {'key':   None,
                   'rrd':   None}

# Host name to bind on:
#   0.0.0.0    - allow all connections
#   localhost  - only allow connections from same machine
HOST = '0.0.0.0'

# Port to listen on
PORT = 60405

# Directory that contains the user profiles
PROFILE_DIR  = '/path/to/profiles'
