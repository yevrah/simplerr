#!/usr/bin/env python
import click
from simplerr import dispatcher

@click.group()
def cli(): pass

@cli.command()
@click.option('-s', '--site', type=str, default='/', help='/app_path')
@click.option('-h', '--hostname', type=str, default='localhost', help="localhost")
@click.option('-p', '--port', type=int, default=5000, help="5000")
@click.option('--reloader', is_flag=True, default=False)
@click.option('--debugger', is_flag=True)
@click.option('--evalex', is_flag=True, default=False)
@click.option('--threaded', is_flag=True)
@click.option('--processes', type=int, default=1, help="1")
def runserver(site, hostname, port, reloader, debugger, evalex, threaded, processes):
    """Start a new development server."""
    app = dispatcher.wsgi(site, hostname, port,
               use_reloader=reloader,
               use_debugger=debugger,
               use_evalex=evalex,
               threaded=threaded,
               processes=processes) # , ssl_context=(crt, key))

    app.serve()



if __name__ == '__main__':
    cli()

