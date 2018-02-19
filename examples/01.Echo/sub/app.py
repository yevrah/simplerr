from simplerr.web import web


@web('/sub/app/echo/<msg>')
def echo(request, msg):
    return "Echo from sub-app: {}".format(msg)



