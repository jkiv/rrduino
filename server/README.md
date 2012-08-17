rrduino server
==============

This is an example _rrduino_ server written in Python.

`server.py` - runs the server.

`rrduino/` - contains `config.py` for configuring the server and contains much of the _rrduino_ server code.

Configuration
-------------

`rrduino/config.py` contains the configuration file for the _rrduino_ server. 

`PROFILE_DIR` - the directory which will contain the user profiles. It is strongly recommended that this be set to a valid directory, writable by the server.

`PORT` - the port to listen on. Feel free to change this to your liking. Make sure your _Arduino_ client is correctly configured if this is changed from the default.

`HOST` - the host to bind to. `0.0.0.0` should suffice for general use. However, it is __highly recommended__ that the server be running behind a NAT router or generally not exposed to the wider Internet.

Creating Profiles
-----------------

A profile stores information about a client. This information includes the client's pre-shared key and information about its _rrdtool_ database. A single server can handle many clients which may collect and record various types of data.

Before proceeding, make sure `rrduino/config.py` contains the path to the directory which will store all the profiles (`PROFILE_DIR`).

Each client has its own profile file. The filenames are derived from the client's ID.

Profiles are JSON-formatted objects. Here is an example profile (or see `example.json`):

    {
      "key": "secret123",
      "handler_options": {
        "path": "/path/to/example.rrd",
        "create": ["--step", "60",
                   "DS:temperature:GAUGE:120:-50:110",
                   "RRA:AVERAGE:0.5:5:288",
                   "RRA:AVERAGE:0.5:60:720",
                   "RRA:AVERAGE:0.5:240:1096"],
        "update": "N:{temperature}"
      }
    }

The root object contains two values:

`key` - the client's pre-shared key.
`handler_options` - options for managing an _rrdtool_ database

By default, `handler_options` expects three values:

`path` - the full file path to the _rrdtool_ database.
`create` - a list of options used to instantiate the _rrdtool_ database. (Technically speaking, these strings correspond to `rrdtool.create` options.)
`update` - a string used to update the _rrdtool_ database. In the above example, we are expecting the client to send a value with the key `temperature` in its `update` commands (as shown by the use of `{temperature}`).

Custom Handlers
---------------

`RRDuinoHandler` is a handler with _rrduino_-specific functionality. It provides a way for handling `update` commands and manipulating an _rrdtool_ database in your own way.

For general purpose applications, `BaseHandler` contains all that is necessary for performing the handshake (`hello` command), registering arbitrary message types, and automagically checking the HMAC of each message if desired.

The values specified in a profile's `handler_options` are passed to a handler object upon creation via `**options`. This allows profiles to work along-side any `BaseHandler`-derived object seemlessly.

For validating options, `BaseHandler` will call the class method `validate_options` when instantiating any `BaseHandler`-derived class. If deriving from another handler class such as `RRDuinoHandler`, it may be necessary to call `validate_options` on the base class manually during validations.

See `rrduino/RRDuinoHandler.py` for an example of how `BaseHandler` can be extended to accomodate other message types.
