from simplerr.web import web
from pathlib import Path

@web('/')
def echo(request):
    return "Hello from index"


@web('/echo/<msg>')
def echo(request, msg):
    return "Echo from index: {}".format(msg)


@web('/static/<path:file>', file=True)
def echo(request, file):
    return "./shared/" + file





