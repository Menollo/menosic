import json
from collections import OrderedDict

try:
    from urllib.request import urlopen
    jsonurl = lambda u: json.loads(urlopen(u).read().decode('utf-8'))
except ImportError:
    # python2 fallback
    from urllib2 import urlopen
    jsonurl = lambda u: json.load(urlopen(u))


class Playlist(object):
    tracks = []
    current = None

    def __init__(self, server, tracks, selected=None):
        self.server = server
        self.tracks = OrderedDict([(t['id'], t) for t in tracks])
        self.playlist_iterator = iter(self.tracks.values())
        self.goto_track(selected)

    def goto_track(self, id):
        # loop from the begining
        self.playlist_iterator = iter(self.tracks.values())

        if id in self.tracks.keys():
            self.next()
            while self.current['id'] != id:
                self.next()
            return True
        else:
            return False

    def get_current(self):
        return "%s%s" % (self.server, self.current['mp3'])

    def next(self):
        try:
            self.current = next(self.playlist_iterator)
            return True
        except StopIteration:
            return False


class Player(object):
    playlist = None

    def __init__(self, hass, config, device, song_change_callback):
        self.hass = hass
        self.config = config
        self.device = device
        self.song_change_callback = song_change_callback

        hass.bus.listen('state_changed', self.hass_event)

        try:
            self.update_playlist()
        except:
            print('error retrieving playlist...')
        else:
            self.playlist.next()

    def hass_event(self, event):
        if (
                event.data['entity_id'] == self.device and
                event.data['old_state'].state == 'playing' and
                event.data['new_state'].state == 'idle'):
            if self.playlist.next():
                self.play()

    def update_playlist(self):
        current_id = self.playlist.current['id'] if self.playlist else None

        data = jsonurl('{server}/client/{playlist_id}/?token={client_token}'.format(**self.config))
        if not self.playlist or [t['id'] for t in data['playlist']] != list(self.playlist.tracks.keys()):
            self.playlist = Playlist(self.config['server'], data['playlist'], current_id)

    def play_song(self, id):
        self.playlist.goto_track(id)
        self.play()

    def play(self):
        print("Playing: %s - %s" % (self.playlist.current['artist'], self.playlist.current['title']))

        url = "%s?token=%s" % (self.playlist.get_current(), self.config['client_token'])
        data = {
            'entity_id': self.device,
            'media_content_id': url,
            'media_content_type': 'music',
        }

        self.hass.services.call('media_player', 'play_media', data)
        self.song_change()

    def pause(self):
        data = {
            'entity_id': self.device,
        }
        self.hass.services.call('media_player', 'media_play_pause', data)

    def next(self):
        if self.playlist.next():
            self.play()

    def song_change(self):
        self.song_change_callback(self.device, self.playlist.current['id'])
