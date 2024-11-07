#!/usr/bin/env python

# standard library imports
import argparse
import sys


# 3rd party library imports
import pandas as pd

# local imports
from .access_logs import AccessLog

pd.options.display.float_format = '{:,.1f}'.format


class CountBots(AccessLog):

    """
    Attributes
    ----------
    inputfile: path
        Process this apache logfile.
    useragent : str or None
        If not None, restrict log entries to this user agent
    views : bool
        If True, compute views instead of hits.
    """

    def __init__(self, infile=None, useragent=None, views=False):
        super().__init__(infile, useragent=useragent)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run(self):

        super().run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin
    )

    help = "Restrict to this user agent"
    parser.add_argument('--useragent', help=help)

    help = "Compute views instead of hits."
    parser.add_argument('--views', help=help, action='store_true')

    args = parser.parse_args()

    with CountBots(
        args.infile, useragent=args.useragent, views=args.views
    ) as o:
        o.run()
