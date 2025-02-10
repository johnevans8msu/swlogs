# standard library imports
import argparse
import datetime as dt

# local imports
from swlogs.loglogs import LogLogs
from swlogs.plots import Plot
from swlogs.swreports import SWReport


def plot():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--overall',
        help='Plot total hits, bytes',
        action='store_true'
    )
    parser.add_argument(
        '--bots',
        help='Plot bots',
        action='store_true'
    )
    parser.add_argument(
        '--n',
        help='Number of bots',
        type=int,
        default=5
    )

    args = parser.parse_args()

    with Plot(overall=args.overall, bots=args.bots, numbots=args.n) as o:
        o.run()


def loglogs():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--logfile',
        help='Access log',
        default='/var/log/nginx/access.log.1'
    )

    args = parser.parse_args()

    with LogLogs(logfile=args.logfile) as o:
        o.run()


def swreport():

    parser = argparse.ArgumentParser()

    parser.add_argument('--overall', action='store_true')
    parser.add_argument('--ip16', action='store_true')
    parser.add_argument('--ip24', action='store_true')
    parser.add_argument('--ip32', action='store_true')
    parser.add_argument('--useragent', help='Restrict to specific user agent')

    parser.add_argument(
        '--robots',
        action='store_true',
        help='Restrict to log entries where robots.txt was consulted.'
    )

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

    with SWReport(
        overall=args.overall,
        ip16=args.ip16,
        ip24=args.ip24,
        ip32=args.ip32,
        thedate=args.date,
        useragent=args.useragent,
        robots=args.robots,
    ) as o:
        o.run()
