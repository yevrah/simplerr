from simplerr.web import web

@web('/')
def echo(request):
    return "Hello from index"

@web('/echo/<msg>')
def echo(request, msg):
    return "Echo: {}".format(msg)



