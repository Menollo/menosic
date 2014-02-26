from mutagenx.mp3 import MP3
from music import tags

class Track(tags.Track):
    filetype = 'mp3'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.mp3 = MP3(path)

        self.title = self.mp3.get('TIT2')
        self.discnumber = tags.number(self.mp3.get('TPOS'))
        self.tracknumber = tags.number(self.mp3.get('TRCK'))
        self.length = int(self.mp3.info.length)
        self.bitrate = int(self.mp3.info.bitrate)

        self.musicbrainz_trackid = tags.data(self.mp3.get('UFID:http://musicbrainz.org'))
        self.genres = tags.item_to_list(self.mp3.get('TCON'))

        artist = tags.Artist()
        artist.name = self.mp3.get('TPE1')
        artist.sortname = self.mp3.get('TSOP')
        #artist.musicbrainz_artistid = self.mp3.get('TXXX:MusicBrainz Artist Id')[0]
        self.artists.append(artist)

        album = tags.Album()
        album.title = self.mp3.get('TALB')
        album.date = self.mp3.get('TDOR') or self.mp3.get('TDRC')
        album.country = self.mp3.get('TXXX:MusicBrainz Album Release Country')
        album.musicbrainz_albumid = self.mp3.get('TXXX:MusicBrainz Album Id')
        album.musicbrainz_releasegroupid = self.mp3.get('TXXX:MusicBrainz Release Group Id')
        album.labels = tags.item_to_list(self.mp3.get('TPUB'))
        album.albumtypes = tags.item_to_list(self.mp3.get('TXXX:MusicBrainz Album Type'))
        album.albumstatus = tags.item_to_list(self.mp3.get('TXXX:MusicBrainz Album Status'))

        albumartist = tags.Artist()
        albumartist.name = self.mp3.get('TPE2')
        albumartist.sortname = self.mp3.get('TSO2')
        album.albumartists.append(albumartist)

        self.album = album
