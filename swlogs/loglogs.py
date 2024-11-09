# standard library imports
from datetime import date, datetime
import sqlite3

# 3rd party library imports
import numpy as np
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

    def __init__(self, infile, dbfile, views=False, thedate=None):
        super().__init__(infile)

        self.dbfile = dbfile
        self.conn = sqlite3.connect(dbfile)

        if thedate is None:
            self.date = date.today()
        else:
            self.date = datetime.strptime(thedate, '%Y-%m-%d').date()

    def log_bots(self):

        self.top20['date'] = self.date
        self.top20.to_sql('bots', self.conn, if_exists='append')

    def log_overall(self):
        """
        Record the total bytes and number of hits for the day
        """
        self.df['date'] = self.df['timestamp'].apply(pd.Timestamp.date)

        df = (
            self.df.groupby('date')
                   .agg(bytes=('bytes', 'sum'), hits=('date', 'size'))
        )
        df.to_sql('overall', self.conn, if_exists='append')

    def run(self):
        super().run()
        self.log_overall()
        self.log_bots()
