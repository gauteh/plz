import xarray as xr
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

def open_mfdataset_overlap(url_base, time_series, timedim='time'):
    """
    Aggregate many files with some overlap together. The overlap is often in the time-dimension where
    files have produced by a model started at shorter time intervals than the simulation span.

    Example:

    >>> u = 'https://thredds.met.no/thredds/dodsC/ww3_4km_archive_files/%Y/%m/%d/ww3_4km_%Y%m%dT00Z.nc'
    >>> ds = open_mfdataset_overlap(u, pd.date_range('2023-01-01', '2023-01-15'))
    >>> print(ds)

    """
    urls = [t.strftime(url_base) for t in time_series]
    time_step = time_series[1] - time_series[0]
    logger.debug('Opening individual URLs...')
    datasets = [xr.open_dataset(u, chunks='auto').sel({timedim: slice(t, t+time_step-timedelta(seconds=1))})
                for u,t in zip(urls, time_series)]
    logger.debug('Concatenating...')
    ds = xr.concat(datasets, dim=timedim,
                   compat='override', combine_attrs='override', join='override', coords='all')
    return ds

