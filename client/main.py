import json
import random
import ssl
import string
import threading
import time
import websocket

import settings
from player import Player


class WebsocketPlayerControl(object):

    def __init__(self, player, server=settings.WS_SERVER):
        websocket.enableTrace(settings.DEBUG)
        rand_chars = string.ascii_uppercase + string.digits
        self.player_id = ''.join(random.choice(rand_chars) for _ in range(10))
        self.player = player
        self.ws = websocket.WebSocketApp(server,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error)

        player.song_change_callback = self.song_change

    def song_change(self, identifier):
        data = {
            'action': 'song_change',
            'player': self.player_id,
            'key': settings.CLIENT_TOKEN,
            'playlist': settings.PLAYLIST_ID,
            'identifier': identifier
            }
        self.ws.send(json.dumps(data))

    def start(self):
        while True:
            if settings.DEBUG:
                print('opening websocket connection...')
            sslopt = {"cert_reqs": ssl.CERT_NONE}
            self.ws.run_forever(ping_interval=60, sslopt=sslopt)
            time.sleep(10)

    def quit(self):
        self.ws.send("client disconnect")
        self.ws.close()

    def on_open(self, ws):
        try:
            name = settings.CLIENT_NAME
        except AttributeError:
            name = 'Client'

        data = {
            'action': 'register',
            'player': self.player_id,
            'key': settings.CLIENT_TOKEN,
            'playlist': settings.PLAYLIST_ID,
            'name': name
            }
        ws.send(json.dumps(data))

    def on_message(self, ws, message):
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

    def on_error(self, ws, error):
        print(error)


def main():
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


if __name__ == "__main__":
    main()
