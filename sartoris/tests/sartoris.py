# -*- coding: utf-8 -*-
"""
    sartoris.testsuite
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 by Wikimedia Foundation.
    :license: BSD, see LICENSE for more details.
"""

import unittest


class TestNullHandler(unittest.TestCase):
    def test_emit(self):
        # null_handler = NullHandler()
        # self.assertEqual(expected, null_handler.emit(record))
        assert False  # TODO: implement your test here


class TestParseargs(unittest.TestCase):
    def test_parseargs(self):
        # self.assertEqual(expected, parseargs(argv))
        assert False  # TODO: implement your test here


class TestSartoris(unittest.TestCase):
    def test___init__(self):
        # sartoris = Sartoris(*args, **kwargs)
        assert False  # TODO: implement your test here

    def test___new__(self):
        # sartoris = Sartoris(*args, **kwargs)
        assert False  # TODO: implement your test here

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

if __name__ == '__main__':
    unittest.main()
