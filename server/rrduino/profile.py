import os
import cPickle as pickle
import hashlib
import logging

from . import config

# TODO Use JSON for profiles (so users can edit the profiles)

def filename_of(s):
    '''The filename for a profile is a hash. The ID of the client is
       used for the filename. We hash it to hide this ID. The ID is
       thus not derivable from the profile.
    '''
    return hashlib.sha256(s).hexdigest()

def validate(profile):
    '''Validates a profile.
    '''
    
    # Key
    if not profile['key']:
        raise ValueError("A pre-shared key is required.")

    # rrdtool database path
    if not profile['rrd']:
        raise ValueError("A path to an rrd database is required.")
        
def create(filename, **kwargs):
    '''Creates a profile from **kwargs.
    '''
    
    # Get the full path of the profile
    profile_path = os.path.join(config.PROFILE_DIR, filename_of(filename))
    
    # Master key is hashed for storage (same as on Arduino)
    profikwargsle['key'] = hashlib.sha256(kwargs['key']).digest()
    
    logging.info("Creating profile for {0}: {1}".format(filename, profile_path))
    
    # Validate the profile
    validate(kwargs)
    
    # Write the profile to disk
    with open(profile_path, 'w') as f:
        pickle.dump(kwargs, f)

def load(filename):
    '''Loads a profile from disk.
    '''
    
    # Load the default profile
    profile = config.DEFAULT_PROFILE.copy() 
    
    # Get the full path of the profile
    profile_path = os.path.join(config.PROFILE_DIR, filename_of(filename))

    # Update the default profile with the profile loaded from disk
    with open(profile_path, 'r') as f:
        profile.update(pickle.load(f))

    return profile
