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


def closest_point(ds, y, x, dist='geo', threshold=None, dimx='X', dimy='Y'):
    """
    Find the index of the closest points in `ds` of `x` and `y`, when `x` and
    `y` are not dimensions but variables mapped on the coordinate variables.
    E.g. `lat` and `lon` 2D variables on `X` and `Y` 1D projection variables.

    Args:

        x, y: coordinates, lon, lat if geo

        dist: distance norm to use: 'l2' or 'geo'

        threshold: None, if set the max distance before raising an error.

        dimx, dimy: dimensions in ds to select on.

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

    if dist == 'l2':
        dist_x = ds[dimx] - x
        dist_y = ds[dimy] - y
        dist = np.sqrt(dist_x**2 + dist_y**2) # l2 norm
        print(dist)

    elif dist == 'geo':
        from pyproj import Geod
        g = Geod(ellps='WGS84')
        lon1 = ds[x.dims[0]].values
        lat1 = ds[y.dims[0]].values
        assert len(x) == 1 and len(y) == 1, "geo dist only supports length 1 x and y"
        assert lon1.shape == lat1.shape
        xx = x.values * np.ones(lon1.shape)
        yy = y.values * np.ones(lon1.shape)
        _az12, _az21, dist = g.inv(yy, xx, lat1, lon1)

    else:
        raise ValueError("unknown distance norm");

    distmin = dist.argmin(dim=(dimx, dimy))

    maxdist = dist.isel(**distmin)
    logger.info(f'closest_point: max distance is {maxdist}.')

    if threshold is not None:
        maxdist[maxdist>threshold] = np.nan
        if np.any(np.isnan(maxdist)):
            logger.error(f'distance exceeds threshold: {maxdist} > {threshold}')
            logger.debug(f'{x=}, {y=}')
            logger.debug(f'{ds=}')

            raise ValueError('distance exceeds threshold')

    return ds.isel(**distmin).assign(closest_point_distance=dist.isel(**distmin), closest_xi=distmin[dimx], closest_yi=distmin[dimy])
