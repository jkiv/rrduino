import os
import logging
import inspect
import json
import hashlib

from . import config
from BaseHandler import BaseHandler

# No need to change unless you've
# extended the use of the profile.
DEFAULT_PROFILE = {'key':             None,
                   'handler':         config.DEFAULT_HANDLER,
                   'handler_options': { 'path':   None,
                                        'create': None,
                                        'update': None }
                  }

def filename_for(client_id):
    '''Returns the profile filename for a given client_id
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

    # Convert handler class name from string to a class
    if isinstance(profile['handler'], basestring):
        profile['handler'] = import_handler_class(profile['handler'])

    # Validate profile
    validate(profile)

    return profile


def import_handler_class(class_name):
    '''Tries to import rrduino.class_name and returns the handler
       class of the same name. So, this assumes that class_name.py
       exists in the rrduino module and class_name.py contains a
       class of the name class_name.
    '''
    module = __import__('rrduino.{0}'.format(class_name), fromlist = [class_name])
    klass = getattr(module, class_name)

    # Raise an error if this isn't what we expect
    if not inspect.isclass(klass) or not issubclass(klass, BaseHandler):
        raise TypeError('{0} is not a {1}-derived class.'.format(class_name, BaseHandler.__name__))

    return klass
