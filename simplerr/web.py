#!/usr/bin/env python

from werkzeug.serving import run_simple

from os import path
from threading import Thread
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.debug import DebuggedApplication

from werkzeug.serving import make_ssl_devcert

from werkzeug.routing import Map, Rule, NotFound, RequestRedirect

from jinja2 import Environment, FileSystemLoader, Template

import functools

from pathlib import Path


from .script import script

import json
from .template import T

#  _   _   _   _  _  _   _ _ _  ___  ___   ___  _  _ _  ___  _  _  _  __
# | \_/ | / \ | || \| | | | | || __|| o ) | o \/ \| | ||_ _|| || \| |/ _|
# | \_/ || o || || \\ | | V V || _| | o \ |   ( o ) U | | | | || \\ ( |_n
# |_| |_||_n_||_||_|\_|  \_n_/ |___||___/ |_|\\\_/|___| |_| |_||_|\_|\__/
#

class web(object):
    # Is this a potential memorry leak?
    destinations = []
    template_engine = None


    def __init__(self, route="/", template=None, methods=["GET"], endpoint=None):
        self.route = route
        self.template = template
        self.methods = methods
        self.endpoint = endpoint or route
        self.fn = None
        self.args = None # to be set when matched() is called

        print('>> Adding Route >> {}, {}', self.route, self.template)

    def __call__(self, fn):
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
            rule = Rule(item.route, endpoint=item.endpoint)
            map.add(rule)
            print(">> Searching destination {}".format(item.route))

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

        # Template expected, attempt render
        if(template != None):
            out = web.template(cwd, template, data)
            return Response(out)

        # No template, just plain old string response
        if isinstance(data, str):
            return Response(data)

        # User has decided to run their own request object, just return this
        if isinstance(data, Response):
            return data

        # Just raw data, send as is
        # TODO: Must be flagged as json explicity
        out = json.dumps(data)
        response = Response(out)
        response.headers['Content-Type'] = 'application/json'
        return response

    @staticmethod
    def template(cwd, template, data):
        # This maye have to be removed if CWD proves to be mutable per request
        web.template_engine = web.template_engine or T(cwd)
        return web.template_engine.render(template, data)

    @staticmethod
    def all():
        return web.destinations

