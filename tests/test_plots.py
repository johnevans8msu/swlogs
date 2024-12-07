# standard library imports
import datetime as dt
import importlib.resources as ir
import unittest
from unittest.mock import Mock
from unittest.mock import patch

# 3rd party library imports
import pandas as pd

# local imports
from swlogs.plots import Plot


class TestSuite(unittest.TestCase):

    def test_smoke_overall(self):
        """
        Scenario:  overall plot

        Expected result:  no errors, there were two matplotlib plot calls
        """
        path = ir.files('tests.data.swreport').joinpath('overall.csv')
        df = pd.read_csv(path, parse_dates=['date'])

        with (
            patch('swlogs.plots.plt.subplots') as mock_subplots,
            patch('swlogs.plots.pd.Series.plot') as mock_plot,
            patch('swlogs.plots.mpl.ticker'),
            patch('swlogs.plots.pd.read_sql') as mock_read_sql,
        ):
            mock_read_sql.return_value = df
            mock_subplots.return_value = (Mock(), (Mock(), Mock()))

            with Plot() as o:
                o.run()

            self.assertEqual(len(mock_plot.mock_calls), 2)

    def test_smoke_bots(self):
        """
        Scenario:  bots plot

        Expected result:  no errors, there was one seaborn plot call
        """
        path = ir.files('tests.data.swreport').joinpath('bots.csv')
        df = pd.read_csv(path, parse_dates=['date'])

        with (
            patch('swlogs.plots.date') as mock_date,
            patch('swlogs.plots.pd.read_sql') as mock_read_sql,
            patch('swlogs.plots.plt.subplots') as mock_subplots,
            patch('swlogs.plots.mpl.ticker'),
            patch('swlogs.plots.sns.lineplot') as mock_sns_plots,
        ):
            mock_date.today.return_value = dt.date(2024, 11, 14)
            mock_read_sql.return_value = df
            mock_subplots.return_value = (Mock(), Mock())

            with Plot(bots=True) as o:
                o.run()

            self.assertEqual(len(mock_sns_plots.mock_calls), 1)
