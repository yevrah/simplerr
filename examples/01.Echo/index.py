from simplerr.web import web


@web('/')
def plain(request):
    return """Hello from Echo index.py, click for a <a href="/TOC">TOC</a>"""


@web('/TOC', '/assets/toc.html')
def template(request):
    import simplerr
    return {"version": simplerr.__version__}


@web('/echo/<msg>')
def echo(request, msg):
    return "Echo from index: {}".format(msg)


@web('/echo/args')
def echo_args(request):
    return "Echo using args: {}".format(request.args['msg'])


@web('/echo/form')
def echo_form(request):
    msg = "[not submitted yet]"

    if "msg" in request.form.keys():
        msg = request.form["msg"]

    return """
    <html>
    <body>
     <form method=post action="">
      Message: <input type="text" name="msg" placeholder="Enter msg value"/>
      <input type="submit">
      You typed in: "{}"
     </form>
    </body>
    </html>
    """.format(msg)



