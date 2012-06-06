rrduino server
==============

This is an example rrduino server written in Python.

`server.py` - creates profiles or runs the server.

`rrduino/` - contains `config.py` for configuring the server; contains much of the rrduino server code; and is the destination of custom handlers.

Configuration
-------------

`rrduino/config.py` contains the configuration file for the rrduino server. 

`PROFILE_DIR` - the directory which will contain the user profiles. It is strongly recommended that this be set to a valid directory, writable to by the server.

`HANDLER` - the class name for the handler that the server will use. Change this to reflect the name of your own handler. Make sure to import the handler you wish to use. (Right now there is one handler type for all clients. This is subject to change as development continues.)

`PORT` - the port to listen on. Feel free to change this to your liking.

`HOST` - the host to bind to. `0.0.0.0` should suffice for general use, however, it is assumed that the server is running behind a NAT router or other type of firewall.

`DEFAULT_PROFILE` - the default profile state. This should only be changed by developers who have added or removed features of the profile.

Creating Profiles
-----------------

A profile stores information about a client. This information includes the client's pre-shared key and a path to an rrdtool database. A single server can handle many clients of the same type.

Before proceeding, make sure `rrduino/config.py` contains the path to the directory which will store the profiles.

For example, to create a profile for `fridge`

`server.py -c fridge -r /path/to/fridge.rrd`

You can also specify the key using the -k option, but if it is omitted then you will be prompted for a key.

The above will create a profile for the client `fridge` which will use the rrdtool database `/path/to/fridge.rrd`.

Writing a Handler
-----------------

In order to create or update an rrd database properly, a handler needs to be written.

Handlers which update rrdtool databases are classes which derive from `RRDuinoHandler`. Handlers should implement the following two methods:

`create(self, profile, **kwargs)` - called before updating if the rrd database does not exist.

`update(self, profile, **kwargs)` - called when an update message is received from the client. Key-value pairs sent by the client are available in `kwargs`. The path to the rrd database is available by `profile['rrd']`.

Handlers are placed in `rrduino/` and set for use in `rrduino/config.py`.

`rrduino/ExampleRRDHandler.py` shows which functions a handler should implement. `rrduino/CarboyHandler.py` contains an example implementation of a handler.

(Right now there is one handler type for all clients. This is subject to change as development continues.)

Very Custom Handlers
--------------------

`RRDuinoHandler` is a handler with rrduino-specific functionality. It provides a way for handling 'update' commands and an interface for extending the handling capabilities (i.e. manipulating an rrd database in your own way).

For general purpose applications, `BaseHandler` contains all that is necessary for performing the handshake ('hello' command), registering arbitrary message types, and automagically checking the HMAC of each message (if desired).

See `rrduino/RRDuinoHandler.py` for an example of how `BaseHandler` can be extended to accomodate other message types.
