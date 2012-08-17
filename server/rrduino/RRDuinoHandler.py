import logging
import rrdtool

from BaseHandler import *

class RRDuinoHandler(BaseHandler):
    '''Updates an rrdtool database for the connected client.
    '''
    
    def __init__(self, sock, session, **options):
        BaseHandler.__init__(self, sock, session, **options)
        
        # Register 'u' (update) message type
        self.register_message_type('u', self.handle_update, True)

        # Unpack options
        self.rrd_path         = str(options['path'])
        self.update_format    = str(options['update'])
        self.create_arguments = [str(x) for x in options['create']]
        
    @classmethod
    def validate_options(cls, opts):
        # Validations for handler options

        if not opts['path']:
            raise ValueError("\"handler_options\": an rrdtool database path (\"path\") is required.")

        if not opts['create']:
            raise ValueError("\"handler_options\": rrdtool database creation arguments (\"create\") are required.")

        if not opts['update']:
            raise ValueError("\"handler_options\": rrdtool database update statement (\"update\") is required.")

    def create(self):
        '''Creates rrdtool database based on
           profile['handler_options']['create'] (i.e. self.create_arguments).
        '''
        rrdtool.create(self.rrd_path, *self.create_arguments)
        
    def update(self, **data):
        '''Update the database given **data. Format of update
           command is specified in profile['handler_options']['update']
           (i.e. self.update_format).
        '''
        rrdtool.update(self.rrd_path, self.update_format.format(**data))

    def handle_update(self, data):
        '''Handles an 'update' command.
        '''
        
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

        # Create profile if it doesn't exist
        if not os.path.isfile(self.rrd_path):
            self.create()

        # Update the rrd database
        self.update(**dict(zip(sources, data)))
