# standard library imports
import sqlite3

# 3rd party library imports
import pandas as pd
import sqlalchemy


connstr = 'postgresql://jevans@localhost/jevans'
engine = sqlalchemy.create_engine(connstr)
conn3 = sqlite3.connect('/home/jevans/Documents/swlogs/access.db')

with engine.connect() as connection:
    sql = """
            CREATE TABLE IF NOT EXISTS swlogs.overall (
                id     int generated always as identity primary key,
                date   DATE,
                bytes  bigint,
                hits   bigint
            );
            create index on swlogs.overall (date);
    """
    result = connection.execute(sqlalchemy.text(sql))

    df = pd.read_sql('select * from overall', conn3)
    df.to_sql(
        name='overall',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    connection.commit()

    sql = """
         CREATE TABLE IF NOT EXISTS swlogs.bots (
           id        int generated always as identity primary key,
           ua        TEXT,
           hits      INTEGER,
           error_pct REAL,
           c429      INTEGER,
           robots    boolean,
           xmlui     boolean,
           sitemaps  boolean,
           item_pct  REAL,
           date      DATE
         );
    """
    connection.execute(sqlalchemy.text(sql))

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

    sql = """
         CREATE TABLE IF NOT EXISTS swlogs.ip32 (
           ip        cidr,
           hits      INTEGER,
           error_pct REAL,
           date      DATE
         );
    """
    connection.execute(sqlalchemy.text(sql))

    df = pd.read_sql('select * from ip32', conn3)
    df.to_sql(
        name='ip32',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    sql = """
         CREATE TABLE IF NOT EXISTS swlogs.ip24 (
           ip        cidr,
           hits      INTEGER,
           error_pct REAL,
           date      DATE
         );
    """
    connection.execute(sqlalchemy.text(sql))

    df = pd.read_sql('select * from ip24', conn3)
    df = df.rename(mapper={'ip24': 'ip'}, axis='columns')
    df.to_sql(
        name='ip24',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    sql = """
         CREATE TABLE IF NOT EXISTS swlogs.ip16 (
           ip        cidr,
           hits      INTEGER,
           error_pct REAL,
           date      DATE
         );
    """
    connection.execute(sqlalchemy.text(sql))

    df = pd.read_sql('select * from ip16', conn3)
    df = df.rename(mapper={'ip16': 'ip'}, axis='columns')
    df.to_sql(
        name='ip16',
        con=connection,
        if_exists='append',
        index=False,
        schema='swlogs'
    )

    sql = """
         CREATE TABLE IF NOT EXISTS swlogs.staging (
           ip        cidr,
           timestamp timestamp with time zone,
           status    INTEGER,
           useragent text,
           url       text,
           bytes     INTEGER
         );
    """
    connection.execute(sqlalchemy.text(sql))

    connection.commit()
