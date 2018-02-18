from werkzeug.serving import run_simple

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

import os
import sys


class script(object):

    # Set path to root of project
    # cwd = '/var/www/example.com'
    #
    # Route paths always maps to a physical files, as this is part of the
    # design
    #
    # route = '/'


    def __init__(self, cwd, route):
        self.cwd = Path(cwd)
        self.route = Path( "." + route)

    def get_script(self):
        # Examples
        #  /var/www/example.com/app/login
        #  /var/www/example.com/app/login/
        #  /var/www/example.com/app/login/exit
        #  /var/www/example.com/app/login/exit/1

        # Maximum search path, start the top of the
        # route and continue down. By using route
        # we ensure we don't dig deaper then the 
        # web path (cwd).

        # We also use pathlibs for a more OO view of the filesystem
        max_depth = self.route.parts.__len__()
        for i in range(max_depth,0,-1):
            search = self.route.parts[:i]
            search_path = self.cwd / Path(*search)

            # Is this a script file without the '.py'
            # eg, test for ..mple.com/app/login -> ..mple.com/app/login.py
            script_py_str = ''.join([search_path.__str__(), ".py" ])
            script_py = Path(script_py_str)

            print(">> Checking for script: {}".format(script_py.__str__()))

            if script_py.exists():
                return script_py.absolute().__str__()

            # Is this a folder with index.py
            # eg, test for ..mpl.com/app/login/index.py
            index_py = search_path / 'index.py'

            print(">> Checking for script: {}".format(index_py.__str__()))

            if index_py.exists():
                return index_py.absolute().__str__()


            # Parent folder "/" cant be a py file ("/.py") but can contain an
            # index.py file ("/index.py") so if i==1 then we have to test for
            # this final edge case.
            if i!=1: continue

            root_index_py = search_path.parent / 'index.py'
            print(">> Checking final edge case {}".format(root_index_py.__str__()))
            if root_index_py.exists():
                return root_index_py.absolute().__str__()


    def get_module(self):
        # https://www.blog.pythonlibrary.org/2016/05/27/python-201-an-intro-to-importlib/
        # https://docs.python.org/3/library/importlib.html
        script = self.get_script()

        print(">> getting script >> {}".format(script))


        spec = importlib.util.spec_from_file_location("", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # You can no do this
        #   app = module.application()

        return module



