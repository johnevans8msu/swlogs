# standard library imports
import argparse
import datetime as dt

# local imports
from swlogs.loglogs import LogLogs
from swlogs.swreports import SWReport


def loglogs():

    parser = argparse.ArgumentParser()

    parser.add_argument('logfile', help='Access log')
    parser.add_argument('dbfile', help='database file')

    args = parser.parse_args()

    with LogLogs(logfile=args.logfile, dbfile=args.dbfile) as o:
        o.run()

def swreport():

    parser = argparse.ArgumentParser()

    args = parser.parse_args()

    with SWReport() as o:
        o.run()
