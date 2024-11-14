# standard library imports
from datetime import date, datetime
import sqlite3

# 3rd party library imports
import pandas as pd

# local imports
from .access_logs import AccessLog


class LogLogs(AccessLog):
    """
    Attributes
    ----------
    logfile : path
        Process this apache/nginx logfile.
    dbfile: path
        Location of sqlite database file.
    views : bool
        If True, compute views instead of hits.
    conn : sqlite3.Connection
    """
    def __init__(
        self,
        logfile='/var/log/nginx/access.log.1',
        dbfile='/home/jevans/Documents/swlogs/access.db',
        views=False
    ):
        super().__init__(logfile)

        self.dbfile = dbfile
        self.conn = sqlite3.connect(dbfile)

    def log_bots(self):

        self.top20['date'] = self.df['date'].mode().iloc[0]
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
