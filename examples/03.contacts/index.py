from simplerr.web import web
from model import Person

@web('/example.txt')
def response_test(request):
    response= web.response('Here is a bespoke response')
    response.headers['Content-Type'] = 'application/octet-stream'

    return response


@web('/')
def home(request):
    return Person.select() # {'model': [Persons]}

@web('/first', template="first.html")
def home(request):
    return Person.select().get() 

@web('/echo/<msg>')
def echo(request, msg):
    return "Echo: {}".format(msg)
