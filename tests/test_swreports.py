# standard library imports
import importlib.resources as ir
import io
import pathlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

# 3rd party library imports
import pandas as pd

# local imports
from swlogs.swreports import SWReport


class TestSuite(unittest.TestCase):

    def setUp(self):

        self.tdir = tempfile.TemporaryDirectory()

        self.dbfile = pathlib.Path(self.tdir.name) / 'test.db'
        conn = sqlite3.connect(self.dbfile)

        path = ir.files('tests.data.swreport').joinpath('bots.csv')
        df = pd.read_csv(path)
        df.to_sql('bots', conn, index=False)

        path = ir.files('tests.data.swreport').joinpath('overall.csv')
        df = pd.read_csv(path)
        df.to_sql('overall', conn, index=False)

    def tearDown(self):
        self.tdir.cleanup()

    def test_bots_smoke(self):
        """
        Scenario:  report daily bots

        Expected result:  report is verified
        """

        newconn = sqlite3.connect(self.dbfile)

        with SWReport() as o:
            with patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout:
                with patch.object(o, 'conn', new=newconn):
                    o.run()

                actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-bots.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_overall_smoke(self):
        """
        Scenario:  report overall

        Expected result:  report is verified
        """

        newconn = sqlite3.connect(self.dbfile)

        with SWReport(overall=True) as o:
            with patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout:
                with patch.object(o, 'conn', new=newconn):
                    o.run()

                actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-overall.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)