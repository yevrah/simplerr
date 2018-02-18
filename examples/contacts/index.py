from simplerr.web import web

import sys


sys.path.append("/Users/harvey/dev/simplerr.com/examples/contacts/")

from model import Person

@web('/')
def home(request):
    return Person.select()


@web('/echo/<msg>')
def echo(request, msg):
    return "Echo: {}".format(msg)
