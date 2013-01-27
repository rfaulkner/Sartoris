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
    2: 'A deployment has already been started.  Exiting.',
    3: 'Please enter valid arguments.',
    4: 'Missing lock file.',
    5: 'Could not reset.',
    6: 'Diff failed.',
    7: 'Missing tag(s).',
    20: 'Cannot find top level directory for the git repository. Exiting.',
    21: 'Missing system configuration item "hook-dir". Exiting.',
    22: 'Missing repo configuration item "tag-prefix". '
        'Please configure this using:'
        '\n\tgit config tag-prefix <repo>',
    30: 'No deploy started. Please run: git deploy start',
    31: 'Failed to write tag on sync. Exiting.',
    32: 'Failed to write the .deploy file. Exiting.',
    40: 'Failed to run sync script. Exiting.',
    50: 'Failed to read the .deploy file. Exiting.',
}

class SartorisError(Exception):
    """ Basic exception class for UserMetric types """
    def __init__(self, message="Git deploy error.",exit_code=1):
        Exception.__init__(self, message)
        self._exit_code = int(exit_code)

    @property
    def exit_code(self): return self._exit_code

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

    # Module level attribute for tagging datetime format
    DATE_TIME_TAG_FORMAT = '%Y%m%d-%H%M%S'

    # Name of deployment directory
    DEPLOY_DIR = '.git/deploy/'

    # Name of lock file
    LOCK_FILE_HANDLE = 'lock'

    __instance = None                           # class instance

    def __init__(self, *args, **kwargs):
        """ Initialize class instance """
        self.__class__.__instance = self
        self._configure()
        self._tag = None                    # Stores tag state

    def __new__(cls, *args, **kwargs):
        """ This class is Singleton, return only one instance """
        if not cls.__instance:
            cls.__instance = super(Sartoris, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def _configure(self):
        """ Parse configuration from git config """
        sc = StackedConfig(StackedConfig.default_backends())
        self.config = {}
        proc = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'])
        if proc.returncode != 0:
            exit_code = 20
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            sys.exit(exit_code)
        self.config['top_dir'] = proc.stdout.read()
        self.config['deploy_file'] = self.config['top_dir'] + '/.git'
        try:
            self.config['hook_dir'] = sc.get('deploy', 'hook-dir')
        except KeyError:
            exit_code = 21
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            sys.exit(exit_code)
        try:
            self.config['repo_name'] = sc.get('deploy', 'tag-prefix')
        except KeyError:
            exit_code = 22
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            sys.exit(exit_code)
        self.config['sync_dir'] = '{0}/sync'.format(hook_dir)

    def _check_lock(self):
        """ Returns boolean flag on lock file existence """
        return os.path.exists(self.DEPLOY_DIR + self.LOCK_FILE_HANDLE)

    def _create_lock(self):
        """ Create a lock file """
        with open(self.DEPLOY_DIR + self.LOCK_FILE_HANDLE,'rb'): pass

    def _get_commit_sha_for_tag(self, tag):
        """ Obtain the commit sha of an associated tag
                e.g. `git rev-list $TAG | head -n 1` """
        # @TODO replace with dulwich

        cmd = "git rev-list {0} | head -n 1".format(tag)
        proc = subprocess.Popen(cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if not proc.returncode:
            return proc.stdout.readline().strip()
        else:
            raise SartorisError(message=exit_codes[8], exit_code=8)

    def start(self, args):
        """
            * write a lock file
            * add a start tag
        """
        # @TODO use dulwich package implement git functionality rather
        #       than shell commands - http://www.samba.org/~jelmer/dulwich/

        # Create lock file - check if it already exists
        # @TODO catch exceptions for any os callable attributes
        if self._check_lock():
            raise SartorisError(message=exit_codes[2])

        log.debug(__name__ + '::Creating lock file.')
        self._create_lock()

        # Tag the repo at this point
        repo_name = self.config['repo_name']
        log.debug(__name__ + '::Adding `start` tag for repo.')

        timestamp = datetime.now().strftime(self.DATE_TIME_TAG_FORMAT)
        _tag = '{0}-start-{1}'.format(repo_name, timestamp)
        subprocess.call(['git', 'tag', '-a', _tag, '-m',
                         '"Tag for {0}"'.format(repo_name)])
        return 0

    def abort(self, args):
        """
            * reset state back to start tag
            * remove lock file
        """

        # Get the commit hash of the current tag
        commit_sha = self._get_commit_sha_for_tag(self._tag)

        # 1. hard reset the index to the desired tree
        # 2. move the branch pointer back to the previous HEAD
        # 3. commit revert
        # @TODO replace with dulwich
        if subprocess.call("git reset --hard {0}".format(commit_sha).split()):
            raise SartorisError(message=exit_codes[5], exit_code=5)
        if subprocess.call("git reset --soft HEAD@{1}".split()):
            raise SartorisError(message=exit_codes[5], exit_code=5)
        if subprocess.call("git commit -m 'Revert to {0}'".format(commit_sha).
            split()):
            raise SartorisError(message=exit_codes[5], exit_code=5)

        # Remove lock file
        if os.listdir(self.DEPLOY_DIR).__contains__(self.LOCK_FILE_HANDLE):
            os.remove(self.LOCK_FILE_HANDLE)
        else:
            raise SartorisError(message=exit_codes[4])
        return 0

    def sync(self, args, no_deps=False, force=False):
        """
            * add a sync tag
            * write a .deploy file with the tag information
            * call a sync hook with the prefix (repo) and tag info
        """
        #TODO: do git calls in dulwich, rather than shelling out
        if 'lock' not in os.listdir('.git/deploy'):
            exit_code = 30
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        repo_name = self.config['repo_name']
        _tag = "{0}-sync-{1}".format(repo_name,
                                     datetime.now().strftime(
                                         DATE_TIME_TAG_FORMAT))
        proc = subprocess.Popen(['/usr/bin/git tag', '-a', _tag])
        if proc.returncode != 0:
            exit_code = 31
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        # Write .deploy file
        try:
            deploy_file = open(self.config['deploy_file'], 'w')
            deploy_file.write(json.dumps({'repo': repo_name, 'tag': _tag}))
            deploy_file.close()
        except OSError:
            exit_code = 32
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        return self._sync()

    def _sync(self, tag, force):
        repo_name = self.config['repo_name']
        sync_script = '{0}/{1}.sync'.format(self.config["sync_dir"], repo_name)
        #TODO: use a pluggable sync system rather than shelling out
        if os.path.exists(sync_script):
            proc = subprocess.Popen([sync_script,
                                     '--repo="{0}"'.format(repo_name),
                                     '--tag="{0}"'.format(_tag),
                                     '--force="{0}"'.format(force)])
            log.info(proc.stdout.read())
            if proc.returncode != 0:
                exit_code = 40
                log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
                return exit_code
        os.unlink('.git/deploy')
        return 0

    def resync(self, args):
        """
            * write a lock file
            * call sync hook with the prefix (repo) and tag info
            * remove lock file
        """
        if self._check_lock():
            exit_code = 2
            log.error(__name__ + '::' + exit_codes[exit_code])
            return exit_code
        self._create_lock()
        repo_name = self.config['repo_name']
        try:
            deploy_file = open(self.config['deploy_file'], 'r')
            deploy_info = deploy_file.read()
            deploy_info = json.loads(deploy_info)
        except OSError:
            exit_code = 50
            log.error("{0}::{1}".format(__name__, exit_codes[exit_code]))
            return exit_code
        return self._sync(repo_name, deploy_info["tag"], self.config(force))

    def revert(self, args):
        """
            * write a lock file
            * write previous deploy info into .deploy
            * call sync hook with the prefix (repo) and tag info
            * remove lock file
        """
        raise NotImplementedError()

    def show_tag(self, args):
        """
            * display current tagged release
        """
        raise NotImplementedError()

    def log_deploys(self, args):
        """
            * show last x deploys
        """
        raise NotImplementedError()

    def diff(self, args):
        """
            * show a git diff of the last deploy and it's previous deploy
        """

        # Get the last two tags - assumes tagging on deployment only
        proc = subprocess.Popen("git tag | head -n 2".split())
        if not proc.returncode:
            tag_last = proc.stdout.readline().strip()
            tag_second_last = proc.stdout.readline().strip()
            if not tag_last or not tag_second_last:
                raise SartorisError(message=exit_codes[7], exit_code=7)
        else:
            raise SartorisError(message=exit_codes[6], exit_code=6)

        # Get the associated commit hashes for those tags
        sha_1 = self._get_commit_sha_for_tag(tag_last)
        sha_2 = self._get_commit_sha_for_tag(tag_second_last)

        # Produce the diff
        # @TODO replace with dulwich
        proc = "git diff {0} {1}".format(sha_2, sha_1).split()
        line = proc.stdout.readline()
        while line:
            print line
            line = proc.stdout.readline()
        return 0


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
        try:
            getattr(Sartoris(), args.method)(args)
        except SartorisError as e:
            log.error(e.message)
            return e.exit_code
    else:
        log.error(__name__ + '::No function called %(method)s.' % {
            'method': args.method})

if __name__ == "__main__":  # pragma: nocover
    sys.exit(main(sys.argv))
