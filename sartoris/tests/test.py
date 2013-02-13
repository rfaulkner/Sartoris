# -*- coding: utf-8 -*-

"""
    sartoris.testsuite
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Wikimedia Foundation.
    :license: BSD, see LICENSE for more details.
"""

import unittest
import sartoris


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
        s = sartoris.Sartoris()
        assert 'top_dir' in s.config

    def test_conf_top_dir(self):
        s = sartoris.Sartoris()
        assert 'hook_dir' in s.config

    def test_conf_repo_name(self):
        s = sartoris.Sartoris()
        assert 'repo_name' in s.config

    def test_conf_deploy_file(self):
        s = sartoris.Sartoris()
        assert 'deploy_file' in s.config

    def test___new__(self):
        # sartoris = Sartoris(*args, **kwargs)
        assert False  # TODO: implement your test here


class TestSartorisFunctionality(unittest.TestCase):
    def test_abort(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.abort(args))
        assert False  # TODO: implement your test here

    def test_diff(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.diff(args))
        assert False  # TODO: implement your test here

    def test_log_deploys(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.log_deploys(args))
        assert False  # TODO: implement your test here

    def test_resync(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.resync(args))
        assert False  # TODO: implement your test here

    def test_revert(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.revert(args))
        assert False  # TODO: implement your test here

    def test_show_tag(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.show_tag(args))
        assert False  # TODO: implement your test here

    def test_start(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.start(args))
        assert False  # TODO: implement your test here

    def test_sync(self):
        # sartoris = Sartoris(*args, **kwargs)
        # self.assertEqual(expected, sartoris.sync(args, no_deps, force))
        assert False  # TODO: implement your test here


class TestMain(unittest.TestCase):
    def test_main(self):
        # self.assertEqual(expected, main(argv, out, err))
        assert False  # TODO: implement your test here


class TestCli(unittest.TestCase):
    def test_cli(self):
        # self.assertEqual(expected, cli())
        assert False  # TODO: implement your test here
