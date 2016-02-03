class Error(Exception):
    """ Generic error class. """


class ErrorStats(Error):
    """ Stats dosn't work """


class NotFound(Error):
    """ Not found 404 """
