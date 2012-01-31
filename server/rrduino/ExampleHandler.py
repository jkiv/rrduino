#import rrdtool
from RRDuinoHandler import *

class ExampleHandler(RRDuinoHandler):
    def update(self, rrd_path, **kwargs):
        """
        We should use kwargs to update the rrd database
        """
        print self.__class__
        print rrd_path, kwargs

    def create(self, rrd_path):
        """
        If the database does not exist, use this function to create it.
        """
        print self.__class__
        print rrd_path
