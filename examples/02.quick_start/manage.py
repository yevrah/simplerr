#!/usr/bin/env python
import click
from simplerr import dispatcher


"""
Example usage

./manage.py runserver --site site
"""

@click.group()
def cli(): pass


@cli.command()
@click.option('-s', '--site', type=str, default='/', help='/site')
@click.option('-h', '--hostname', type=str, default='localhost', help="localhost")
@click.option('-p', '--port', type=int, default=5000, help="5000")
def runserver(site, hostname, port, reloader, debugger, evalex, threaded, processes):
    """Start a new development server."""
    app = dispatcher.wsgi(site, hostname, port,
               use_reloader=True,
               use_debugger=True,
               use_evalex=True,
               threaded=True,
               processes=4)

    app.serve()

if __name__ == '__main__':
    cli()
