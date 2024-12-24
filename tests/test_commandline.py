# standard library imports
import importlib.resources as ir
import unittest
from unittest import mock

# 3rd party library imports

# local imports
from swlogs import commandline


@mock.patch('swlogs.common.sqlalchemy')
@mock.patch('swlogs.common.psycopg.connect')
@mock.patch('swlogs.common.yaml')
class TestSuite(unittest.TestCase):

    def test_plot_bots(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['', '--bots']),
            mock.patch('swlogs.plots.Plot.run', new=lambda x: None),
        ):
            commandline.plot()

    def test_plot_overall(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['', '--overall']),
            mock.patch('swlogs.plots.Plot.run', new=lambda x: None),
        ):
            commandline.plot()

    def test_swreport(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_ip16(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program for ip16 addresses

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['', '--ip16']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_ip24(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program for ip24 addresses

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['', '--ip24']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_ip32(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program for ip32 addresses

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['', '--ip32']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_with_user_agent(self, mock_yaml, mock_psycopg, mock_sqlalchemy):  # noqa : E501
        """
        Scenario:  run command line program for bot report and a specific user
        agent

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['', '--useragent', 'something']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_with_specific_date(self, mock_yaml, mock_psycopg, mock_sqlalchemy):  # noqa : E501
        """
        Scenario:  run command line program for bot report and a specific date

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['', '--date', '2024-11-13']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_swreport_overall(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program for overall hits and bytes

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['--overall']),
            mock.patch('swlogs.swreports.SWReport.run', new=lambda x: None),
        ):
            commandline.swreport()

    def test_loglogs(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        logfile = ir.files('tests.data').joinpath('smoke.log')

        with (
            mock.patch('sys.argv', new=['', '--logfile', str(logfile)]),
            mock.patch('swlogs.loglogs.LogLogs.run', new=lambda x: None),
        ):
            commandline.loglogs()

        self.assertTrue(True)

    def test_loglogs_no_optional_arguments(self, mock_yaml, mock_psycopg, mock_sqlalchemy):  # noqa : E501
        """
        Scenario:  run command line program

        Expected result:  no errors
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        with (
            mock.patch('sys.argv', new=['']),
            mock.patch('swlogs.commandline.LogLogs.run', new=lambda x: None),
        ):
            commandline.loglogs()

        self.assertTrue(True)
