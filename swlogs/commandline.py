# standard library imports
import argparse

# local imports
from swlogs.loglogs import LogLogs
from swlogs.swreports import SWReport


def loglogs():

    parser = argparse.ArgumentParser()

    parser.add_argument('--logfile', help='Access log', default='/var/log/nginx/access.log.1')
    parser.add_argument('--dbfile', help='database file', default='/home/jevans/Documents/swlogs/access.db')

    args = parser.parse_args()

    with LogLogs(logfile=args.logfile, dbfile=args.dbfile) as o:
        o.run()


def swreport():

    parser = argparse.ArgumentParser()
    parser.add_argument('--overall', action='store_true')

    args = parser.parse_args()

    with SWReport(overall=args.overall) as o:
        o.run()
