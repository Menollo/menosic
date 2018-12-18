import traceback
import threading
import websocket
import time
import sys
import json
import string
import random
import ssl

import settings
from player import Player

class WebsocketPlayerControl(object):

    def __init__(self, player, server=settings.WS_SERVER):
        websocket.enableTrace(settings.DEBUG)
        self.player_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
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
        while True:
            if settings.DEBUG:
                print('opening websocket connection...')
            self.ws.run_forever(ping_interval=60, sslopt={"cert_reqs": ssl.CERT_NONE})
            time.sleep(10)

    def quit(self):
        self.ws.send("client disconnect")
        self.ws.close()

    def on_open(self):
        try:
            name = settings.CLIENT_NAME
        except:
            name = 'client'

        data = {'action':'register', 'player': self.player_id, 'key': settings.CLIENT_TOKEN, 'playlist': settings.PLAYLIST_ID, 'name': name}
        self.ws.send(json.dumps(data))

    def on_message(self, message):
        if settings.DEBUG:
            print('message received:', message)
        data = json.loads(message)

        if data['action'] == 'play':
            self.player.play()
        elif data['action'] == 'pause':
            self.player.pause()
        elif data['action'] == 'update_playlist':
            self.player.update_playlist()
        elif data['action'] == 'next':
            self.player.next()
        elif data['action'] == 'play_song':
            self.player.play_song(data['identifier'])

    def on_error(self, error):
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
