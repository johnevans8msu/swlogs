"""
Report something about scholarworks.
"""

# standard library imports
from datetime import date, timedelta
import sys  # noqa : F401

# 3rd party library imports
import pandas as pd

# local imports
from .common import CommonObj

pd.options.display.float_format = '{:,.1f}'.format
pd.options.display.max_columns = 200
pd.options.display.width = 200


class SWReport(CommonObj):
    """
    Attributes
    ----------
    overall :bool
        If true, print the daily amounts of total bytes and hits.  Otherwise
        report the daily bot traffic.
    date : datetime.date
        The report may be restricted to this date.
    """

    def __init__(self, overall=False, thedate=None):
        super().__init__()

        self.overall = overall
        if thedate is None:
            self.date = date.today() - timedelta(days=1)
        else:
            self.date = thedate

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
            where date=?
        """
        params = (self.date.isoformat(),)
        df = pd.read_sql(sql, self.conn, params=params, index_col='date')

        print(df)
