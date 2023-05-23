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
