import importlib.resources as ir
import unittest

import pandas as pd

from swlogs.countbots import CountBots


class TestSuite(unittest.TestCase):

    def test_smoke(self):
        """
        Scenario:  read log file

        Expected result:  hits are verified
        """

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with CountBots(logfile) as o:
            o.run()
            actual = o.top_n['hits']

        data = [
            'dspace-internal', 'bingbot/2.0', "Safari/iOS/WebKit on iPhone"
        ]
        index = pd.Index(data, name='ua')
        data = [86, 12, 2]
        expected = pd.Series(index=index, data=data, name='hits')
        pd.testing.assert_series_equal(actual, expected)

    def test_ip24(self):
        """
        Scenario:  read log file

        Expected result:  24 bit ip addresses are verified
        """

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with CountBots(logfile) as o:
            o.run()
            actual = o.df_ip24

        data = [
            '24.57.50', '52.167.144', '153.90.6',
        ]
        index = pd.Index(data, name='ip24')
        data = {
            'hits': [2, 12, 86],
            'error_pct': [0.0, 0.0, 6.976744186046512]
        }
        expected = pd.DataFrame(index=index, data=data)
        pd.testing.assert_frame_equal(actual, expected)

    def test_ip32(self):
        """
        Scenario:  read log file

        Expected result:  32 bit ip addresses are verified
        """

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with CountBots(logfile) as o:
            o.run()
            actual = o.df_ip32

        data = [
            '24.57.50.45', '52.167.144.22', '153.90.6.244',
        ]
        index = pd.Index(data, name='ip')
        data = {
            'hits': [2, 12, 86],
            'error_pct': [0.0, 0.0, 6.976744186046512]
        }
        expected = pd.DataFrame(index=index, data=data)
        pd.testing.assert_frame_equal(actual, expected)
