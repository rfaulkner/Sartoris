#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`This`_ is a tool to manage using git as a deployment management tool

.. _This:   https://github.com/wikimedia/Sartoris/blob/master/sartoris.py

All of this is accomplished using only modules from the Python standard library
that are available in every installation.

"""
__license__ = """\
Copyright (c) 2012 Ryan Faulkner <rfaulkner@wikimedia.org>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.\
"""

import logging
import optparse
import sys
import os
from datetime import datetime

exit_codes = {
    1 : 'Operation failed.  Exiting.',
    2 : 'Lock file already exists.  Exiting.'
}

# Module level attribute for tagging datetime format
DATE_TIME_TAG_FORMAT = '%Y%m%d-%H%M%S'

# NullHandler was added in Python 3.1.
try:
    NullHandler = logging.NullHandler
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record): pass

# Add a do-nothing NullHandler to the module logger to prevent "No handlers
# could be found" errors. The calling code can still add other, more useful
# handlers, or otherwise configure logging.
log = logging.getLogger(__name__)
log.addHandler(NullHandler())

def parseargs(argv):
    """Parse command line arguments.

    Returns a tuple (*opts*, *args*), where *opts* is an
    :class:`optparse.Values` instance and *args* is the list of arguments left
    over after processing.

    :param argv: a list of command line arguments, usually :data:`sys.argv`.
    """
    prog = argv[0]
    parser = optparse.OptionParser(prog=prog)
    parser.allow_interspersed_args = False

    defaults = {
        "quiet": 0,
        "silent": False,
        "verbose": 0,
    }

    # Global options.
    parser.add_option("-q", "--quiet", dest="quiet",
        default=defaults["quiet"], action="count",
        help="decrease the logging verbosity")
    parser.add_option("-s", "--silent", dest="silent",
        default=defaults["silent"], action="store_true",
        help="silence the logger")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=defaults["verbose"], action="count",
        help="increase the logging verbosity")

    (opts, args) = parser.parse_args(args=argv[1:])
    return (opts, args)

def start():
    """
        * write a lock file
        * add a start tag
    """

    # Create lock file - check if it already exists
    if 'lock' in os.listdir('.git/deploy'):
        exit_code = 2
        log.error(__name__ + '::' + exit_codes[exit_code])
        return exit_code

    lock_file_handle = '.git/deploy/lock'
    log.info(__name__ + '::Creating lock file.')
    os.system('touch {0}'.format(lock_file_handle))

    # Add tags.  First retrieve the repository name then build the tag.
    try:
        repo_name = os.popen('git remote -v').read().split('/')[-1].split(
            '.git')[0]
    except KeyError:
        exit_code = 2
        log.error(__name__ + '::' + exit_codes[exit_code])
        return exit_code

    log.info(__name__ + '::Adding `start` tag for repo.')
    os.system('git tag -a {0}-start-{1}'.format(repo_name,
        datetime.now().strftime(DATE_TIME_TAG_FORMAT)))

def abort():
    """
        * reset state back to start tag
        * remove lock file
    """
    raise NotImplementedError()

def sync(): # -> fetch, finish, checkout
    """
        * add a sync tag
        * write a .deploy file with the tag information
        * call a sync hook with the prefix (repo) and tag info
    """
    raise NotImplementedError()

def resync():
    """
        * write a lock file
        * call sync hook with the prefix (repo) and tag info
        * remove lock file
    """
    raise NotImplementedError()

def revert():
    """
        * write a lock file
        * write previous deploy info into .deploy
        * call sync hook with the prefix (repo) and tag info
        * remove lock file
    """
    raise NotImplementedError()

def show_tag():
    """
        * display current tagged release
    """
    raise NotImplementedError()

def log_deploys():
    """
        * show last x deploys
    """
    raise NotImplementedError()

def diff():
    """
        * show a git diff of the last deploy and it's previous deploy
    """
    raise NotImplementedError()


def main(argv, out=None, err=None):
    """Main entry point.

    Returns a value that can be understood by :func:`sys.exit`.

    :param argv: a list of command line arguments, usually :data:`sys.argv`.
    :param out: stream to write messages; :data:`sys.stdout` if None.
    :param err: stream to write error messages; :data:`sys.stderr` if None.
    """
    print dir(log)
    if out is None: # pragma: nocover
        out = sys.stdout
    if err is None: # pragma: nocover
        err = sys.stderr
    (opts, args) = parseargs(argv)
    level = logging.WARNING - ((opts.verbose - opts.quiet) * 10)
    if opts.silent:
        level = logging.CRITICAL + 1

    format = "%(message)s"
    handler = logging.StreamHandler(err)
    handler.setFormatter(logging.Formatter(format))
    log.addHandler(handler)
    log.setLevel(level)

    log.debug("Ready to run")

    # Inline call to functionality
    #
    # @TODO: modify usage to avoid eval.
    #       1. Create a singleton class `Sartoris` which contains all of the git-deploy methods
    #       2. qualify args with `Sartoris` via duck-typing (e.g. hasattr, getattr, __callable__)
    #
    try:
        eval(args[0] + '()')
    except NameError:
        logging.error(__name__ + '::No function called %(func)s.' % {
            'func' : str(args[0])})


if __name__ == "__main__": # pragma: nocover
    sys.exit(main(sys.argv))

