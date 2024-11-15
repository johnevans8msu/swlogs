# standard library imports
from datetime import date, timedelta
import sqlite3
import sys  # noqa : F401

# 3rd party library imports
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set()

# local imports
from .common import CommonObj


class PlotOverall(CommonObj):

    def __init__(self):
        super().__init__()

    def run(self):

        fig, axes = plt.subplots(nrows=2)

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

        plt.show()
