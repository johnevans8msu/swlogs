# standard library imports
import importlib.resources as ir
import io
import logging
import time

# 3rd party library imports

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
    conn : database connection
    """
    def __init__(
        self,
        logfile='/var/log/nginx/access.log.1',
        views=False
    ):
        super().__init__(logfile)

    def log_ip16(self):

        logging.warning('Starting log_ip16')
        t0 = time.time()

        sql = ir.files('swlogs.data').joinpath('ip16.sql').read_text()

        with self.conn.cursor() as cursor:
            cursor.execute(sql)

        self.conn.commit()

        t1 = time.time()
        logging.warning(f'Ending log_ip16, took {(t1 - t0):.1f} seconds')

    def log_ip24(self):

        logging.warning('Starting log_ip24')
        t0 = time.time()

        sql = ir.files('swlogs.data').joinpath('ip24.sql').read_text()

        with self.conn.cursor() as cursor:
            cursor.execute(sql)

        self.conn.commit()

        t1 = time.time()
        logging.warning(f'Ending log_ip24, took {(t1 - t0):.1f} seconds')

    def log_ip32(self):

        logging.warning('Starting log_ip32')
        t0 = time.time()

        sql = ir.files('swlogs.data').joinpath('ip32.sql').read_text()

        with self.conn.cursor() as cursor:
            cursor.execute(sql)

        self.conn.commit()

        t1 = time.time()
        logging.warning(f'Ending log_ip32, took {(t1 - t0):.1f} seconds')

    def log_bots(self):
        """
        Summarize the top bot information.
        """
        logging.warning('Starting log_bots')
        t0 = time.time()

        sql = ir.files('swlogs.data').joinpath('log-bots.sql').read_text()

        with self.conn.cursor() as cursor:
            cursor.execute(sql)

        self.conn.commit()

        t1 = time.time()
        logging.warning(f'Ending log_bots, took {(t1 - t0):.1f} seconds')

    def log_overall(self):
        """
        Record the total bytes and number of hits for the day
        """
        with self.conn.cursor() as cursor:

            sql = """
            insert into swlogs.overall
            (date, bytes, hits)
            select
                timestamp::date as date,
                sum(bytes) as bytes,
                count(*) as hits
            from swlogs.staging
            group by 1
            """
            cursor.execute(sql)

        self.conn.commit()

    def log_raw(self):
        """
        Record the raw log rows
        """
        logging.warning('Starting bulk insert of daily log items.')
        t0 = time.time()
        cols = ['ip', 'timestamp', 'status', 'ua', 'url', 'bytes']
        with self.conn.cursor() as cursor:

            cursor.execute('truncate swlogs.staging')

            buffer = io.StringIO()
            self.df[cols].to_csv(buffer, index=False)
            buffer.seek(0)
            with cursor.copy('copy swlogs.staging from stdin with (format csv, header)') as copy:  # noqa E501
                while data := buffer.read(1048576):
                    copy.write(data)

        t1 = time.time()
        msg = (
            f'log_raw:  '
            f'took {t1-t0} seconds to insert {self.df.shape[0]} rows.'
        )
        logging.warning(msg)

        self.conn.commit()

    def run(self):
        super().run()

        self.log_raw()

        self.log_overall()
        self.log_bots()
        self.log_ip32()
        self.log_ip24()
        self.log_ip16()
