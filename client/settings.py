SERVER = 'http://127.0.0.1:8000'
WS_SERVER = 'ws://127.0.0.1:8001'
CLIENT_TOKEN = '1'
PLAYLIST_ID = 1
DEBUG = False

# try to import local_settings for overrides
try:
    from local_settings import *
except ImportError:
    pass
