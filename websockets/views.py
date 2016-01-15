from django.contrib.auth.models import User
import tornado.websocket
import json

class Client(object):
    name = 'Unknown'
    key = None
    player = None
    playlist = None
    _user = None

    @property
    def user(self):
        if not self._user:
            self._user = User.objects.get(id=self.key)
        return self._user

    @property
    def allowed_users(self):
        return [ self.user, ]


class TestWebSocket(tornado.websocket.WebSocketHandler):
    clients = {}

    def check_origin(self, origin):
        return True

    def open(self):
        self.clients[self] = Client()

    def on_close(self):
        user = self.clients[self].user
        del self.clients[self]

        for obj, client in self.clients.items():
            if user in client.allowed_users:
                self.update_client_players(obj)

    def on_message(self, message):
        try:
            data = json.loads(message)  

            if hasattr(self, data.get('action')):
                print('message received: ', data)
                getattr(self, data['action'])(data)
            else:
                print('unknown action:', data.get('action'))
        except json.decoder.JSONDecodeError:
            print('no json received')


    def register(self, data):
        self.clients[self].key = data['key']
        self.clients[self].name = data['name']
        self.clients[self].player = data['player']
        self.clients[self].playlist = int(data['playlist'])

        user = self.clients[self].user
        for obj, client in self.clients.items():
            if user in client.allowed_users:
                self.update_client_players(obj)


    def update_client_players(self, obj):
        user = self.clients[obj].user
        clients = []
        for client in self.clients.values():
            if user in client.allowed_users:
                clients.append(client)

        response = {'action': 'players', 'players': [{'player': client.player, 'name': client.name, 'user': client.user.username} for client in clients ]}
        obj.write_message(json.dumps(response))


    def players(self, data):
        self.update_client_players(self)

    def update_playlist(self, data):
        for obj, client in self.clients.items():
            if obj not is self:
                if client.playlist == data['playlist']:
                    response = {
                            'action': 'update_playlist',
                            'playlist': data['playlist']
                        }
                    obj.write_message(json.dumps(response))

    def song_change(self, data):
        for obj, client in self.clients.items():
            if client.playlist == data['playlist']:
                response = {
                        'action': data['action'],
                        'player': data['player'],
                        'playlist': data['playlist'],
                        'identifier': data['identifier'],
                    }
                obj.write_message(json.dumps(response))

    def play_song(self, data):
        for obj, client in self.clients.items():
            if client.player == data['player']:
                response = {
                        'action': data['action'],
                        'player': data['player'],
                        'playlist': data['playlist'],
                        'identifier': data['identifier'],
                    }
                obj.write_message(json.dumps(response))


    def _player_action(self, data):
        for obj, client in self.clients.items():
            if client.player == data['player']:
                response = {'action': data['action'], 'player': data['player']}
                obj.write_message(json.dumps(response))

    play = _player_action
    pause = _player_action
    next = _player_action
    previous = _player_action
