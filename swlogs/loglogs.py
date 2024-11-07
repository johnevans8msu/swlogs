# standard library imports
from datetime import date
import sqlite3

# 3rd party library imports
import pandas as pd

# local imports
from .access_logs import AccessLog

pd.options.display.float_format = '{:,.1f}'.format


class LogLogs(AccessLog):

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

    def __init__(self, infile, dbfile, views=False):
        super().__init__(infile)

        self.dbfile = dbfile
        self.conn = sqlite3.connect(dbfile)

    def run(self):
        super().run()

        self.top20['date'] = date.today()

        self.top20.to_sql('logs', self.conn, if_exists='append')
