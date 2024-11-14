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

    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect(self.dbfile)

    def run(self):

        sql = """
            select * from bots
            where date='2024-11-13'
        """
        df = pd.read_sql(sql, self.conn)

        print(df)
