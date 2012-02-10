#import rrdtool
from RRDuinoHandler import *

class ExampleRRDHandler(RRDuinoHandler):
    def create(self, profile):
        # If the database does not exist, use this function to create it.
        print self.__class__, "create"
        print profile['rrd']

    def update(self, profile, **kwargs):
        # We should use kwargs to update the rrd database
        print self.__class__, "update"
        print profile['rrd'], kwargs
