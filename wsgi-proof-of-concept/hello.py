import lib.test

def application(environment, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)

    hello = lib.test.some()
    page = b"""
<html>
<body>
<h1>Hello.py</h1>
<p>This is being served using mod_wsgi</p>
</body>
</html>
"""
    return [page]
