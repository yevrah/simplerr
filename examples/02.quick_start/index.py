from simplerr.web import web

@web('/')
def echo(request):
    return "Hello from quick_start application"
