# standard library imports
import argparse
import datetime as dt

# local imports
from swlogs.loglogs import LogLogs
from swlogs.plots import PlotOverall, PlotBots
from swlogs.swreports import SWReport


def plot_bots():

    with PlotBots() as o:
        o.run()


def plot_overall():

    with PlotOverall() as o:
        o.run()


def loglogs():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--logfile',
        help='Access log',
        default='/var/log/nginx/access.log.1'
    )
    parser.add_argument(
        '--dbfile',
        help='database file',
        default='/home/jevans/Documents/swlogs/access.db'
    )

    args = parser.parse_args()

    with LogLogs(logfile=args.logfile, dbfile=args.dbfile) as o:
        o.run()


def swreport():

    parser = argparse.ArgumentParser()

    parser.add_argument('--overall', action='store_true')

    help = (
        'Restrict to this date (bot report only).  '
        'The default is yesterday.'
    )
    parser.add_argument(
        '--date',
        type=dt.date.fromisoformat,
        default=dt.date.today() - dt.timedelta(days=1),
        help=help
    )

    args = parser.parse_args()

    with SWReport(overall=args.overall, thedate=args.date) as o:
        o.run()
