import logging
from BaseHandler import *

class RRDuinoHandler(BaseHandler):
    """
    Updates an rrdtool database for the connected client.
    Subclasses implement specifics about the rrd database.
    """
    
    def __init__(self, sock, session):
        super(RRDuinoHandler, self).__init__(sock, session)
        
        self.register_message_type('u', self.handle_update, True) # Update message
        
        if not os.path.isfile(profile['rrd']):
            # rrd database does not exist for user... create it.
            self.create(profile)
        
    def create(self, path):
        """
        Implemented to create the rrd database if it does not exist. Path to database should be profile['rrd'].
        """
        pass
        
    def update(self, profile, **kwargs):
        """
        Update the database given **kwargs. Path to database should be profile['rrd'].
        """
        pass

    def graph(self, profile, **kwargs):    
        """
        Save the graph of the rrd database. Path to output image should be profile['graph'].
        """
        pass

    def handle_update(self, data):
        logging.debug('Handling update: {0}'.format(data))

        # Split up the request into its parts
        request = data.split(' ')

        # Split up update request
        sources = request[0::2]
        data = request[1::2]

        if '' in sources:
            raise InvalidRequest("Malformed data source")

        if '' in data:
            raise InvalidRequest("Malformed data")

        # Update the rrd database
        self.update(self.session['profile'], **dict(zip(sources, data)))
        
        # Graph the rrd database
        self.graph(self.session['profile'])