def application(environment, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    page = b"""
<html>
<body>
<h1>From Sub</h1>
<p>This is being served using mod_wsgi</p>
</body>
</html>
"""
    return [page]
