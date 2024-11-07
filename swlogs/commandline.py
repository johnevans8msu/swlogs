# standard library imports
import argparse

# local imports
from swlogs.loglogs import LogLogs

def loglogs():

    parser = argparse.ArgumentParser()

    parser.add_argument('logfile', help='Access log')
    parser.add_argument('dbfile', help='database file')

    args = parser.parse_args()

    with LogLogs(args.logfile, args.dbfile) as o:
        o.run()
