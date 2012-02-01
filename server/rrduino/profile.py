import os
import cPickle as pickle
import hashlib
import logging

from . import config

def filename_of(s):
    return hashlib.sha256(s).hexdigest()

def validate(profile):
    # Key
    if not profile['key']:
        raise ValueError("A pre-shared key is required.")

    # rrd path
    if not profile['rrd']:
        raise ValueError("A path to an rrd database is required.")

def create(filename, **kwargs):
    profile_path = os.path.join(config.PROFILE_DIR, filename_of(filename))
    kwargs['key'] = hashlib.sha256(kwargs['key']).digest()
    logging.info("Creating profile for {0}: {1}".format(filename, profile_path))
    with open(profile_path, 'w') as f:
        pickle.dump(kwargs, f)

def load(filename):
    profile = config.DEFAULT_PROFILE.copy() 
    profile_path = os.path.join(config.PROFILE_DIR, filename_of(filename))

    with open(profile_path, 'r') as f:
        profile.update(pickle.load(f))

    return profile
