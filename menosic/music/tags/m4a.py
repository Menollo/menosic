from mutagenx.mp4 import MP4
from music import tags

l = tags.list_to_item

class Track(tags.Track):
    filetype = 'm4a'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.m4a = MP4(path)
        f = self.m4a

        self.title = l(f.get(b'\xa9nam'))
        self.discnumber = l(f.get(b'disk'))[0]
        self.tracknumber = l(f.get(b'trkn'))[0]
        self.length = int(f.info.length)
        self.bitrate = int(f.info.bitrate)

        self.musicbrainz_trackid = l(f.get(b'----:com.apple.iTunes:MusicBrainz Track Id'))
        self.genres = f.get(b'\xa9gen')

        artist = tags.Artist()
        artist.name = l(f.get(b'\xa9ART'))
        artist.sortname = l(f.get(b'soar'))
        #artist.musicbrainz_artistid = self.mp3.get('TXXX:MusicBrainz Artist Id')[0]
        self.artists.append(artist)

        album = tags.Album()
        album.title = l(f.get(b'\xa9alb'))
        album.date = l(f.get(b'\xa9day'))
        album.country = l(f.get(b'----:com.apple.iTunes:MusicBrainz Album Release Country'))
        album.musicbrainz_albumid = l(f.get(b'----:com.apple.iTunes:MusicBrainz Album Id'))
        album.musicbrainz_releasegroupid = l(f.get(b'----:com.apple.iTunes:MusicBrainz Release Group Id'))
        album.labels = f.get(b'----:com.apple.iTunes:LABEL')
        album.albumtypes = f.get(b'----:com.apple.iTunes:MusicBrainz Album Type')
        album.albumstatus = f.get(b'----:com.apple.iTunes:MusicBrainz Album Status')

        albumartist = tags.Artist()
        albumartist.name = l(f.get(b'aART'))
        albumartist.sortname = l(f.get(b'soaa'))
        album.albumartists.append(albumartist)

        self.album = album
