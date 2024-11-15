# standard library imports
import datetime as dt
import importlib.resources as ir
import pathlib
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock
from unittest.mock import patch

# 3rd party library imports
import pandas as pd

# local imports
from swlogs.plots import PlotOverall


class TestSuite(unittest.TestCase):

    def setUp(self):
        """
        Before each test, setup a test SQLITE database.
        """

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

    def test_smoke_overall(self):
        """
        Scenario:  overall plot

        Expected result:  no errors
        """

        newconn = sqlite3.connect(self.dbfile)

        with patch('swlogs.plots.pd.Series.plot') as mock_plot:
            with patch('swlogs.plots.plt.subplots') as mock_subplots:
                mock_subplots.return_value = (Mock(), (Mock(), Mock()))
                with PlotOverall() as o:
                    with patch.object(o, 'conn', new=newconn):
                        o.run()

            self.assertEqual(len(mock_plot.mock_calls), 2)
