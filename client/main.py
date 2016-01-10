import traceback
import threading
import websocket
import time
import sys

import settings
from player import Player

class WebsocketPlayerControl(object):

    def __init__(self, player, server=settings.WS_SERVER):
        self.ws = websocket.WebSocketApp("%s/ws/player_%d?subscribe-broadcast&publish-broadcast" % (server, settings.PLAYER_ID),
                              on_message = self.on_message,
                              on_error = self.on_error)
        
        self.player = player
        self.ws.on_open = self.on_open

    def start(self):
        self.ws.run_forever()

    def quit(self):
        self.ws.send("client disconnect")
        self.ws.close()

    def on_open(self, ws):
        ws.send('client connected')

    def on_message(self, ws, message):
        print(message)
        if message == 'play':
            self.player.play()
        elif message == 'pause':
            self.player.pause()
        elif message == 'update playlist':
            self.player.update_playlist()
        elif message == 'next':
            self.player.next()

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
