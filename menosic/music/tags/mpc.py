from mutagenx.musepack import  Musepack
from music import tags

class Track(tags.Track):
    filetype = 'mpc'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.mpc = Musepack(path)
        f = self.mpc

        self.title = f.get('Title')
        self.discnumber = tags.number(f.get('Disc'))
        self.tracknumber = tags.number(f.get('Track'))
        self.length = int(f.info.length)
        self.bitrate = int(f.info.bitrate)

        self.musicbrainz_trackid = f.get('Musicbrainz_Trackid')
        self.genres = tags.item_to_list(f.get('Genre'))

        artist = tags.Artist()
        artist.name = f.get('Artist')
        artist.sortname = f.get('Artistsort')
        artist.musicbrainz_artistid = f.get('Musicbrainz_Artistid')
        self.artists.append(artist)

        album = tags.Album()
        album.title = f.get('Album')
        album.date = f.get('Originaldate') or f.get('Year')
        album.country = f.get('Releasecountry')
        album.musicbrainz_albumid = f.get('Musicbrainz_Albumid')
        album.musicbrainz_releasegroupid = f.get('Musicbrainz_Releasegroupid')
        album.labels = tags.item_to_list(f.get('Label'))
        album.albumtypes = tags.item_to_list(f.get('MUSICBRAINZ_ALBUMTYPE'))
        album.albumstatus = tags.item_to_list(f.get('MUSICBRAINZ_ALBUMSTATUS'))

        albumartist = tags.Artist()
        albumartist.name = f.get('Album Artist') or f.get('Albumartist')
        albumartist.sortname = f.get('Albumartistsort')
        albumartist.musicbrainz_artistid = f.get('Musicbrainz_Albumartistid')
        album.albumartists.append(albumartist)

        self.album = album
