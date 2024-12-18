# standard library imports
import sqlite3

# 3rd party library imports
import pandas as pd
import sqlalchemy


connstr = 'postgresql://jevans@localhost/jevans'
engine = sqlalchemy.create_engine(connstr)
conn3 = sqlite3.connect('/home/jevans/Documents/swlogs/access.db')

with engine.connect() as connection:

    df = pd.read_sql('select * from overall', conn3)
    df.to_sql(
        name='overall',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    df = pd.read_sql('select * from bots', conn3)

    df = df.rename(mapper={'429': 'c429'}, axis='columns')

    df['robots'] = df['robots'].astype(bool)
    df['xmlui'] = df['xmlui'].astype(bool)
    df['sitemaps'] = df['sitemaps'].astype(bool)

    df.to_sql(
        name='bots',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    df = pd.read_sql('select * from ip32', conn3)
    df.to_sql(
        name='ip32',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    df = pd.read_sql('select * from ip24', conn3)
    df = df.rename(mapper={'ip24': 'ip'}, axis='columns')
    df.to_sql(
        name='ip24',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    df = pd.read_sql('select * from ip16', conn3)
    df = df.rename(mapper={'ip16': 'ip'}, axis='columns')
    df.to_sql(
        name='ip16',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    connection.commit()
