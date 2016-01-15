import traceback
import threading
import websocket
import time
import sys
import json

import settings
from player import Player

class WebsocketPlayerControl(object):

    def __init__(self, player, server=settings.WS_SERVER):
        self.player_id = 'client'
        self.player = player
        self.ws = websocket.WebSocketApp(server,
                              on_message = self.on_message,
                              on_error = self.on_error)
        
        player.song_change_callback = self.song_change
        self.ws.on_open = self.on_open

    def song_change(self, identifier):
        data = {'action':'song_change', 'player': self.player_id, 'key': settings.CLIENT_TOKEN,  'playlist': settings.PLAYLIST_ID, 'identifier': identifier}
        self.ws.send(json.dumps(data))

    def start(self):
        self.ws.run_forever()

    def quit(self):
        self.ws.send("client disconnect")
        self.ws.close()

    def on_open(self, ws):
        data = {'action':'register', 'player': self.player_id, 'key': settings.CLIENT_TOKEN, 'playlist': settings.PLAYLIST_ID}
        ws.send(json.dumps(data))

    def on_message(self, ws, message):
        print(message)
        data = json.loads(message)

        if data['action'] == 'play':
            self.player.play()
        elif data['action'] == 'pause':
            self.player.pause()
        elif data['action'] == 'update playlist':
            self.player.update_playlist()
        elif data['action'] == 'next':
            self.player.next()
        elif data['action'] == 'play_song':
            self.player.play_song(data['identifier'])

    def on_error(self, ws, error):
        print(error)


if __name__ == "__main__":

    player = Player()
    ws = WebsocketPlayerControl(player)
    
    ws_thread = threading.Thread(name='ws', target=ws.start)

    try:
        ws_thread.start()
        player.start()
    except KeyboardInterrupt:
        player.quit()
        ws.quit()
        ws_thread.join()
