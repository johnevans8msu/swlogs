# standard library imports
from datetime import date, timedelta
import sys  # noqa : F401

# 3rd party library imports
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# local imports
from .common import CommonObj

sns.set()


class Plot(CommonObj):
    """
    Plot hit history of top n bots
    """

    def __init__(self, bots=False, overall=False, numbots=5):
        super().__init__()

        self.bots = bots
        self.overall = overall
        self.n = numbots

    def run(self):

        if self.bots:
            self.plot_bots()
        else:
            self.plot_overall()

    def plot_bots(self):

        # Get the top n bots for yesterday.
        yesterday = date.today() - timedelta(days=1)
        sql = f"""
            select ua from bots
            where date = "{yesterday.isoformat()}"
                and ua <> "dspace-internal"
            order by hits desc
            limit {self.n}
            """
        df = pd.read_sql(sql, self.conn)
        ua = df['ua']

        # select history for those bots
        sql = f"""
            select date, ua, hits
            from bots
            where ua in ('{'\', \''.join([x for x in ua.values])}')
            order by date asc
        """
        df = pd.read_sql(sql, self.conn)
        df['date'] = pd.to_datetime(df['date'])

        fig, ax = plt.subplots()
        sns.lineplot(data=df, x='date', y='hits', hue='ua', ax=ax)

        ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator())
        ax.set_xlabel('')

        fig.autofmt_xdate()
        plt.show()

    def plot_overall(self):

        fig, axes = plt.subplots(nrows=2, sharex=True)

        sql = """
            select
                date,
                cast(sum(bytes) as real) /1024/1024/1024 as bytes,
                cast(sum(hits) as real) / 1e6 as hits
            from overall
            group by date
        """
        df = pd.read_sql(sql, self.conn, index_col='date')

        # get rid of the last day, it's usually just a few observations
        df = df[:-1]

        df['hits'].plot(ax=axes[0])
        axes[0].set_ylabel('M Hits')

        df['bytes'].plot(ax=axes[1])

        axes[1].set_ylabel('GBytes')
        axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=30)
        axes[1].set_xlabel('')

        fig.tight_layout()

        plt.show()
