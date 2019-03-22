from mutagenx.mp3 import MP3
from music.backend.tags import reader

def l(i):
    if i:
        item = reader.list_to_item(i.text)
        if type(item) in (tuple, list):
            item = item[0]
        return item

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
        artist.name = l(self.mp3.get('TPE1'))
        artist.sortname = l(self.mp3.get('TSOP'))
        artist.musicbrainz_artistid = reader.item_to_list(self.mp3.get('TXXX:MusicBrainz Artist Id'))
        self.artist = artist

        for a, i in zip(
                reader.item_to_list(self.mp3.get('TXXX:Artists')) or [],
                reader.item_to_list(self.mp3.get('TXXX:MusicBrainz Artist Id')) or [],
                ):
            artist = reader.Artist()
            artist.name = a
            artist.musicbrainz_artistid = i
            self.artists.append(artist)

        album = reader.Album()
        album.title = l(self.mp3.get('TALB'))
        album.date = l(self.mp3.get('TDOR') or self.mp3.get('TDRC'))
        album.country = l(self.mp3.get('TXXX:MusicBrainz Album Release Country'))
        album.musicbrainz_albumid = str(self.mp3.get('TXXX:MusicBrainz Album Id'))
        album.musicbrainz_releasegroupid = str(self.mp3.get('TXXX:MusicBrainz Release Group Id'))
        album.labels = reader.item_to_list(self.mp3.get('TPUB'))
        album.albumtypes = reader.item_to_list(self.mp3.get('TXXX:MusicBrainz Album Type'))
        album.albumstatus = reader.item_to_list(self.mp3.get('TXXX:MusicBrainz Album Status'))

        albumartist = reader.Artist()
        albumartist.name = l(self.mp3.get('TPE2'))
        albumartist.sortname = l(self.mp3.get('TSO2'))
        albumartist.musicbrainz_artistid = reader.item_to_list(self.mp3.get('TXXX:MusicBrainz Album Artist Id'))
        album.artist = albumartist

        self.album = album
