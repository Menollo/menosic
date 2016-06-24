from mutagenx.asf import ASF
from music.backend.tags import reader


l = reader.list_to_item


class Track(reader.Track):
    filetype = 'wma'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.wma = ASF(path)
        f = self.wma

        self.title = l(f.get('Title'))
        self.discnumber = reader.number(l(f.get('WM/PartOfSet')))
        self.tracknumber = reader.number(l(f.get('WM/TrackNumber')))
        self.length = int(f.info.length)
        self.bitrate = int(f.info.bitrate)

        self.musicbrainz_trackid = l(f.get('MusicBrainz/Track Id'))
        self.genres = f.get('WM/Genre')

        artist = reader.Artist()
        artist.name = l(f.get('Author'))
        artist.sortname = l(f.get('WM/ArtistSortOrder'))
        #artist.musicbrainz_artistid = self.mp3.get('TXXX:MusicBrainz Artist Id')[0]
        self.artist = artist

        for a in f.get('WM/ARTISTS', []):
            artist = reader.Artist()
            artist.name = a
            self.artists.append(artist)

        album = reader.Album()
        album.title = l(f.get('WM/AlbumTitle'))
        album.date = l(f.get('WM/OriginalReleaseYear') or f.get('WM/Year'))
        album.country = l(f.get('MusicBrainz/Album Release Country'))
        album.musicbrainz_albumid = l(f.get('MusicBrainz/Album Id'))
        album.musicbrainz_releasegroupid = l(f.get('MusicBrainz/Release Group Id'))
        album.labels = f.get('WM/Publisher')
        album.albumtypes = f.get('MusicBrainz/Album Type')
        album.albumstatus = f.get('MusicBrainz/Album Status')

        albumartist = reader.Artist()
        albumartist.name = l(f.get('WM/AlbumArtist'))
        albumartist.sortname = l(f.get('WM/AlbumArtistSortOrder'))
        album.artist = albumartist

        self.album = album
