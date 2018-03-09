from werkzeug.contrib.sessions import SessionStore, SessionMiddleware


class NoSQLSessionStore(SessionStore):
    """Todo: Implement TinyDB dict session store"""
    pass

class DbSessionStore(SessionStore):
    """Todo: Implement Db session store"""
    pass

class MemorySessionStore(SessionStore):
    """TODO: Flesh out, sourced from
    https://github.com/pallets/werkzeug/blob/master/examples/contrib/sessions.py

    Review Flask Secure Sessions
    https://github.com/pallets/flask/blob/master/flask/sessions.py

    How to Use
    ----------

    def application(environ, start_response):
        session = environ['werkzeug.session']
        session['visit_count'] = session.get('visit_count', 0) + 1

        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['''
            <!doctype html>
            <title>Session Example</title>
            <h1>Session Example</h1>
            <p>You visited this page %d times.</p>
        ''' % session['visit_count']]


    def make_app():
        return SessionMiddleware(application, MemorySessionStore())
    """

    COOKIE_NAME = 'sessionfast'

    def __init__(self, session_class=None):
        SessionStore.__init__(self, session_class=None)
        self.sessions = {}

    def save(self, session):
        self.sessions[session.sid] = session

    def delete(self, session):
        self.sessions.pop(session.id, None)

    def get(self, sid):
        if not self.is_valid_key(sid) or sid not in self.sessions:
            print("    > SESSION -> new session, not valid key")
            return self.new()

        print("    > SESSION --> existing session")
        return self.session_class(self.sessions[sid], sid, False)


    """
    From: http://werkzeug.pocoo.org/docs/0.14/contrib/sessions/

    For better flexibility it’s recommended to not use the middleware but the store
    and session object directly in the application dispatching:

    ::

        session_store = FilesystemSessionStore()

        def application(environ, start_response):
            request = Request(environ)
            sid = request.cookies.get('cookie_name')
            if sid is None:
                request.session = session_store.new()
            else:
                request.session = session_store.get(sid)
            response = get_the_response_object(request)
            if request.session.should_save:
                session_store.save(request.session)
                response.set_cookie('cookie_name', request.session.sid)
            return response(environ, start_response)


    The following provides a helper method for pre request and post request
    process.
    """

    def pre_response(self, request):
        sid = request.cookies.get(MemorySessionStore.COOKIE_NAME)
        print("    > Pre response session fired, cookie sid is: {}".format(sid))
        if sid is None:
            request.session = self.new()
            print("    > Generated new sid: {}".format(request.session.sid))
        else:
            request.session = self.get(sid)
            print("    > Using existing sid: {}".format(request.session.sid))

    def post_response(self, request, response):
        print("    > Post response session fired, saving sid: {}", request.session.sid)

        if request.session.should_save:
            self.save(request.session)
            response.set_cookie(MemorySessionStore.COOKIE_NAME,
                                request.session.sid)


