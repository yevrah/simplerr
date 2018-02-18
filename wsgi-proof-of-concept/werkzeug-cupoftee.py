#!/usr/bin/env python
"""
    Manage Cup Of Tee
    ~~~~~~~~~~~~~~~~~
    Manage the cup of tee application.
    :copyright: (c) 2009 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
import click
from werkzeug.serving import run_simple

import time
from os import path
from threading import Thread
from werkzeug.templates import Template
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule


class Page(object):
    __metaclass__ = PageMeta
    url_arguments = {}

    def __init__(self, cup, request, url_adapter):
        self.cup = cup
        self.request = request
        self.url_adapter = url_adapter

    def url_for(self, endpoint, **values):
        return self.url_adapter.build(endpoint, values)

    def process(self):
        pass

    def render_template(self, template=None):
        if template is None:
            template = self.__class__.identifier + '.html'
        context = dict(self.__dict__)
        context.update(url_for=self.url_for, self=self)
        body_tmpl = Template.from_file(path.join(templates, template))
        layout_tmpl = Template.from_file(path.join(templates, 'layout.html'))
        context['body'] = body_tmpl.render(context)
        return layout_tmpl.render(context)

    def get_response(self):
        return Response(self.render_template(), mimetype='text/html')


class file(object):

class MyApp(object):

    def __init__(self):
        self.db = database


    def dispatch_request(self, request):
        url_adapter = url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = url_adapter.match()
            page = pages[endpoint](self, request, url_adapter)
            response = page.process(**values)
        except NotFound, e:
            page = MissingPage(self, request, url_adapter)
            response = page.process()
        except HTTPException, e:
            return e
        return response or page.get_response()

    def __call__(self, environ, start_response):
        request = Request(environ)
        return self.dispatch_request(request)(environ, start_response)




def init_app(database, interval=60):
    return SharedDataMiddleware(
        MyApp(database), {
        '/shared':  path.join(path.dirname(__file__), 'shared')
    })

def make_app():
    from cupoftee import make_app
    return init_app('/tmp/cupoftee.db')


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
    app = make_app()

    run_simple(hostname, port, app,
               use_reloader=reloader, use_debugger=debugger,
               use_evalex=evalex, threaded=threaded, processes=processes)


if __name__ == '__main__':
