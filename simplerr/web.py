#!/usr/bin/env python

from werkzeug.serving import run_simple

from os import path
from threading import Thread
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware, wrap_file
from werkzeug.exceptions import HTTPException, NotFound, abort
from werkzeug.debug import DebuggedApplication
from werkzeug.serving import make_ssl_devcert
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from werkzeug.utils import redirect as wz_redirect

from jinja2 import Environment, FileSystemLoader, Template

import functools

from pathlib import Path


from .script import script

from .template import T

from peewee import *
from peewee import ModelSelect

from playhouse.shortcuts import model_to_dict, dict_to_model

import mimetypes


# We need custom json_serial to handle date time - not supported
# by the default json_dumps
#
# See https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable

import json
from datetime import date, datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


#  _   _   _   _  _  _   _ _ _  ___  ___   ___  _  _ _  ___  _  _  _  __
# | \_/ | / \ | || \| | | | | || __|| o ) | o \/ \| | ||_ _|| || \| |/ _|
# | \_/ || o || || \\ | | V V || _| | o \ |   ( o ) U | | | | || \\ ( |_n
# |_| |_||_n_||_||_|\_|  \_n_/ |___||___/ |_|\\\_/|___| |_| |_||_|\_|\__/
#



class web(object):
    """Primary routing decorator and helpers

    The `web()` decorator traps all routes and add them to a list, which is
    passed to werkzeugs `werkzeug.routing.Map()` for find the current method to
    run for the matched route.

    Decorator Format
    ==================

    The `web()` decorator (routes) wraps the `werkzueg.routing.Rule()` format
    `<converter(arguments):name>`. 

    In addition to the `Route()` parameters, `web()` also add's a `template` to
    use in rendering that endpoint.

    Routes are used in the following way:

    ::

        @web('/user/<int:id>', 'user.html')
        def get_user(request, id):
            # The return value will be used
            # as the context for the template
            return {'id':id, 'name':'John Doe'}

    Route Parameters
    ----------------

    Routes in simplerr wrap the `Rule()` class in werkzeug - highlighted below

    ::

        class werkzeug.routing.Rule(
            string,
            defaults=None,          # Not yet implemented
            subdomain=None,         # Not yet implemented
            methods=None,
            build_only=False,       # Not yet implemented
            endpoint=None,          # Assigned to same value as first string param, eg '/index'
            strict_slashes=None,    # Not yet implemented
            redirect_to=None,       # Not yet implemented
            alias=False,            # Not yet implemented
            host=None               # Not yet implemented
            )


    The 'web()' decorator has the following signature.

    ::

        class simplerr.web(
            string,         # Route
            string=None,    # Template to combine `return` value as context
            methods=None
        )


    string
        Route strings are URL paths which optionally use placeholders for
        arguments using the following format <converter(arguments):name>.

    string
        Path to the template to be rendered, the return value is supplied as the
        template context. In addition, the `request` object is also available under
        `request`.

    endpoint
        The endpoint for this rule. This can be anything. A reference to a
        function, a string, a number etc. The preferred way is using a string
        because the endpoint is used for URL generation.

    methods
        A list of http methods to accept, defaults to `None` which accepts all.
        Otherwise sepcify `'GET'`, `'POST'`, `'PUT'`, `'DELETE'`. Note that
        `'HEAD'` is accepeted on `'GET'` requests.


    Footnotes
    =========

    .. [1] Werkzeug Rule() details at http://werkzeug.pocoo.org/docs/0.14/routing/#rule-format

    """

    #TODO: Is this a potential memorry leak?
    destinations = []
    filters = {}
    template_engine = None


    def __init__(self, route="/", template=None, methods=None, endpoint=None, file=False):
        self.route = route
        self.template = template
        self.methods = methods
        self.endpoint = endpoint
        self.fn = None
        self.args = None # to be set when matched() is called
        self.file = file


    def __call__(self, fn):
        # A quick cleanup first, if no endpoint was specified we need to set it
        # to the view function
        self.endpoint = self.endpoint or fn.__name__ # Default endpoint name if none provided.

        # Proceed to create decorator
        self.fn = fn

        # add this function into destinations
        web.destinations.append(self)

        @functools.wraps(fn)
        def decorated(request, *args, **kwargs):
            return fn(request, *args, **kwargs)

        # Return pretty much unmodified, we really only
        # wanted this to index it into destinations
        return decorated

    @staticmethod
    def match(environ):
        map = Map()
        index = {}

        for item in web.destinations:
            # Lets create an index on routes, as urls.match returns a route
            index[item.endpoint] = item

            # Create the rule and add it tot he map
            rule = Rule(item.route, endpoint=item.endpoint, methods=item.methods)
            map.add(rule)

        # Check for match
        urls = map.bind_to_environ(environ)
        endpoint, args = urls.match()

        # Get match and attach current args
        match = index[endpoint]
        match.args = args

        return match

    @staticmethod
    def process(request, environ, cwd):
        match = web.match(environ)
        args = match.args
        out = match.fn(request, **args)
        data = out
        template = match.template
        file = match.file


        # Check to see if this is a peewee model and convert to
        # dict
        if(isinstance(data, Model)):
            out = model_to_dict(out)
            data = out


        if(isinstance(data, ModelSelect)):
            array_out = []
            for item in data:
                array_out.append(model_to_dict(item))
                out = {'results': array_out}
                data = out


        # Template expected, attempt render
        if(template != None):
            # Add request to data
            data = data or {}
            data['request'] = request
            out = web.template(cwd, template, data)
            response = Response(out)
            response.headers['Content-Type'] = 'text/html;charset=utf-8'
            return response


        # Example implementation here
        #   http://bit.ly/2ocHYNZ
        if(file == True):
            file_path = Path(cwd) / Path(out)
            file = open(file_path.absolute().__str__(), 'rb')
            data = wrap_file(environ, file)

            mtype = mimetypes.guess_type(file_path.__str__())[0]

            response = Response(data, direct_passthrough=True)
            response.headers['Content-Type'] = '{};charset=utf-8'.format(mtype)
            return response

        # No template, just plain old string response
        if isinstance(data, str):
            response = Response(data)
            response.headers['Content-Type'] = 'text/html;charset=utf-8'
            return response

        # User has decided to run their own request object, just return this
        if isinstance(data, Response):
            return data

        # Just raw data, send as is
        # TODO: Must be flagged as json explicity
        out = json.dumps(data, default=json_serial)
        response = Response(out)
        response.headers['Content-Type'] = 'application/json'
        return response

    @staticmethod
    def response(data):
        return Response(data)

    @staticmethod
    def filter(name):

        def wrap(fn):
            # Add to filters dict
            web.filters[name] = fn

            def decorated(*args, **kwargs):
                fn(*args, **kwargs)
            return decorated
        return wrap


        @functools.wraps(fn)
        def decorated(request, *args, **kwargs):
            return fn(request, *args, **kwargs)

        # Return pretty much unmodified, we really only
        # wanted this to index it into filters dict
        return decorated

    @staticmethod
    def template(cwd, template, data):
        # This maye have to be removed if CWD proves to be mutable per request
        web.template_engine = web.template_engine or T(cwd)

        # Add any registered filters
        for filter in web.filters.keys():
            web.template_engine.env.filters[filter] = web.filters[filter]

        # Return Rendering
        return web.template_engine.render(template, data)


    @staticmethod
    def redirect(location, code=302, Response=None):
        return wz_redirect(location, code, Response)

    @staticmethod
    def abort(code=404):
        return abort(code)

    @staticmethod
    def all():
        return web.destinations

