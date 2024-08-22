import xarray as xr
import pandas as pd
import numpy as np
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
    datasets = [
        xr.open_dataset(u, chunks='auto').sel(
            {timedim: slice(t, t + time_step - timedelta(seconds=1))})
        for u, t in zip(urls, time_series)
    ]
    logger.debug('Concatenating...')
    ds = xr.concat(datasets,
                   dim=timedim,
                   compat='override',
                   combine_attrs='override',
                   join='override',
                   coords='all')
    return ds


def reset_time(ds: xr.Dataset,
               dim: str = 'time',
               unit='s',
               ref: pd.Timestamp = None,
               preserve_units=False):
    """
    Reset time to relative time in seconds since start (without units).

    Args:

        ref: Reference time, if None use first value in `dim`.

        dim: Time dimension to reset.
    """
    ds = ds.copy()

    if ref is None:
        ref = ds[dim].values[0]

    t = ds[dim].values - ref

    if not preserve_units:
        t = t / pd.to_timedelta(1., unit)

    ds = ds.assign_coords({dim: t})

    if not preserve_units:
        ds[dim].attrs['unit'] = 's'

    return ds


def nc_cmp(ds: xr.Dataset):
    """
    Encoding to compress NetCDF file.
    """
    encoding = {}
    for v in ds.variables:
        encoding[v] = {'zlib': True}

    return encoding


def closest_point(ds, x, y):
    """
    Find the index of the closest points in `ds` of `x` and `y`, when `x` and
    `y` are not dimensions but variables mapped on the coordinate variables.
    E.g. `lat` and `lon` 2D variables on `X` and `Y` 1D projection variables.

    e.g.:

    >>> lat, lon = 60.372601, 5.166712
    >>>
    >>> ds = xr.open_dataset('https://thredds.met.no/thredds/dodsC/sea/norkyst800m/1h/aggregate_be')
    >>> print(ds)
    >>>
    >>> # find closest point in lat, lon grid
    >>> ds = plz.xr.closest_point(ds, xr.DataArray([lat], dims='lat'), xr.DataArray([lon], dims='lon'))
    >>> print(ds)
    """

    dist_x = ds[x.dims[0]].values - x.values
    dist_y = ds[y.dims[0]].values - y.values
    dist = dist_x**2 + dist_y**2 # n2 norm

    xi, yi = np.unravel_index(np.argmin(dist), dist.shape)

    assert ds[x.dims[0]].dims == ds[y.dims[0]].dims

    xdim = ds[x.dims[0]].dims[0]
    ydim = ds[x.dims[0]].dims[1]

    return ds.isel({ xdim : xi, ydim : yi })
