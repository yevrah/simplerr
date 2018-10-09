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
from datetime import date, datetime, time

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()


    if(isinstance(obj, Model)):
        return model_to_dict(obj)


    if(isinstance(obj, ModelSelect)):
        array_out = []
        for item in obj:
            array_out.append(model_to_dict(item))

        return array_out


    return str(obj)


    # raise TypeError ("Type %s not serializable" % type(obj))




# TODO - Finish this up

class BaseAccess(): pass
class private(BaseAccess): pass
class public(BaseAccess): pass
class disbled(BaseAccess): pass

import inspect

class Auth(object):
    """



    Basic auth management, inspired by https://flask-login.readthedocs.io/en/latest/_modules/flask_login/login_manager.html#LoginManager.user_loader
    
    How to use

    # index.py

    # Mark whole index as private - alternatices include public, and disabled
    # NOTE: This is highly experimental, there are various problems with this - like tracking this setting if multiple files are imported
    web.secure_routes('*', private) #this attaches a VIEW_DEFAULT_SECURITY = private to the current view
    web.secure_routes('/admin/*', private) #this attaches a VIEW_DEFAULT_SECURITY = private to the current view


    @web.auth(private) # Run my own checks
    def check_private_auth(user):
        pass

    class admins(BaseAccess): pass

    @web.auth(admin):
    def check_admin(user):

    
    # With the exception
    @web('/public', any=[private, public]) # Any can be true
        return "Hello to ALL!"

    # With the exception
    @web('/public', only=[private, admins]) # All must be true
        return "Hello to ALL!"


    @web.unauthorised()
    def login():
        # handle not authorised


    Available methods

    auth.login(userid, user)
    auth.logout(userid)
    auth.user() # Get current user
    """

    def __init__(self, storage):
        self.authenticated = False
        self.active = False
        self.anonymous = False
        self.redirect = '/'
        pass

    def check(self):
        pass




#  _   _   _   _  _  _   _ _ _  ___  ___   ___  _  _ _  ___  _  _  _  __
# | \_/ | / \ | || \| | | | | || __|| o ) | o \/ \| | ||_ _|| || \| |/ _|
# | \_/ || o || || \\ | | V V || _| | o \ |   ( o ) U | | | | || \\ ( |_n
# |_| |_||_n_||_||_|\_|  \_n_/ |___||___/ |_|\\\_/|___| |_| |_||_|\_|\__/
#

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ToManyArgumentsError(Error):
    """Exception raised for errors in the web() signature"""

    def __init__(self, message):
        self.message = message

class BaseMethod(object): verb=None
class POST(BaseMethod): verb="POST"
class GET(BaseMethod): verb="GET"
class DELETE(BaseMethod): verb="DELETE"
class PUT(BaseMethod): verb="PUT"
class PATCH(BaseMethod): verb="PATCH"


class CORS(object):

    """Add basic CORS header support when provided

    More information
    ----------------
    See issue at https://github.com/pallets/werkzeug/issues/131

    Example usage
    -------------

    # Using default values
    @web('/api/login', cors=CORS())
    def login(request):
        return {'success':True}

    # Using custom configuration
    cors=CORS()
    cors.origin="localhost"
    cors.methods=[POST]

    # Will append header to defaults, if you want to reset use `cors.headers=[]`
    cors.headers.append('text/plain') 

    # Using default values
    @web('/api/login', cors=cors)
    def login(request):
        return {'success':True}


    """

    def __init__(self):
        """TODO: to be defined1. """

        self.origin="*"
        self.methods=[POST, GET, DELETE, PUT, PATCH]
        self.headers=['Content-Type', 'Authorization']

    def set(self, response):
        response.headers.add('Access-Control-Allow-Origin', '*')

        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,PATCH')

        response.headers.add('Access-Control-Allow-Headers',

                             # Expects string in following format
                             # 'Content-Type, Authorization'
                             ",".join(self.headers)
                             )


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

    def __init__(self, *args, route=None, template=None, methods=None, endpoint=None, file=False, cors=None, mimetype=None):

        self.endpoint = endpoint
        self.fn = None
        self.args = None # to be set when matched() is called
        self.file = file
        self.cors = cors
        self.mimetype = mimetype

        # Key-word Grammer - note, if route or template exists from 
        # key word arguments, they will not be overriden by *args values
        self.route = route
        self.template = template
        self.methods = methods

        # However, we also allow a basic grammer with optional arguments web([route],[template], [methods])
        # Note, 1) First item may be a route or template, 2) second item may be a template

        args_strings = [item for item in args if isinstance(item, str)]

        # We have to check not string first as issubclass failes on testing str items
        args_methods = [item for item in args if not(isinstance(item, str)) and issubclass(item, BaseMethod)]


        # Add the methods
        if len(args_methods) > 0:
            self.methods = self.methods or []
            for method in args_methods:
                self.methods.append(method.verb)


        # Only one string, maybe route or template
        if len(args_strings) == 1:

            if(self.route is None):
                self.route = args_strings[0]
            elif(self.template is None):
                self.template = args_strings[0]
            else:
                raise ToManyArgumentsError("Got too many string arguments when route and template already set using named parameters")

        if len(args_strings) == 2:

            if(self.route is None and self.template is None):
                self.route, self.template = args_strings
            else:
                raise ToManyArgumentsError("Got too many string arguments when route or template set using named parameters")

        if len(args_strings) > 2:
                raise ToManyArgumentsError("Got too many string, expected only 2 got {}".format(len(args_strings)))







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

        # Weg web() object that matches this request
        match = web.match(environ)

        # Lets extract some key response information
        args = match.args
        out = match.fn(request, **args)
        data = out
        template = match.template
        file = match.file
        mimetype = match.mimetype
        cors = match.cors


        # TODO: Check auth here

        # TODO: Can we replace the Model, and ModelSelct with json.dumps(data,
        # json_serial) which has been udpated to handle these types?



        # User has decided to run their own request object, just return this
        if isinstance(data, Response):
            return data


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
            if cors: cors.set(response)
            return response


        # Example implementation here
        #   http://bit.ly/2ocHYNZ
        if(file == True):
            file_path = Path(cwd) / Path(out)
            file = open(file_path.absolute().__str__(), 'rb')
            data = wrap_file(environ, file)

            mtype = mimetype or mimetypes.guess_type(file_path.__str__())[0]

            # Sometimes files are named without extensions in the local storage, so
            # instead try and infer from the route
            if mtype is None:
                urifile = environ.get('PATH_INFO').split('/')[-1:][0]
                mtype = mimetypes.guess_type(urifile)[0]


            response = Response(data, direct_passthrough=True)
            response.headers['Content-Type'] = '{};charset=utf-8'.format(mtype)

            if cors: cors.set(response)
            return response

        # No template, just plain old string response
        if isinstance(data, str):
            response = Response(data)
            response.headers['Content-Type'] = 'text/html;charset=utf-8'
            if cors: cors.set(response)
            return response


        # Just raw data, send as is
        # TODO: Must be flagged as json explicity
        out = json.dumps(data, default=json_serial)
        response = Response(out)
        response.headers['Content-Type'] = 'application/json'
        if cors: cors.set(response)
        return response

    @staticmethod
    def response(data, *args, **kwargs):
        # TODO: This should build a web() compliant response object
        # that handles cors, additional headers, etc
        response=Response(data, *args, **kwargs)
        # if cors: cors.set(response)


        return response


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

