import os
import bottle
from bottle import *


class Route(bottle.Route):
    """
    Nadomestni razred za poti s privzetimi imeni.
    """
    def __init__(self, app, rule, method, callback, name=None, plugins=None, skiplist=None, **config):
        if name is None:
            name = callback.__name__
        def decorator(*largs, **kwargs):
            bottle.request.environ['SCRIPT_NAME'] = os.environ.get('BOTTLE_ROOT', '')
            return callback(*largs, **kwargs)
        super().__init__(app, rule, method, decorator, name, plugins, skiplist, **config)

bottle.Route = Route
