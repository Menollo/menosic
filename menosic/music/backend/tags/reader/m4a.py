from mutagenx import mp4
from music.backend.tags import reader


def l(i):
    item = reader.list_to_item(i)
    if type(item) == tuple:
        item = item[0]
    if type(item) in (bytes, mp4.MP4FreeForm):
        item = item.decode('utf-8')
    return item


class Track(reader.Track):
    filetype = 'm4a'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.m4a = mp4.MP4(path)
        f = self.m4a

        self.title = l(f.get(b'\xa9nam'))
        self.discnumber = reader.number(l(f.get(b'disk')))
        self.tracknumber = reader.number(l(f.get(b'trkn')))
        self.length = int(f.info.length)
        self.bitrate = int(f.info.bitrate)

        self.musicbrainz_trackid = l(f.get(b'----:com.apple.iTunes:MusicBrainz Track Id'))
        self.genres = f.get(b'\xa9gen')

        artist = reader.Artist()
        artist.name = l(f.get(b'\xa9ART'))
        artist.sortname = l(f.get(b'soar'))
        #artist.musicbrainz_artistid = self.mp3.get('TXXX:MusicBrainz Artist Id')[0]
        self.artist = artist

        for a in f.get(b'----:com.apple.iTunes:ARTISTS', []):
            artist = reader.Artist()
            artist.name = a
            self.artists.append(artist)

        album = reader.Album()
        album.title = l(f.get(b'\xa9alb'))
        album.date = l(f.get(b'\xa9day'))
        album.country = l(f.get(b'----:com.apple.iTunes:MusicBrainz Album Release Country'))
        album.musicbrainz_albumid = l(f.get(b'----:com.apple.iTunes:MusicBrainz Album Id'))
        album.musicbrainz_releasegroupid = l(f.get(b'----:com.apple.iTunes:MusicBrainz Release Group Id'))
        album.labels = f.get(b'----:com.apple.iTunes:LABEL')
        album.albumtypes = f.get(b'----:com.apple.iTunes:MusicBrainz Album Type')
        album.albumstatus = f.get(b'----:com.apple.iTunes:MusicBrainz Album Status')

        albumartist = reader.Artist()
        albumartist.name = l(f.get(b'aART'))
        albumartist.sortname = l(f.get(b'soaa'))
        album.artist = albumartist

        self.album = album
