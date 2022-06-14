from cartopy.io import img_tiles

class NorgeIBilder(img_tiles.GoogleWTS):
    """
    Based on URL found on JOSM (open street map).
    """
    def __init__(self, cache=False):
        super().__init__(cache=cache)

    def _image_url(self, tile):
        x, y, z = tile
        return (
            f'https://waapi.webatlas.no/maptiles/tiles/webatlas-orto-newup/wa_grid/{z}/{x}/{y}.jpeg?api_key=b8e36d51-119a-423b-b156-d744d54123d5'
        )
