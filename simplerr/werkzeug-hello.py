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
class dispatcher(object):

    def __init__(self):
        print('Initialising class..')
        self.version = "0.1.0"


    def dispatch_request(self, request, environ):
        # For url /home/app/12 - check for
        #   /home/app/12.py
        #   /home/app/index.py

        #   /home/app.py
        #   /home/index.py .. and so on
        # import app
        # out = app.process(request)
        #
        # Will also need to set endpoint prefix for routes when root path found
        #   eg..  EndpointPrefix('blog/',....
        #
        print("==========================================")
        print("Request path: {}".format(request.path))
        print("Request host: {}".format(request.host))
        print("Request url: {}".format(request.url))
        print("Request method: {}".format(request.method))
        print("Request URL Params: {}".format(request.args.keys()))
        print("Request Form: {}".format(request.form.keys()))
        print("Request Files: {}".format(request.files.keys()))
        print("Request Headers: {}".format(request.headers.keys()))


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

        response = web.process(request, environ, '/Users/harvey/tmp/wsgi-test')


        ## Response section

        # response = Response('Hello World!')
        response.data += b" Thanks for Visiting!"
        response.headers['Content-Type'] = 'text/plain'
        response.set_cookie('name', 'value')
        print("Response Status: {}".format(response.status))
        print("Response Code: {}".format(response.status_code))
        print("Response Length: {}".format(response.content_length))
        print("")
        print("")

        return response  # return web.process(route).

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request, environ)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)




def make_wsgi_app():
    app = DebuggedApplication(dispatcher(), evalex=True)
    return SharedDataMiddleware(
        app, {
        '/shared':  path.join(path.dirname(__file__), 'shared')
    })






@click.group()
def cli():
    pass


@cli.command()
@click.option('-h', '--hostname', type=str, default='localhost', help="localhost")
@click.option('-p', '--port', type=int, default=5000, help="5000")
@click.option('--reloader', is_flag=True, default=False)
@click.option('--debugger', is_flag=True)
@click.option('--evalex', is_flag=True, default=False)
@click.option('--threaded', is_flag=True)
@click.option('--processes', type=int, default=1, help="1")
def runserver(hostname, port, reloader, debugger, evalex, threaded, processes):
    """Start a new development server."""
    app = make_wsgi_app()

    (crt, key) = make_ssl_devcert('/tmp/', host='localhost')

    run_simple(hostname, port, app,
               use_reloader=reloader, use_debugger=debugger,
               use_evalex=evalex, threaded=threaded, processes=processes) # , ssl_context=(crt, key))


if __name__ == '__main__':
    cli()

"""
Setting up on apache: http://werkzeug.pocoo.org/docs/0.14/deployment/mod_wsgi/


@web('/')
def hello(request):
    return "Hello from inside this awesome app!!"

@web('/echo/<out>')
def echo(request, out):
    return out


@web('/echot/<name>', '/templates/hello.html')
def echot(request, name):
    return {'name': name}

@web('/echodouble/<out>')
def some_fn2(request, out):
    print('hellow')

@web('/favicon.ico')
def some_fn3(request):
    return ""

print(web.all())




"""
