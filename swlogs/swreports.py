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
    ip24 : bool
        If true, generate the ip24 report
    ip32 : bool
        If true, generate the ip32 report
    """

    def __init__(
        self,
        ip16=False,
        ip24=False,
        ip32=False,
        overall=False,
        useragent=None,
        thedate=None
    ):
        super().__init__()

        self.ip16 = ip16
        self.ip24 = ip24
        self.ip32 = ip32
        self.overall = overall
        if thedate is None:
            self.date = date.today() - timedelta(days=1)
        else:
            self.date = thedate
        self.useragent = useragent

    def run(self):

        if self.overall:
            self.run_overall()
        elif self.ip16:
            self.run_ip16_report()
        elif self.ip24:
            self.run_ip24_report()
        elif self.ip32:
            self.run_ip32_report()
        else:
            self.run_bots()

    def run_ip16_report(self):
        """
        Print report for top ip addresses
        """

        sql = f"""
            select
                date,
                ip,
                hits
            from ip16
            where date = '{self.date.isoformat()}'
            order by hits desc
        """
        df = pd.read_sql(sql, self.conn, index_col='date')
        df['ip'] = df['ip'].astype(str)

        print(df)

    def run_ip24_report(self):
        """
        Print report for top ip addresses
        """

        sql = f"""
            select
                date,
                ip,
                hits
            from ip24
            where date = '{self.date.isoformat()}'
            order by hits desc
        """
        df = pd.read_sql(sql, self.conn, index_col='date')

        print(df)

    def run_ip32_report(self):
        """
        Print report for top ip addresses
        """

        sql = f"""
            select
                date,
                ip,
                hits as hits
            from ip32
            where date = '{self.date.isoformat()}'
            order by hits desc
        """
        df = pd.read_sql(sql, self.conn, index_col='date')

        print(df)

    def run_overall(self):

        sql = """
            select
                date,
                cast(sum(bytes) as real)/1024/1024/1024 as GBytes,
                cast(sum(hits) as real) / 1e6 as "hits (million)"
            from overall
            group by date
            order by date asc
        """
        df = pd.read_sql(sql, self.engine, index_col='date')

        print(df)

    def run_bots(self):

        if self.useragent is None:
            sql = """
                select
                    date,
                    ua,
                    hits,
                    error_pct,
                    c429,
                    robots,
                    xmlui,
                    sitemaps,
                    item_pct
                from bots
                where date = %(date)s
            """
            params = {'date': self.date.isoformat()}
            df = pd.read_sql(sql, self.engine, params=params, index_col='date')
        else:
            sql = """
                select
                    date,
                    ua,
                    hits,
                    error_pct,
                    c429,
                    robots,
                    xmlui,
                    sitemaps,
                    item_pct
                where
                    ua = %(useragent)s
                    and date <= %(date)s
            """
            params = {
                'useragent': self.useragent,
                'date': self.date.isoformat()
            }
            df = pd.read_sql(sql, self.conn, params=params, index_col='date')
            df = df.drop(labels='ua', axis='columns')

        print(df)
