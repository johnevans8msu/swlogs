# standard library imports
import sqlite3
import sys  # noqa : F401

# 3rd party library imports
import pandas as pd

# local imports
from .common import CommonObj

pd.options.display.float_format = '{:,.1f}'.format
pd.options.display.max_columns = 200
pd.options.display.width = 200


class SWReport(CommonObj):

    def __init__(self, overall=False):
        super().__init__()

        self.overall = overall
        self.conn = sqlite3.connect(self.dbfile)

    def run(self):

        if self.overall:
            self.run_overall()
        else:
            self.run_bots()

    def run_overall(self):

        sql = """
            select
                date,
                cast(sum(bytes) as real)/1024/1024/1024 as GBytes,
                cast(sum(hits) as real) / 1e6 as 'hits (million)'
            from overall
            group by date
        """
        df = pd.read_sql(sql, self.conn, index_col='date')

        print(df)

    def run_bots(self):

        sql = """
            select * from bots
            where date='2024-11-13'
        """
        df = pd.read_sql(sql, self.conn, index_col='date')

        print(df)
