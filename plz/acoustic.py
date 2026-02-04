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

    seatemp = gsw.t_from_CT(so, CT, pressure)

    c = 1449.2 + 4.6 * seatemp - 0.055 * seatemp**2 + 0.00029 * seatemp**3 + (
        1.34 - 0.01 * seatemp) * (so - 35.) + 0.016 * odepth

    return c


def oasesssp(depths, ssp, linear=False):
    """
    Generate a list of lines for the environment file to OASES.

    Args:

        depths: depth, positive in meters, increasing.

        ssp: sound speed in m/s

        linear: step-wise or linear output

    Returns:

        list of strings for the env file.
    """

    di = np.argmax(np.isnan(ssp))
    depths = depths[:di]
    ssp = ssp[:di]

    layers = []

    # make OASES env model
    #
    # IMPORTANT: need to have 0.0 depth twice!
    layers.append('0.00  0.0       0    0.0   0.0   0.00   0.0 0.0 0')

    if linear:
        if depths[0] != 0.0:
            layers.append("%.2f %.2f -%.2f 0.0 0.0 1.0264 0.0" %
                          (0.0, ssp[0], ssp[1]))

        for i, d in enumerate(depths[:-1]):
            # add linearliy increasing layers
            layers.append("%.2f %.2f -%.2f 0.0 0.0 1.0264 0.0" %
                          (d, ssp[i], ssp[i + 1]))

        # add last layer
        layers.append("%.2f %.2f 0.0 0.0 0.0 1.0264 0.0" %
                      (depths[-1], ssp[-1]))

    else:
        if depths[0] != 0.0:
            layers.append('%.2f  %.1f    0.0  0.0   0.0   1.000  0.0 0.0 0' %
                          (0.0, ssp[0]))  # from surface to first interface

        for i, d in enumerate(depths):
            layers.append('%.2f  %.1f    0.0  0.0   0.0   1.000  0.0 0.0 0' %
                          (d, ssp[i]))

    return layers
