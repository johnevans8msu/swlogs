# standard library imports
import importlib.resources as ir
import unittest

# 3rd party library imports
import pandas as pd
import psycopg
import sqlalchemy
import testing.postgresql

# local imports


class CommonTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Recreate the schemas, tables, and indices before running each test.
        """
        # Spin up a postgresql instance
        cls.postgresql = testing.postgresql.Postgresql()

        # create a connection engine
        cls.engine = sqlalchemy.create_engine(cls.postgresql.url())
        cls.connstr = cls.postgresql.url()
        cls.conn = psycopg.connect(cls.connstr, autocommit=True)

        with cls.conn.cursor() as cursor:
            for p in sorted(ir.files('swlogs.migrations').glob('*.sql')):
                text = p.read_text()
                for statement in text.split('\n\n'):
                    cursor.execute(statement.rstrip().rstrip(';'))

            sql = "alter database test set search_path to swlogs"
            cursor.execute(sql)

            cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.postgresql.stop()

    def setUp(self):
        """
        Truncate all tables before each test.
        """
        sql = """
            select * from information_schema.tables
            where table_schema = 'swlogs'
        """
        df = pd.read_sql(sql, self.engine)

        with self.conn.cursor() as cursor:
            for idx, table in df['table_name'].items():
                sql = f"truncate table swlogs.{table}"
                cursor.execute(sql)

        self.conn.commit()

    def tearDown(self):
        pass
