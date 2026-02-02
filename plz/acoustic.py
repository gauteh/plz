import numpy as np
import gsw


def c(thetao, so, depth, lats):
    """
    Calculate sound speed.

    Pressure is calculated from depth and latitude using `gsw`.

    Args:

        thetao: potential temperature, T x D x lat x lon-array

        so: salinity, T x D x lat x lon-array

        depth: 1d array of depth

        lats: 1d array of latitudes

    Returns:

        sound speed, array with same dimensions as `thetao` and `so`.

    .. see-also::

        * http://glossary.ametsoc.org/wiki/Potential_temperature
        * https://bluerobotics.com/learn/pressure-depth-calculator/?waterType=fresh hydrostatic

    """
    odepth = depth
    depth, lats = np.meshgrid(depth, lats)
    pressure = gsw.p_from_z(-depth, lats).T

    CT = gsw.CT_from_pt(so, thetao)
    # print(CT.shape, pressure.shape)

    seatemp = gsw.t_from_CT(so, CT, pressure[np.newaxis, :, :, np.newaxis])

    c = 1449.2 + 4.6 * seatemp - 0.055 * seatemp**2 + 0.00029 * seatemp**3 + (
        1.34 - 0.01 * seatemp) * (
            so - 35.) + 0.016 * odepth[np.newaxis, :, np.newaxis, np.newaxis]

    return c
