import rrdtool
from RRDuinoHandler import *

class CarboyHandler(RRDuinoHandler):
    def create(self, profile):
        # Create our database
        rrdtool.create(profile['rrd'],
                       '--step', '60',
                       'DS:temperature:GAUGE:-50:100:U',
                       'RRA:AVERAGE:0.5:60:720') # At 1 minute/step, this is hourly avg. for one month

    def update(self, profile, **kwargs):
        # We're expecting to update the temperature
        rrdtool.update(profile['rrd'], 'N:{temperature}'.format(kwargs))
    
    def graph(self, profile, **kwargs):
        # Plot the temperature
        rrdtool.graph(profile['graph'],
                      '--vertical-label', 'Temperature (C)',
                      'DEF:T={0}:temperature:AVERAGE'.format(profile['rrd']),
                      'LINE2:T#FF0000')