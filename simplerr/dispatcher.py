#!/usr/bin/env python

import click
from werkzeug.serving import run_simple

import time
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
import importlib.util

from .web import web
from .script import script

import sys

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class SiteNoteFoundError(Error):
    """Exception raised for errors in the site path

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, site, message):
        self.site = message
        self.message = message


#
#  _   _   _   _  _  _   _ _ _ __  __  _
# | \_/ | / \ | || \| | | | | / _|/ _|| |
# | \_/ || o || || \\ | | V V \_ ( |_n| |
# |_| |_||_n_||_||_|\_|  \_n_/|__/\__/|_|
#
#  ___  ___  _   _   _  ___  _ _ _  _  ___ _  _
# | __|| o \/ \ | \_/ || __|| | | |/ \| o \ |//
# | _| |   / o || \_/ || _| | V V ( o )   /  (
# |_|  |_|\\_n_||_| |_||___| \_n_/ \_/|_|\\_|\\
#
#

class WebRequest(Request):
    """Adds support for JSON and other niceties"""

    @property
    def json(self):
        # TODO: need to cache this otherwise each call runs json.loads
        try:
            data=self.data
            out=json.loads(data, encoding=charset)
        except ValueError as e:
            out=None
        return out


class dispatcher(object):

    def __init__(self, cwd):
        self.cwd = cwd


    def dispatch_request(self, request, environ):
        # print("==========================================")
        # print("Request path: {}".format(request.path))
        # print("Request host: {}".format(request.host))
        # print("Request url: {}".format(request.url))
        # print("Request method: {}".format(request.method))
        # print("Request URL Params: {}".format(request.args.keys()))
        # print("Request Form: {}".format(request.form.keys()))
        # print("Request Files: {}".format(request.files.keys()))
        # print("Request Headers: {}".format(request.headers.keys()))


        # Routes management
        # url_map = Map([
        #     Rule('/', endpoint='/'),
        #     Rule('/index', endpoint='index'),
        #     Rule('/echo/<echo>', endpoint='def-echo'),
        #     Rule('/favicon.ico', endpoint='favicon')
        # ])
        #
        # urls = url_map.bind_to_environ(environ)
        # endpoint, args = urls.match()

        sc = script(self.cwd, request.path)
        module = sc.get_module()

        response = web.process(request, environ, self.cwd)


        ## Response section

        # response = Response('Hello World!')
        # response.data += b" Thanks for Visiting!"
        # response.headers['Content-Type'] = 'text/plain'
        # response.set_cookie('name', 'value')
        # print("Response Status: {}".format(response.status))
        # print("Response Code: {}".format(response.status_code))
        # print("Response Length: {}".format(response.content_length))
        # print("")
        # print("")

        return response  # return web.process(route).

    def wsgi_app(self, environ, start_response):
        request = WebRequest(environ)
        response = self.dispatch_request(request, environ)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


### WSGI Processesor
class wsgi(object):

    def __init__(self, site, hostname, port, use_reloader=True,
                  use_debugger=False, use_evalex=False, threaded=True,
                  processes=1):

        self.site = site
        self.hostname = hostname
        self.port = port
        self.use_reloader = use_reloader
        self.use_debugger = use_debugger
        self.use_evalex = use_evalex
        self.threaded = threaded
        self.processes = processes

        self.app = None

        self.cwd = self.make_cwd()

        # Add CWD to search path, this is where project modules will be located
        sys.path.append( self.cwd.absolute().__str__() )

    def make_cwd(self):
        path_site = Path(self.site)
        path_with_cwd = Path.cwd() / path_site

        if path_site.exists():
            return path_site

        if path_with_cwd.exists():
            return path_with_cwd

        raise SiteNoteFoundError(
            self.site,
            "Could not access folder"
        )

    def make_app(self):
        self.app = dispatcher(self.cwd.absolute().__str__())
        return self.app

    def make_app_debug(self):
        self.app = DebuggedApplication(
            dispatcher(self.cwd.absolute().__str__()),
            evalex=True
        )

        return self.app

    def serve(self):
        """Start a new development server."""

        self.make_app_debug()

        """Generate SSL Keys, not currently used, needs some improvements"""
        # (crt, key) = make_ssl_devcert('/tmp/', host='localhost')

        run_simple(self.hostname,
                   self.port,
                   self.app,
                   use_reloader=self.use_reloader,
                   use_debugger=self.use_debugger,
                   use_evalex=self.use_evalex,
                   threaded=self.threaded,
                   processes=self.processes) # , ssl_context=(crt, key))


### Main form - nothing happens at the moment
if __name__ == '__main__':
    pass

