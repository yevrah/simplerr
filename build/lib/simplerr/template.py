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




# Template - why cant we use template??? Fixe when properly modularised
class T(object):
    # TODO: Should this be instance
    # Updates this to add filters, eg filters['escapejs'] = json.dumps
    filters = {}

    def __init__(self, cwd):
        self.cwd = cwd
        self.env = Environment(
            loader=FileSystemLoader(cwd), autoescape=True
        )

        filters = self.env.filters

    def render(self, template, data={}):
       return self.env.get_template(template).render(**data)

