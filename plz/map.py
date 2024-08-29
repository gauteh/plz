from cartopy.io import img_tiles


class NorgeIBilder(img_tiles.GoogleWTS):
    """
    Norge i bilder, ortofoto.

    Usage:

    >>> fig = plt.figure()
    >>> img = NIB(cache=True)
    >>> ax = fig.add_subplot(1,1,1, projection=img.crs)
    >>> ax.add_image(img, 12)

    Credits:

        Norge i bilder inneholder lisensierte data. Løsningen omfatter ortofoto
        både fra Geovekst og Omløpsfoto, der andre parter i tillegg til
        Kartverket er rettighetshavere. I tillegg har kommunene Oslo, Bærum,
        Stavanger, Bergen og Trondheim gjennom egne kartleggingsprosjekter
        publisert bilder i Norge i bilder som parter i Norge digitalt. For all
        kommersiell bruk gjelder at man må innhente tillatelse fra
        rettighetshaver. Dette oppnås gjennom å kontakte Formidlingstjenesten i
        Kartverket eller en av våre forhandlere.



        For ikke-kommersiell bruk av dataene: Ta kontakt med en av
        rettighetshaverne for tillatelse til publisering i for eksempel
        rapporter, historielagsartikler o.l. Som kildehenvisning skal i disse
        tilfellene stå:
        © Statens kartverk, Geovekst og kommunene, <Prosjektnavn og årstall>.


    Based on URL found on JOSM (open street map).
    """

    def __init__(self, cache=False):
        super().__init__(cache=cache)

    def _image_url(self, tile):
        x, y, z = tile
        return (
            f'https://waapi.webatlas.no/maptiles/tiles/webatlas-orto-newup/wa_grid/{z}/{x}/{y}.jpeg?api_key=b8e36d51-119a-423b-b156-d744d54123d5'
        )


NIB = NorgeIBilder


def figure_nib(level=None, cache=False, *args, **kwargs):
    import matplotlib.pyplot as plt
    fig = plt.figure(*args, **kwargs)
    ax = addsubplot_nib(fig, level, cache, 1, 1, 1)
    return fig, ax


def addsubplot_nib(fig=None,
                   level=None,
                   cache=False,
                   nrows=1,
                   ncols=1,
                   index=1,
                   *args,
                   **kwargs):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs

    if fig is None:
        fig = plt.gcf()

    img = NIB(cache)
    ax = fig.add_subplot(nrows, ncols, index, projection=img.crs, *args, **kwargs)
    ax.add_image(img, level)

    gcrs = ccrs.PlateCarree()

    gl = ax.gridlines(gcrs, draw_labels=True)
    gl.top_labels = None

    return ax
