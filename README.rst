========
Universe
========

.. image:: https://travis-ci.com/jbradberry/universe.svg?branch=master
    :target: https://travis-ci.com/jbradberry/universe

Universe will be a 4X turn-based strategy game, similar to `Stars <http://en.wikipedia.org/wiki/Stars%21>`_.


Requirements
------------

- Python >= 3.6


Installation
------------

Use pip to install universe from github
::

    $ mkvirtualenv universe -p $(which python3)
    (universe) $ pip install git+https://github.com/jbradberry/universe.git


Testing
-------

The tests can be run under the supported versions of Python using tox
::

    (universe) $ pip install tox
    (universe) $ tox

or under a particular version by using the standard library's unittest
discovery
::

    $ python -m unittest discover
