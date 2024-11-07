# standard library imports
import argparse
import datetime as dt

# local imports
from swlogs.loglogs import LogLogs


def loglogs():

    parser = argparse.ArgumentParser()

    parser.add_argument('logfile', help='Access log')
    parser.add_argument('dbfile', help='database file')
    parser.add_argument(
        '--date',
        help='Date of log file',
        default=f"{dt.date.today()}",
    )

    args = parser.parse_args()

    with LogLogs(args.logfile, args.dbfile, thedate=args.date) as o:
        o.run()
