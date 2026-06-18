"""
Tests for figure_seachart() and the underlying Kartverket WMTS/WMS services.

The old base URL https://cache.kartverket.no/v1/wmts returns HTTP 500
("invalid request"). The correct URL is the full capabilities path:
https://cache.kartverket.no/v1/wmts/1.0.0/WMTSCapabilities.xml

Alternative WMS: https://wms.geonorge.no/skwms1/wms.sjokartraster2
"""

import urllib.request
import urllib.error
import pytest


WMTS_CAPABILITIES_URL = (
    "https://cache.kartverket.no/v1/wmts/1.0.0/WMTSCapabilities.xml"
)
WMTS_BASE_URL_OLD = "https://cache.kartverket.no/v1/wmts"

GEONORGE_WMS = "https://wms.geonorge.no/skwms1/wms.sjokartraster2"


def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "plz-test/1.0"})
    resp = urllib.request.urlopen(req, timeout=timeout)
    return resp.status, resp.read()


def test_old_wmts_base_url_broken():
    """Confirm the old base URL is no longer functional (HTTP 500)."""
    try:
        status, _ = http_get(
            WMTS_BASE_URL_OLD + "?SERVICE=WMTS&REQUEST=GetCapabilities"
        )
        assert status != 200, (
            f"Old URL unexpectedly works (HTTP {status}). "
            "figure_seachart() may no longer need the fix."
        )
    except urllib.error.HTTPError as e:
        # 500 or other non-200 response — expected
        assert e.code != 200, f"Unexpected 200 from old URL via exception: {e}"


def test_wmts_capabilities_url_accessible():
    """The full capabilities URL must return HTTP 200."""
    status, body = http_get(WMTS_CAPABILITIES_URL)
    assert status == 200, f"WMTS capabilities URL returned HTTP {status}"
    assert b"WMTSCapabilities" in body or b"Capabilities" in body


def test_wmts_sjokartraster_layer_present():
    """The sjokartraster layer must be listed in the WMTS capabilities."""
    _, body = http_get(WMTS_CAPABILITIES_URL)
    assert b"sjokartraster" in body, (
        "Layer 'sjokartraster' not found in WMTS capabilities"
    )


def test_geonorge_wms_alternative_accessible():
    """
    Alternative: WMS service from geonorge (use add_wms instead of add_wmts).
    Layers include 'all', 'overseiling', 'kyst', and per-chart layers.
    """
    status, body = http_get(
        GEONORGE_WMS + "?SERVICE=WMS&REQUEST=GetCapabilities"
    )
    assert status == 200, f"Geonorge WMS returned HTTP {status}"
    assert b"sjokartraster" in body.lower() or b"Sj" in body


@pytest.mark.skipif(
    pytest.importorskip("cartopy", reason="cartopy not installed") is None,
    reason="cartopy not installed",
)
def test_figure_seachart_creates_figure():
    """figure_seachart() should return (fig, ax, layer) without errors."""
    cartopy = pytest.importorskip("cartopy")
    import matplotlib
    matplotlib.use("Agg")

    from plz.map import figure_seachart
    fig, ax, layer = figure_seachart()
    assert fig is not None
    assert ax is not None
    assert layer is not None
