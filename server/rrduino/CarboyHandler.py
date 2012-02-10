import rrdtool
from RRDuinoHandler import *

class CarboyHandler(RRDuinoHandler):
    def create(self, profile):
        # Create our database
        rrdtool.create(profile['rrd'],
                       '--step', '60',
                       'DS:temperature:GAUGE:120:-50:110',
                       'RRA:AVERAGE:0.5:5:288',    # 5 minute avg. for one day
                       'RRA:AVERAGE:0.5:60:720',   # hourly avg. for one month
                       'RRA:AVERAGE:0.5:240:1096') # 4-hour average, for 6 months

    def update(self, profile, **kwargs):
        # We're expecting to update the temperature
        rrdtool.update(profile['rrd'], 'N:{temperature}'.format(**kwargs))
