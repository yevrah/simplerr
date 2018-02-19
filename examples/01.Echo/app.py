from simplerr.web import web

import os

os.sys.path.append("/Users/harvey/dev/simplerr.com/")


@web('/app/')
def echo_root(request):
    return "Hello from root"


@web('/app/echo/<msg>')
def echo_plain_text(request, msg):
    return "Echo from app: {}".format(msg)


@web('/app/echo_json/<msg>')
def echo_json(request, msg):
    return {'msg': msg}


@web('/app/echo_template/<msg>', 'test.html')
def echo_template(request, msg):
    return {'msg': msg}


@web('/app/echo_args')
def echo_args(request):
    return "Echo using args: {}".format(request.args['msg'])


@web('/app/echo_form')
def echo_form(request):
    msg = "NOTHING"

    if "msg" in request.form.keys():
        msg = request.form["msg"]

    return """
    <html>
    <body>
     <form method=post action="">
      Mesage: <input type=text name="msg" value="" placeholder="Enter msg value"/><input type="submit">
      You typed in: "{}"
     </form>
    </body>
    </html>
    """.format(msg)


