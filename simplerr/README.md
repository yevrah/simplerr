"""
TODO
[x] Route to function
[x] Render template
[x] Load module dynamically
[ ] Render static file
[ ] Easy file upload
[ ] Easy access to request and response objects

Setting up on apache: http://werkzeug.pocoo.org/docs/0.14/deployment/mod_wsgi/


@web('/')
def hello(request):
    return "Hello from inside this awesome app!!"

@web('/echo/<out>')
def echo(request, out):
    return out


@web('/echot/<name>', '/templates/hello.html')
def echot(request, name):
    return {'name': name}

@web('/echodouble/<out>')
def some_fn2(request, out):
    print('hellow')

@web('/favicon.ico')
def some_fn3(request):
    return ""

print(web.all())




"""

