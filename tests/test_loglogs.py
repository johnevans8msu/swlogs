import importlib.resources as ir
import unittest

import pandas as pd

from swlogs.countbots import CountBots


class TestSuite(unittest.TestCase):

    def test_smoke(self):
        """
        Scenario:  read log file

        Expected result:  no errors
        """

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with CountBots(logfile) as o:
            o.run()
