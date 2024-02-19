import logging

from . import map
from . import xr


def log(level='debug', mpl_level=logging.WARNING):
    import coloredlogs
    coloredlogs.install(level)

    import logging
    logging.getLogger('matplotlib').setLevel(mpl_level)
