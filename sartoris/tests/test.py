# -*- coding: utf-8 -*-

"""
    sartoris.testsuite
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Wikimedia Foundation.
    :license: BSD, see LICENSE for more details.
"""

import unittest
from sartoris.sartoris import Sartoris, SartorisError, exit_codes
from sartoris import config
from dulwich.repo import Repo
from os import mkdir, chdir
from shutil import rmtree


def tester_deco(test_method):
    """
    Performs setup and teardown calls for all tests to decouple the state if
    the repo from this testing module.
    """
    def tester_wrap(self):
        init_test_repo()
        test_method(self)
        teardown_test_repo()
    return tester_wrap


def init_test_repo():
    """
    Create a test repo, change to directory
    """
    mkdir(config.TEST_REPO)
    Repo.init(config.TEST_REPO)
    chdir(config.TEST_REPO)


def teardown_test_repo():
    """
    Remove the test repo
    """
    chdir(config.SARTORIS_HOME)
    rmtree(config.TEST_REPO)


class TestNullHandler(unittest.TestCase):
    def test_emit(self):
        # null_handler = NullHandler()
        # self.assertEqual(expected, null_handler.emit(record))
        assert False  # TODO: implement your test here


class TestParseargs(unittest.TestCase):
    def test_parseargs(self):
        # self.assertEqual(expected, parseargs(argv))
        assert False  # TODO: implement your test here


class TestSartorisInit(unittest.TestCase):
    """ Test cases for Sartoris initialization and config """
    def test_conf_hook_dir(self):
        s = Sartoris()
        assert 'top_dir' in s.config

    def test_conf_top_dir(self):
        s = Sartoris()
        assert 'hook_dir' in s.config

    def test_conf_repo_name(self):
        s = Sartoris()
        assert 'repo_name' in s.config

    def test_conf_deploy_file(self):
        s = Sartoris()
        assert 'deploy_file' in s.config

    def test___new__(self):
        # sartoris = Sartoris(*args, **kwargs)
        assert False  # TODO: implement your test here


class TestSartorisFunctionality(unittest.TestCase):

    @tester_deco
    def test_abort(self):
        """
        abort - test to ensure that ``abort`` method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.start(None)
            sartoris_obj.sync(None)
            sartoris_obj.abort(None)

            # TODO - check lock file & commit

        except SartorisError:
            assert False

    def test_diff(self):
        """
        diff - test to ensure that ``diff`` method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.diff(None)
        except SartorisError:
            assert False

    def test_log_deploys(self):
        """
        log_deploys - test to ensure that ``log_deploys`` method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.log_deploys(None)
        except SartorisError:
            assert False

    def test_resync(self):
        """
        resync - test to ensure that ``resync`` method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.resync(None)
        except SartorisError:
            assert False

    def test_revert(self):
        """
        revert - test to ensure that ``revert`` method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.revert(None)
        except SartorisError:
            assert False

    @tester_deco
    def test_show_tag(self):
        """
        start - test to ensure that start method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.start(None)
            sartoris_obj.sync(None)
            sartoris_obj.show_tag(None)

        except SartorisError:
            assert False

    @tester_deco
    def test_start(self):
        """
        start - test to ensure that ``start`` method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.start(None)
        except SartorisError:
            assert False

    @tester_deco
    def test_sync(self):
        """
        sync - test to ensure that ``sync`` method functions
        without exception
        """
        sartoris_obj = Sartoris()
        try:
            sartoris_obj.start(None)
            sartoris_obj.sync(None)

            # TODO - check tag and deploy file
        except SartorisError:
            assert False

    @tester_deco
    def test_deploy_in_progress(self):
        """
        deploy_in_progress - test to ensure that when the ``start`` method
        is called when a deployment is in progress Sartoris exits with error
        """
        sartoris_obj = Sartoris()

        # TODO - ensure that the repo is "fresh"

        # Call ``start`` twice
        try:
            sartoris_obj.start(None)
            sartoris_obj.start(None)
        except SartorisError as e:
            if not e.msg == exit_codes[2]:
                assert False
            return
        assert False


class TestMain(unittest.TestCase):
    def test_main(self):
        # self.assertEqual(expected, main(argv, out, err))
        assert False  # TODO: implement your test here


class TestCli(unittest.TestCase):
    def test_cli(self):
        # self.assertEqual(expected, cli())
        assert False  # TODO: implement your test here
