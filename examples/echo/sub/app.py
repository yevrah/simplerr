from ...simplerr.web import web


@web('/echo/<msg>')
def echo(request, msg):
    return "Echo from sub-app: {}".format(msg)



