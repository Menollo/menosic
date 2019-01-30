from mutagenx.monkeysaudio import MonkeysAudio
from music.backend.tags import reader


class Track(reader.Track):
    filetype = 'ape'

    def __init__(self, path):
        super(Track, self).__init__(path)
        self.ape = MonkeysAudio(path)
        f = self.ape

        self.title = f.get('Title')
        self.discnumber = reader.number(f.get('Disc'))
        self.tracknumber = reader.number(f.get('Track'))
        self.length = int(f.info.length)
        #self.bitrate = int(f.info.bitrate)

        self.musicbrainz_trackid = str(f.get('Musicbrainz_Trackid'))
        self.genres = reader.item_to_list(f.get('Genre'))

        artist = reader.Artist()
        artist.name = f.get('Artist')
        artist.sortname = f.get('Artistsort')
        #artist.musicbrainz_artistid = str(f.get('Musicbrainz_Artistid'))
        self.artist = artist

        for a in reader.item_to_list(f.get('Artists')):
            artist = reader.Artist()
            artist.name = a
            self.artists.append(artist)

        album = reader.Album()
        album.title = f.get('Album')
        album.date = f.get('Originaldate') or f.get('Year')
        album.country = f.get('Releasecountry')
        album.musicbrainz_albumid = str(f.get('Musicbrainz_Albumid'))
        album.musicbrainz_releasegroupid = str(f.get('Musicbrainz_Releasegroupid'))
        album.labels = reader.item_to_list(f.get('Label'))
        album.albumtypes = reader.item_to_list(f.get('MUSICBRAINZ_ALBUMTYPE'))
        album.albumstatus = reader.item_to_list(f.get('MUSICBRAINZ_ALBUMSTATUS'))

        albumartist = reader.Artist()
        albumartist.name = f.get('Album Artist') or f.get('Albumartist')
        albumartist.sortname = f.get('Albumartistsort')
        #albumartist.musicbrainz_artistid = str(f.get('Musicbrainz_Albumartistid'))
        album.artist = albumartist

        self.album = album
