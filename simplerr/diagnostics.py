
class Diagnostics(object):

    def pre_response(self, request):
        print("==========================================")
        print("Request path: {}".format(request.path))
        print("Request host: {}".format(request.host))
        print("Request url: {}".format(request.url))
        print("Request method: {}".format(request.method))
        print("Request URL Params: {}".format(request.args.keys()))
        print("Request Form: {}".format(request.form.keys()))
        print("Request Files: {}".format(request.files.keys()))
        print("Request Headers: {}".format(request.headers.keys()))

    def post_response(self, request, response):
        # Response section
        response = Response('Hello World!')
        response.data += b" Thanks for Visiting!"
        response.headers['Content-Type'] = 'text/plain'
        response.set_cookie('name', 'value')
        print("Response Status: {}".format(response.status))
        print("Response Code: {}".format(response.status_code))
        print("Response Length: {}".format(response.content_length))
        print("")
        print("")



