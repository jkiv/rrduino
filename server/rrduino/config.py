"""
rrduino Server Configuration
"""

from RRDuinoHandler import *

# Default handler unless specified in profile (TODO)
DEFAULT_HANDLER = RRDuinoHandler

# Host name to bind on:
#   0.0.0.0    - allow all connections
#   localhost  - only allow connections from same machine
HOST = '0.0.0.0'

# Port to listen on
PORT = 60405

# Directory that contains the user profiles
PROFILE_DIR  = '/path/to/rrduino/profiles/'
