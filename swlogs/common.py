# standard library imports

# 3rd party library imports

class CommonObj(object):
    """
    Attributes
    ----------
    dbfile : str or path
        Database file
    """

    def __init__(self, dbfile='/home/jevans/Documents/swlogs/access.db'):
        self.dbfile=dbfile

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
