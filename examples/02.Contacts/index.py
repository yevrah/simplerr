from simplerr.web import web
from model import Person


@web('/')
def home(request):
    return Person.select()

@web('/first', template="first.html")
def home(request):
    return Person.select().get()

@web('/echo/<msg>')
def echo(request, msg):
    return "Echo: {}".format(msg)
