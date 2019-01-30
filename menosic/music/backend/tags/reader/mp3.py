from mutagenx.mp3 import MP3
from music.backend.tags import reader


class Track(reader.Track):
    filetype = 'mp3'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.mp3 = MP3(path)

        self.title = self.mp3.get('TIT2')
        self.discnumber = reader.number(self.mp3.get('TPOS'))
        self.tracknumber = reader.number(self.mp3.get('TRCK'))
        self.length = int(self.mp3.info.length)
        self.bitrate = int(self.mp3.info.bitrate)

        self.musicbrainz_trackid = reader.data(self.mp3.get('UFID:http://musicbrainz.org'))
        self.genres = reader.item_to_list(self.mp3.get('TCON'))

        artist = reader.Artist()
        artist.name = self.mp3.get('TPE1')
        artist.sortname = self.mp3.get('TSOP')
        #artist.musicbrainz_artistid = self.mp3.get('TXXX:MusicBrainz Artist Id')[0]
        self.artist = artist

        for a in self.mp3.get('TXXX:Artists', []):
            artist = reader.Artist()
            artist.name = a
            self.artists.append(artist)

        album = reader.Album()
        album.title = self.mp3.get('TALB')
        album.date = self.mp3.get('TDOR') or self.mp3.get('TDRC')
        album.country = self.mp3.get('TXXX:MusicBrainz Album Release Country')
        album.musicbrainz_albumid = str(self.mp3.get('TXXX:MusicBrainz Album Id'))
        album.musicbrainz_releasegroupid = str(self.mp3.get('TXXX:MusicBrainz Release Group Id'))
        album.labels = reader.item_to_list(self.mp3.get('TPUB'))
        album.albumtypes = reader.item_to_list(self.mp3.get('TXXX:MusicBrainz Album Type'))
        album.albumstatus = reader.item_to_list(self.mp3.get('TXXX:MusicBrainz Album Status'))

        albumartist = reader.Artist()
        albumartist.name = self.mp3.get('TPE2')
        albumartist.sortname = self.mp3.get('TSO2')
        album.artist = albumartist

        self.album = album
