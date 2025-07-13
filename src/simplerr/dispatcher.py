import logging
from functools import lru_cache
from typing import Optional, Any

from werkzeug.serving import run_simple
from werkzeug.wrappers import Request
from werkzeug.exceptions import NotFound, HTTPException, InternalServerError
from werkzeug.debug import DebuggedApplication
from pathlib import Path
from .web import web
import sys
import json

from .script import script
from .session import FileSystemSessionStore

logger = logging.getLogger(__name__)

class SiteError(Exception):
    """Base class for exceptions in this module."""

    pass


class SiteNoteFoundError(SiteError):
    """Exception raised for errors in the site path

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, site, message):
        self.site = site
        self.message = message
        super().__init__(message)


class WebEvents(object):
    """Web Request object, extends Request object.  """

    def __init__(self):
        self.pre_request = []
        self.post_request = []

    # Pre-request subscription
    def on_pre_response(self, fn):
        self.pre_request.append(fn)

    def off_pre_response(self, fn):
        self.pre_request.remove(fn)

    def fire_pre_response(self, request):
        for fn in self.pre_request:
            try:
                fn(request)
            except Exception as e:
                logger.error(f"Error in pre-response event: {e}")
                raise

    # Post-Request subscription management
    def on_post_response(self, fn):
        self.post_request.append(fn)

    def off_post_response(self, fn):
        self.post_request.remove(fn)

    def fire_post_response(self, request, response, exc):
        for fn in self.post_request:
            try:
                fn(request, response, exc)
            except Exception as e:
                logger.error(f"Error in post-response event: {e}")
                raise


class WebRequest(Request):
    """Web Request object, extends Request object.  """

    def __init__(self, *args, auth_class=None, **kwargs):
        super(WebRequest, self).__init__(*args, **kwargs)
        self.view_events = WebEvents()
        self._cached_json: Optional[Any] = None

    @property
    @lru_cache(maxsize=1)
    def json(self):
        """Adds support for JSON and other niceties"""
        if not hasattr(self, '_cached_json'):
            try:
                self._cached_json = json.loads(self.data.decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                logger.error(f"Error decoding JSON: {self.data}")
                self._cached_json = None
        return self._cached_json


class dispatcher(object):
    def __init__(self, cwd, global_events, extension=".py"):
        self.cwd = cwd
        self.global_events = global_events
        self.extension = extension


    def __call__(self, environ, start_response):
        """This methods provides the basic call signature required by WSGI"""
        request = WebRequest(environ)
        response, exc = self.dispatch_request(request, environ)

        try:
            return response(environ, start_response)
        finally:
            # Fire post response events
            request.view_events.fire_post_response(request, response, exc)
            self.global_events.fire_post_response(request, response, exc)


    def dispatch_request(self, request, environ):
        response = None
        exc = None

        # Various errors can occur in processing a request, we need to protect
        # the post event responses from these so they can fire and cleanup
        # events.
        #
        # Note that any errors not caught will be re-thrown, but finally will
        # always run to clean up resources.
        try:
            # RestorePresets
            web.restore_presets()

            # Get view script and view module
            sc = script(self.cwd, request.path, extension=self.extension)
            sc.get_module()

            # Process Response, and get payload
            response = web.process(request, environ, self.cwd, request_hooks=[
                self.global_events.fire_pre_response,
                request.view_events.fire_pre_response,
            ])
        except HTTPException as e:
            exc = e
            response = e
            logger.error(f"HTTPException: {e}")
        except FileNotFoundError as e:
            exc = NotFound(str(e))
            response = exc
            logger.error(f"OSError: {e}")
        except Exception as e:
            exc = InternalServerError(str(e))
            response = exc
            logger.error(f"Exception: {e}")

        # There should be no more user code after this being run
        return response, exc  # return web.process(route).


# WSGI Server
class wsgi(object):
    def __init__(
        self,
        site,
        hostname,
        port,
        use_reloader=True,
        use_debugger=False,
        use_evalex=False,
        threaded=True,
        processes=1,
        use_profiler=False,
        extension=".py"
    ):

        self.site = site
        self.hostname = hostname
        self.port = port
        self.use_reloader = use_reloader
        self.use_debugger = use_debugger
        self.use_evalex = use_evalex
        self.threaded = threaded
        self.processes = processes
        self.extension = extension

        self.app = None

        # TODO: Need to update interface to handle these
        self.session_store = FileSystemSessionStore()

        self.cwd = self._resolve_cwd()

        # Add Relevent Web Events
        # NOTE: Events created at this level should fire static events that
        # are fired on every request and will share application data, all other
        # events should be reset between views. Make sure to not use the global
        # object unless you want the event called at every view.
        self.global_events = WebEvents()

        self._setup_events()

        # Add CWD to search path, this is where project modules will be located
        self._setup_path()

    def _resolve_cwd(self) -> Path:
        path_site = Path(self.site)
        path_with_cwd = Path.cwd() / path_site

        if path_site.exists():
            return path_site

        if path_with_cwd.exists():
            return path_with_cwd

        raise SiteNoteFoundError(self.site, "Could not access folder")

    def _setup_events(self):
        # Add some key events
        self.global_events.on_pre_response(self.session_store.pre_response)
        self.global_events.on_post_response(self.session_store.post_response)

    def _setup_path(self):
        sys.path.append(self.cwd.absolute().__str__())


    def make_app(self, debug: bool = False):
        self.app = dispatcher(self.cwd, self.global_events, self.extension)
        if debug:
            return DebuggedApplication(self.app, evalex=self.use_evalex,)
        return self.app

    def serve(self):
        """Start a new development server."""
        self.make_app(debug=True)

        run_simple(
            self.hostname,
            self.port,
            self.app,
            use_reloader=self.use_reloader,
            use_debugger=self.use_debugger,
            threaded=self.threaded,
            processes=self.processes,
        )
