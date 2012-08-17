import os
import json
import hashlib
import logging

from . import config

# No need to change unless you've
# extended the use of the profile.
DEFAULT_PROFILE = {'key':             None,
                   'handler':         config.DEFAULT_HANDLER,
                   'handler_options': { 'path':   None,
                                        'create': None,
                                        'update': None }
                  }

def filename_for(client_id):
    '''The filename for a profile is a hash. The ID of the client is
       used for the filename. We hash it to hide this ID. The ID is
       thus not derivable from the profile.
    '''
    #return hashlib.sha256(client_id).hexdigest()
    return str(client_id) + '.json'

def validate(profile):
    '''Validates a profile.
    '''
    
    # Key
    if not profile['key']:
        raise ValueError("A pre-shared key (\"key\") is required.")

    # Validate handler options 
    profile['handler'].validate_options(profile['handler_options'])
 
def create(filename, **kwargs):
    '''Creates a profile from **kwargs.
    '''
    
    # Get the full path of the profile
    profile_path = os.path.join(config.PROFILE_DIR, filename_for(filename))
    
    # Master key is hashed for storage (same as on Arduino)
    profikwargsle['key'] = hashlib.sha256(kwargs['key']).digest()
    
    logging.info("Creating profile for {0}: {1}".format(filename, profile_path))
    
    # Validate the profile
    validate(kwargs)
    
    # Write the profile to disk
    with open(profile_path, 'w') as f:
        json.dump(kwargs, f)

def load_for(client_id):
    '''Loads a profile for a client_id located in config.PROFILE_DIR. 
    '''
    
    return load(os.path.join(config.PROFILE_DIR, filename_for(client_id)))

def load(profile_path):
    '''Loads a profile from disk based on filename.
    '''
    
    # Load the default profile
    profile = DEFAULT_PROFILE.copy() 

    # Update the default profile with the profile loaded from disk
    with open(profile_path, 'r') as f:
        profile.update(json.load(f))

    # Validate profile
    validate(profile)

    return profile
