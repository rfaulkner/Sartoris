#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`This`_ is a tool to manage using git as a deployment management tool

.. _This: https://gerrit.wikimedia.org/r/gitweb?p=sartoris.git
"""
__license__ = """\
Copyright (c) 2012-2013 Wikimedia Foundation <info@wikimedia.org>

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
import argparse
import os
import sys
import subprocess
from dulwich.config import StackedConfig
from datetime import datetime

exit_codes = {
    1: 'Operation failed.  Exiting.',
    2: 'Lock file already exists.  Exiting.',
    3: 'Please enter valid arguments.'
}

# Module level attribute for tagging datetime format
DATE_TIME_TAG_FORMAT = '%Y%m%d-%H%M%S'

# NullHandler was added in Python 3.1.
try:
    NullHandler = logging.NullHandler
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Add a do-nothing NullHandler to the module logger to prevent "No handlers
# could be found" errors. The calling code can still add other, more useful
# handlers, or otherwise configure logging.
log = logging.getLogger(__name__)
log.addHandler(NullHandler())


def parseargs(argv):
    """Parse command line arguments.

    Returns *args*, the list of arguments left over after processing.

    :param argv: a list of command line arguments, usually :data:`sys.argv`.
    """

    parser = argparse.ArgumentParser(
        description="This script performs ",
        epilog="",
        conflict_handler="resolve",
        usage="sartoris [-q --quiet] [-s --silent] [-v --verbose] [method]"
    )

    parser.allow_interspersed_args = False

    defaults = {
        "quiet": 0,
        "silent": False,
        "verbose": 0,
    }

    # Global options.
    parser.add_argument("method")
    parser.add_argument("-q", "--quiet",
        default=defaults["quiet"], action="count",
        help="decrease the logging verbosity")
    parser.add_argument("-s", "--silent",
        default=defaults["silent"], action="store_true",
        help="silence the logger")
    parser.add_argument("-v", "--verbose",
        default=defaults["verbose"], action="count",
        help="increase the logging verbosity")

    args = parser.parse_args()
    return args


class Sartoris(object):

    __instance = None                           # class instance

    def __init__(self, *args, **kwargs):
        """ Initialize class instance """
        self.__class__.__instance = self

        # @TODO add dulwich config

    def __new__(cls, *args, **kwargs):
        """ This class is Singleton, return only one instance """
        if not cls.__instance:
            cls.__instance = super(Sartoris, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def start(self):
        """
            * write a lock file
            * add a start tag
        """
        # @TODO use dulwich package implement git functionality rather
        #       than shell commands - http://www.samba.org/~jelmer/dulwich/

        # Create lock file - check if it already exists
        # @TODO catch exceptions for any os callable attributes
        if 'lock' in os.listdir('.git/deploy'):
            exit_code = 2
            log.error(__name__ + '::' + exit_codes[exit_code])
            return exit_code

        lock_file_handle = '.git/deploy/lock'
        log.info(__name__ + '::Creating lock file.')
        subprocess.call(['touch', lock_file_handle])

        # Add tags.  First retrieve the repository name then build the tag.
        try:
            repo_name = subprocess.Popen(['git', 'remote', '-v'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).stdout.readline().strip().split(
                '/')[-1].split('.git')[0]
        except KeyError:
            exit_code = 2
            log.error(__name__ + '::' + exit_codes[exit_code])
            return exit_code

        log.info(__name__ + '::Adding `start` tag for repo.')
        _tag = '{0}-start-{1}'.format(repo_name,
            datetime.now().strftime(DATE_TIME_TAG_FORMAT))
        subprocess.call(['git', 'tag', '-a', _tag, '-m',
                         '"Tag for {0}"'.format(repo_name)])

    def abort(self):
        """
            * reset state back to start tag
            * remove lock file
        """
        raise NotImplementedError()

    def sync(self, no_deps=False, force=False):
        """
            * add a sync tag
            * write a .deploy file with the tag information
            * call a sync hook with the prefix (repo) and tag info
        """
        #TODO: do git calls in dulwich, rather than shelling out
        #TODO: get all configuration via a function, and get it during main
        if 'lock' not in os.listdir('.git/deploy'):
            exit_code = 20
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        sc = StackedConfig(StackedConfig.default_backends())
        try:
            hook_dir = sc.get('deploy', 'hook-dir')
        except KeyError:
            exit_code = 21
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        try:
            repo_name = sc.get('deploy', 'tag-prefix')
        except KeyError:
            exit_code = 22
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        sync_dir = '{0}/sync'.format(hook_dir)
        sync_script = '{0}/{1}.sync'.format(sync_dir, repo_name)
        _tag = "{0}-sync-{1}".format(repo_name,
                                     datetime.now().strftime(
                                         DATE_TIME_TAG_FORMAT))
        proc = subprocess.Popen(['/usr/bin/git tag', '-a', _tag])
        if proc.returncode != 0:
            exit_code = 23
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        #TODO: use a pluggable sync system rather than shelling out
        if os.path.exists(sync_script):
            proc = subprocess.Popen([sync_script,
                                     '--repo="{0}"'.format(repo_name),
                                     '--tag="{0}"'.format(_tag),
                                     '--force="{0}"'.format(force)])
            log.info(proc.stdout.read())
            if proc.returncode != 0:
                exit_code = 24
                log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
                return exit_code

    def resync(self):
        """
            * write a lock file
            * call sync hook with the prefix (repo) and tag info
            * remove lock file
        """
        raise NotImplementedError()

    def revert(self):
        """
            * write a lock file
            * write previous deploy info into .deploy
            * call sync hook with the prefix (repo) and tag info
            * remove lock file
        """
        raise NotImplementedError()

    def show_tag(self):
        """
            * display current tagged release
        """
        raise NotImplementedError()

    def log_deploys(self):
        """
            * show last x deploys
        """
        raise NotImplementedError()

    def diff(self):
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
    if out is None:  # pragma: nocover
        out = sys.stdout
    if err is None:  # pragma: nocover
        err = sys.stderr
    args = parseargs(argv)
    level = logging.WARNING - ((args.verbose - args.quiet) * 10)
    if args.silent:
        level = logging.CRITICAL + 1

    format = "%(asctime)s %(levelname)-8s %(message)s"
    handler = logging.StreamHandler(err)
    handler.setFormatter(logging.Formatter(fmt=format,
        datefmt='%b-%d %H:%M:%S'))
    log.addHandler(handler)
    log.setLevel(level)

    log.debug("Ready to run")

    # Inline call to functionality - if Sartoris does not possess this
    #  attribute flag with logger
    if not args.method:
        print args.help
        return 3

    if hasattr(Sartoris(), args.method) and callable(getattr(Sartoris(),
        args.method)):
        getattr(Sartoris(), args.method)()
    else:
        log.error(__name__ + '::No function called %(method)s.' % {
            'method': args.method})

if __name__ == "__main__":  # pragma: nocover
    sys.exit(main(sys.argv))
