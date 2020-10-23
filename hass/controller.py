import json
import ssl
import time
import websocket

from .player import Player


class Controller(object):

    def __init__(self, hass, config):
        self.hass = hass
        self.player_config = {
                'server': config.get('server'),
                'client_token': config.get('client_token'),
                'playlist_id': config.get('playlist_id'),
            }
        self.players = {}

        self.ws = websocket.WebSocketApp(config.get('ws_server'),
                                         on_message=self.on_message,
                                         on_error=self.on_error)

        self.ws.on_open = self.on_open

    def song_change(self, device, identifier):
        data = {
            'action': 'song_change',
            'player': device,
            'key': self.player_config['client_token'],
            'playlist': self.player_config['playlist_id'],
            'identifier': identifier
            }
        self.ws.send(json.dumps(data))

    def init_players(self):
        devices = self.hass.states.entity_ids('media_player')
        for device in devices:
            self.players[device] = Player(
                    self.hass,
                    self.player_config,
                    device=device,
                    song_change_callback=self.song_change,
                )

            data = {
                'action': 'register',
                'player': device,
                'key': self.player_config['client_token'],
                'playlist': self.player_config['playlist_id'],
                'name': 'Home Assistant',
                }
            self.ws.send(json.dumps(data))

    def start(self):
        while True:
            sslopt = {"cert_reqs": ssl.CERT_NONE}
            self.ws.run_forever(ping_interval=60, sslopt=sslopt)
            time.sleep(10)

    def quit(self):
        self.ws.send("client disconnect")
        self.ws.close()

    def on_open(self):
        # wait until hass has loaded all entities
        # TODO: this can be done better without a sleep.
        time.sleep(3)
        self.init_players()

    def on_message(self, message):
        data = json.loads(message)
        player = self.players.get(data.get('player'))

        if data['action'] == 'play':
            player.play()
        elif data['action'] == 'pause':
            player.pause()
        elif data['action'] == 'update_playlist':
            if player:
                player.update_playlist()
            else:
                for player in self.players.values():
                    if player.config['playlist_id'] == data['playlist']:
                        player.update_playlist()
        elif data['action'] == 'next':
            player.next()
        elif data['action'] == 'play_song':
            player.play_song(data['identifier'])
        elif data['action'] == 'stop':
            player.stop()

    def on_error(self, error):
        print(error)
