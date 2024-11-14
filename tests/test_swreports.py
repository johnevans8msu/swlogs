import importlib.resources as ir
import io
import unittest
from unittest.mock import patch

# 3rd party library imports

from swlogs.swreports import SWReport


class TestSuite(unittest.TestCase):

    def test_bots_smoke(self):
        """
        Scenario:  report daily bots

        Expected result:  report is verified
        """

        with SWReport() as o:
            with patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout:
                o.run()

                actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-bots.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)
