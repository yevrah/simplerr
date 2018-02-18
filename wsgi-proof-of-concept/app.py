# from werkzeug.wrappers import Response

# def application(environment, start_response):
#     status = '200 OK'
#     response_headers = [('Content-type', 'text/html')]
#     start_response(status, response_headers)
#
#     page = b"""
# <html>
# <body>
# <h1>App.py</h1>
# <p>This is being served using mod_wsgi</p>
# </body>
# </html>
# """
#     return [page]

# // https://www.sitepoint.com/python-web-applications-the-basics-of-wsgi/
class application_base(object):
    
    def __init__(self, environ, start_fn):
        self.environ = environ
        self.start_fn = start_fn

    def __iter__(self):
        self.start_fn('200 OK', [('Content-Type', 'text/plain')])
        ret = [("%s: %s\n" % (key, value)).encode("utf-8")
               for key, value in self.environ.items()]
        # yield b"Hello Worlds!\n"
        yield ret.pop


class application(application_base):
    pass
