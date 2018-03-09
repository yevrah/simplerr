from simplerr import web

@web('/login.js', file=True)
def js(request):
    return ['static/js/angular.js'


