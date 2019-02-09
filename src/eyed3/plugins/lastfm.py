from pylast import SIZE_EXTRA_LARGE, SIZE_LARGE, SIZE_MEDIUM, SIZE_MEGA, SIZE_SMALL
from pylast import LastFMNetwork, WSError

api_k = "a5f0ac61e7db2481b054ba52ff9a654f"
api_s = "0c4a52ae5dcdbba1f9e782833a50b623"
_network = None


def Client():
    global _network
    if not _network:
        _network = LastFMNetwork(api_key=api_k, api_secret=api_s)
        _network.enable_rate_limit()
    return _network


def getArtist(artist):
    return Client().get_artist(artist)


def getAlbum(artist, title):
    return Client().get_album(artist, title)


def getAlbumArt(artist, title, size=SIZE_EXTRA_LARGE):
    return _getArt(getAlbum(artist, title), size=size)


def getArtistArt(artist, size=SIZE_EXTRA_LARGE):
    return _getArt(getArtist(artist), size=size)


def _getArt(obj, size=SIZE_EXTRA_LARGE):
    try:
        return obj.get_cover_image(size)
    except WSError:
        raise ValueError("{} not found.".format(obj.__class__.__name__))


if __name__ == "__main__":
    album = getAlbum("Melvins", "Houdini")
    for sz in (SIZE_SMALL, SIZE_MEGA, SIZE_MEDIUM, SIZE_LARGE,
               SIZE_EXTRA_LARGE):
        print(album.get_cover_image(sz))

    melvins = getArtist("Melvins")
    print(melvins)
    for sz in (SIZE_SMALL, SIZE_MEGA, SIZE_MEDIUM, SIZE_LARGE,
               SIZE_EXTRA_LARGE):
        print(melvins.get_cover_image(sz))
