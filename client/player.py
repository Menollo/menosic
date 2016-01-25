import json
from collections import OrderedDict

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

import settings

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

    def __init__(self, tracks, selected=None):
        self.tracks = OrderedDict([ (t['id'], t) for t in tracks])
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
        return "%s%s" % (settings.SERVER, self.current['original'])

    def next(self):
        try:
            self.current = next(self.playlist_iterator)
            return True
        except StopIteration:
            return False


class Player(object):
    playlist = None
    song_change_callback = None


    def __init__(self):
        Gst.init(None)

        self.player = Gst.ElementFactory.make('playbin', 'menosic')

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

        self.update_playlist()
        self.playlist.next()

        GObject.threads_init()
        self.loop = GObject.MainLoop()


    def start(self):
        self.loop.run()


    def quit(self):
        self.loop.quit()


    def update_playlist(self):
        current_id = self.playlist.current['id'] if self.playlist else None

        data = jsonurl('%s/client/%d/?token=%s' % (settings.SERVER, settings.PLAYLIST_ID, settings.CLIENT_TOKEN))
        if not self.playlist or [t['id'] for t in data['playlist']] != list(self.playlist.tracks.keys()):
            self.playlist = Playlist(data['playlist'], current_id)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("Error received from element %s: %s" % (msg.src.get_name(), err))
            print("Debugging information: %s" % debug)
        elif t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            if self.playlist.next():
                self.play()
            else:
                print("End of playlist reached..")


    def play_song(self, id):
        self.player.set_state(Gst.State.NULL)
        self.playlist.goto_track(id)
        self.play()

    def play(self):
        print("Playing: %s - %s" % (self.playlist.current['artist'], self.playlist.current['title']))
        self.player.set_property('uri', "%s?token=%s" % (self.playlist.get_current(), settings.CLIENT_TOKEN))
        self.player.set_state(Gst.State.PLAYING)
        self.song_change()

    def pause(self):
        state = self.player.get_state(10)[1]
        if state == Gst.State.PAUSED:
            self.player.set_state(Gst.State.PLAYING)
        elif state == Gst.State.PLAYING:
            self.player.set_state(Gst.State.PAUSED)
        else:
            self.play()

    def next(self):
        self.player.set_state(Gst.State.NULL)
        if self.playlist.next():
            self.play()

    def song_change(self):
        if self.song_change_callback:
            self.song_change_callback(self.playlist.current['id'])
