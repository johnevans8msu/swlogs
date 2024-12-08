# standard library imports
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

    def log_ip16(self):

        self.df_ip16['date'] = self.df['date'].mode().iloc[0]
        self.df_ip16.to_sql('ip16', self.conn, if_exists='append')

    def log_ip24(self):

        self.df_ip24['date'] = self.df['date'].mode().iloc[0]
        self.df_ip24.to_sql('ip24', self.conn, if_exists='append')

    def log_ip32(self):

        self.df_ip32['date'] = self.df['date'].mode().iloc[0]
        self.df_ip32.to_sql('ip32', self.conn, if_exists='append')

    def log_bots(self):

        self.top_n['date'] = self.df['date'].mode().iloc[0]
        self.top_n.to_sql('bots', self.conn, if_exists='append')

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
        self.log_ip32()
        self.log_ip24()
        self.log_ip16()
