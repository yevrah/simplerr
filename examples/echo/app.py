from simplerr.web import web

import os

os.sys.path.append("/Users/harvey/dev/simplerr.com/")


@web('/app/')
def echo_root(request):
    return "Hello from root"

@web('/app/echo/<msg>')
def echo(request, msg):
    return "Echo from app: {}".format(msg)


@web('/app/echo_json/<msg>')
def echoj(request, msg):
    return {'mesg': msg}


@web('/app/echo_template/<msg>', 'test.html')
def echot(request, msg):
    return {'msg': msg}
