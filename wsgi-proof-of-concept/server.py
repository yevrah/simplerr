# Server examples: https://wiki.python.org/moin/WebServers
#
# See http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/ for a quick
# server setup
#
#     https://docs.python.org/3.6/library/wsgiref.html
from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
import os
# https://docs.python.org/3/library/importlib.html
# Static files: http://pwp.stevecassidy.net/wsgi/static.html
import importlib

web_files = []
# Utility functions


def get_python_files():
    print("Getting files")
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.py'):
                print(root, dirs, file)
                web_files.append(file)


# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def proxy_app(environ, start_response):
    setup_testing_defaults(environ)

    # status = '200 OK'
    # headers = [('Content-type', 'text/plain; charset=utf-8')]

    # start_response(status, headers)

    # ret = [("%s: %s\n" % (key, value)).encode("utf-8")
    #        for key, value in environ.items()]

    page_module = importlib.import_module('app')
    return page_module.application(environ, start_response)


def serve():
    with make_server('', 8000, proxy_app) as httpd:
        get_python_files()

        print("Serving on port 8000...")
        httpd.serve_forever()


if __name__ == "__main__":
    serve()
