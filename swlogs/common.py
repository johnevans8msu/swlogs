# standard library imports
import pathlib

# 3rd party library imports
import psycopg
import sqlalchemy
import yaml

# local imports


class CommonObj(object):
    """
    Attributes
    ----------
    dbfile : str or path
        Database file
    """

    def __init__(self):

        self.setup_config()
        self.setup_postgresql_connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def setup_postgresql_connection(self):
        self.conn = psycopg.connect(self.connstr)
        self.engine = sqlalchemy.create_engine(self.connstr)

    def setup_config(self):
        """
        Look for parts of the postgresql connection string here.
        """
        p = pathlib.Path.home() / '.config/swlogs/config.yml'
        config = yaml.safe_load(p.read_text())

        self.connstr = config['connection_string']
