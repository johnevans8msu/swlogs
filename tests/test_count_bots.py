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
            actual = o.top20['hits']

        data = [
            'dspace-internal', 'bingbot/2.0', "Safari/iOS/WebKit on iPhone"
        ]
        index = pd.Index(data, name='ua')
        data = [86, 12, 2]
        expected = pd.Series(index=index, data=data, name='hits')
        pd.testing.assert_series_equal(actual, expected)

