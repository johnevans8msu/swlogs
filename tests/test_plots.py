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
from swlogs.plots import Plot


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

        Expected result:  no errors, there were two matplotlib plot calls
        """

        newconn = sqlite3.connect(self.dbfile)

        with patch('swlogs.plots.pd.Series.plot') as mock_plot:
            with patch('swlogs.plots.plt.subplots') as mock_subplots:
                mock_subplots.return_value = (Mock(), (Mock(), Mock()))
                with Plot() as o:
                    with patch.object(o, 'conn', new=newconn):
                        o.run()

            self.assertEqual(len(mock_plot.mock_calls), 2)

    def test_smoke_bots(self):
        """
        Scenario:  bots plot

        Expected result:  no errors, there was one seaborn plot call
        """

        newconn = sqlite3.connect(self.dbfile)

        with (
            patch('swlogs.plots.date') as mock_date,
            patch('swlogs.plots.plt.subplots') as mock_subplots,
        ):
            mock_date.today.return_value = dt.date(2024, 11, 14)
            mock_subplots.return_value = (Mock(), Mock())

            with (
                patch('swlogs.plots.mpl.ticker'),
                patch('swlogs.plots.sns.lineplot') as mock_sns_plots,
                Plot(bots=True) as o,
                patch.object(o, 'conn', new=newconn),
            ):
                o.run()

            self.assertEqual(len(mock_sns_plots.mock_calls), 1)
