"""Menosic component for Home Assistant"""
import threading
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .controller import Controller

DOMAIN = "menosic"
PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required('server'): cv.string,
        vol.Required('ws_server'): cv.string,
        vol.Required('client_token'): cv.string,
        vol.Required('playlist_id'): cv.positive_int,
    },
)


def setup(hass, config):
    """Set up the Menosic platform."""

    config = config[DOMAIN][0]

    controller = Controller(hass, config)
    controller_thread = threading.Thread(
            name='controller',
            target=controller.start)
    controller_thread.start()

    return True
