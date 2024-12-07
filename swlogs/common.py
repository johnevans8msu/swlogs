# standard library imports

# 3rd party library imports
import psycopg
import sqlalchemy

# local imports


class CommonObj(object):
    """
    Attributes
    ----------
    dbfile : str or path
        Database file
    """

    def __init__(self):

        self.connstr = 'postgresql://jevans@localhost/jevans'
        self.conn = psycopg.connect(self.connstr)
        self.engine = sqlalchemy.create_engine(self.connstr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
