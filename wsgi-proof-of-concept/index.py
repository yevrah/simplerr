from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server


def application(environment, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)


    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]

    start_response(status, headers)

    ret = [("%s: %s\n" % (key, value)).encode("utf-8")
           for key, value in environ.items()]



    page = """
<html>
<body>
<h1>Hello world!</h1>
<p>This is being served using mod_wsgi</p>
</body>
</html>
"""
    return [ret.encode()]
