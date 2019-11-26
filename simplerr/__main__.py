#!/usr/bin/env python
import click
import os, sys
from simplerr import dispatcher, __version__ as sversion


@click.group()
def cli():
    pass


@cli.command()
@click.option("-s", "--site", type=str, default="/", help="/app_path")
@click.option("-h", "--hostname", type=str, default="localhost", help="localhost")
@click.option("-p", "--port", type=int, default=9000, help="9000")
@click.option("--reloader", is_flag=True, default=True)
@click.option("--debugger", is_flag=True, default=False)
@click.option("--evalex", is_flag=True, default=False)
@click.option("--threaded", is_flag=True)
@click.option("--processes", type=int, default=1, help="1")
def runserver(site, hostname, port, reloader, debugger, evalex, threaded, processes):

    basedir = os.path.abspath(os.getcwd()) + site

    """Start a new development server."""
    app = dispatcher.wsgi(
        basedir,
        hostname,
        port,
        use_reloader=reloader,
        use_debugger=debugger,
        use_evalex=evalex,
        threaded=threaded,
        processes=processes,
    )  # , ssl_context=(crt, key))

    app.serve()


def before_reload():
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        banner()


def after_reload():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # The reloader has restarted, we can put init code here
        pass


def banner():
    print(
        """
               __                __
        .-----|__.--------.-----|  .-----.----.----.
        |__ --|  |        |  _  |  |  -__|   _|   _|
        |_____|__|__|__|__|   __|__|_____|__| |__|
                          |__| v{}

        Welcome to simplerr! The framework aiming to
        keep it easy, clean and simple!

        You run `python -m simplerr runserver` with
        additional parameters, for example:

          `--site project/website` set a web path
          `--host 192.168.0.1` to specify bind host
          `--port 8080` to open specific port
          `--help` to see more options
    """.format(
            sversion
        )
    )


if __name__ == "__main__":
    before_reload()
    after_reload()
    cli()
