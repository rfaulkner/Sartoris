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

import datetime
import dulwich
import logging
import optparse
import os
import sys
import subprocess
from dulwich.config import StackedConfig

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
    raise NotImplementedError()

def abort():
    """
        * reset state back to start tag
        * remove lock file
    """
    raise NotImplementedError()

def sync(no_deps=False,force=False):
    """
        * add a sync tag
        * write a .deploy file with the tag information
        * call a sync hook with the prefix (repo) and tag info
    """
    #TODO: do git calls in dulwich, rather than shelling out
    #TODO: get all configuration via a function, and get it during main
    sc = StackedConfig(StackedConfig.default_backends())
    try:
        hook_dir = sc.get('deploy','hook-dir')
    except KeyError:
        log.error('Failed to pull deploy.hook-dir from configuration')
        sys.exit(1)
    try:
        repo_name = sc.get('deploy','tag-prefix')
    except KeyError:
        log.error('Failed to pull deploy.tag-prefix from configuration')
        sys.exit(1)
    sync_dir = '{0}/sync'.format(hook_dir)
    sync_script = '{0}/{1}.sync'.format(sync_dir, repo_name)
    _tag = "{0}-sync-{1}".format(repo_name,
                                 datetime.now().strftime(DATE_TIME_TAG_FORMAT))
    proc = subprocess.Popen(['/usr/bin/git tag', '-a', _tag])
    if proc.returncode != 0:
        log.error('Failed to write sync tag')
        sys.exit(1)
    #TODO: use a pluggable sync system rather than shelling out
    if os.path.exists(sync_script):
        proc = subprocess.Popen([sync_script, repo_name, tag, force])
        log.info(proc.stdout.read())
        if proc.returncode != 0:
            log.error('Sync script "{0}" failed to run'.format(sync_script))
            sys.exit(1)

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

def log():
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

if __name__ == "__main__": # pragma: nocover
    sys.exit(main(sys.argv))

