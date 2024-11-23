import importlib.resources as ir
import tempfile
import unittest
from unittest import mock

from swlogs import commandline


class TestSuite(unittest.TestCase):

    def test_plot_bots(self):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        with (
            mock.patch('swlogs.plots.PlotBots.run', new=lambda x: None),
        ):
            commandline.plot_bots()

    def test_plot_overall(self):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        with (
            mock.patch('swlogs.plots.PlotOverall.run', new=lambda x: None),
        ):
            commandline.plot_overall()

    def test_swreport(self):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_ip16(self):
        """
        Scenario:  run command line program for ip16 addresses

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['', '--ip16']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_ip24(self):
        """
        Scenario:  run command line program for ip24 addresses

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['', '--ip24']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_ip32(self):
        """
        Scenario:  run command line program for ip32 addresses

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['', '--ip32']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_with_user_agent(self):
        """
        Scenario:  run command line program for bot report and a specific user
        agent

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['', '--useragent', 'something']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_with_specific_date(self):
        """
        Scenario:  run command line program for bot report and a specific date

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['', '--date', '2024-11-13']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_overall(self):
        """
        Scenario:  run command line program for overall hits and bytes

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['--overall']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_loglogs(self):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('smoke.log')

        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with mock.patch(
                'sys.argv',
                new=['', '--logfile', str(logfile), '--dbfile', str(dbfile)]
            ):
                commandline.loglogs()

        self.assertTrue(True)

    def test_loglogs_no_optional_arguments(self):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        with (
            mock.patch('sys.argv', new=['']),
            mock.patch('swlogs.commandline.LogLogs.run', new=lambda x: None),
        ):
            commandline.loglogs()

        self.assertTrue(True)
