import importlib.resources as ir
import tempfile
import unittest
from unittest import mock

from swlogs import commandline


class TestSuite(unittest.TestCase):

    def test_loglogs(self):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('smoke.log')

        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with mock.patch('sys.argv', new=['', str(logfile), str(dbfile)]):
                commandline.loglogs()

        self.assertTrue(True)

    def test_with_date(self):
        """
        Scenario:  run command line program with a date specified

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('smoke.log')

        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with mock.patch(
                'sys.argv',
                new=['', str(logfile), str(dbfile), '--date', '2017-01-01']
            ):
                commandline.loglogs()

        self.assertTrue(True)
