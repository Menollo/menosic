import json
import threading
from collections import OrderedDict
import traceback

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

import settings

try:
    from urllib.request import urlopen
    jsonurl = lambda u: json.loads(urlopen(u).readall().decode('utf-8'))
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
        return "%s%s" % (settings.SERVER_URI, self.current['mp3'])

    def next(self):
        try:
            self.current = next(self.playlist_iterator)
            return True
        except StopIteration:
            return False


class Player(object):
    playlist = None

    def __init__(self):
        Gst.init(None)
        self.player = Gst.ElementFactory.make('playbin', 'menosic')

        self.bus = self.player.get_bus()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.add_signal_watch()
        self.player.send_event(Gst.Event.new_eos())

        self.update_playlist()

    def update_playlist(self):
        current_id = self.playlist.current['id'] if self.playlist else None

        data = jsonurl('%s/client/%s/?token=%s' % (settings.SERVER_URI, settings.PLAYER_ID, settings.CLIENT_TOKEN))
        if not self.playlist or [t['id'] for t in data['playlist']] != list(self.playlist.tracks.keys()):
            self.playlist = Playlist(data['playlist'], current_id)
            if self.player.get_state != Gst.State.PLAYING:
                if self.playlist.next():
                    self.play()

    def on_eos(self, bus, msg):
        self.player.set_state(Gst.State.NULL)
        if self.playlist.next():
            self.play()


    def play(self):
        self.player.set_property('uri', "%s?token=%s" % (self.playlist.get_current(), settings.CLIENT_TOKEN))
        self.player.set_state(Gst.State.PLAYING)
        #if not self.player.set_state(Gst.State.PLAYING):
        #    raise Exception("Cannot play MP3 file! (maybe gst-plugins-ugly is not installed?)")


pl = Player()
pl.play()

loop_thread = threading.Thread(target = GObject.MainLoop().run)
loop_thread.start()

import time
while True:
    time.sleep(10)
    try:
        pl.update_playlist()
    except:
        print("Error updating playlist!")
        traceback.print_exc()
        pass
