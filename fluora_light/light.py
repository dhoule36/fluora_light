#!/usr/bin/python

import logging
from typing import Any
import os
import time
import socket

from .constants import *

import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA,
                                            LightEntity, ATTR_HS_COLOR, SUPPORT_BRIGHTNESS, SUPPORT_COLOR, SUPPORT_EFFECT, ATTR_EFFECT)

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_IP_ADDRESS, CONF_DEVICES
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

SUPPORT_QUANTUM = SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_EFFECT

CONF_NAME = 'name'
CONF_HOSTNAME = 'hostname'
CONF_PORT = 'port'

DEFAULT_NAME = "Fluora Light"
DEFAULT_PORT = 6767

DOMAIN = "living_room_fluora"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_DEVICES, default={}): vol.Schema(
            {
                cv.string: {
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                    vol.Required(CONF_HOSTNAME): cv.string,
                    vol.Optional(CONF_PORT, default=CONF_PORT): vol.Coerce(int),
                }
            }
        ),
    }
)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    _LOGGER.info('Setting up Gree climate platform')
    devices = []
    for unique_id, device_config in config[CONF_DEVICES].items():
        name = device_config[CONF_NAME]
        hostname = device_config[CONF_HOSTNAME]
        port = device_config[CONF_PORT]
        devices.append(FluoraLight(name, hostname, port))

    # Add devices
    add_entities(devices)


def scale_number(value, old_min, old_max, new_min, new_max):
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min


def calculate_brightness_hex(desired_brightness):
    return scale_number((desired_brightness ** 0.1) - 1, 0, 100 ** 0.1 - 1, 3932160, 4160442)


class FluoraLight(LightEntity):
    """Representation of a Fluora Light."""

    def __init__(self, name: str, hostname: str, port: int) -> None:
        """Initialize a FluoraLight."""
        self._name = name
        self._hostname = hostname
        self._port = port

        # resolve the ip address from the hostname if possible
        self._ip_address = socket.gethostbyname(self._hostname)

        # setup and connect the socket for communication with the light
        self._light_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._light_socket.connect((self._ip_address, self._port))

        self._state = None
        self._brightness = None

    def ping_test(self):
        response = os.system(f"ping {self._ip_address}")
        return response == 0


    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool:
        """Return true if light is on. (just if we can communicate for now"""
        return self._state # self.ping_test()

    @property
    def effect_list(self):
        """Return the list of supported effects."""
        return EFFECT_LIST

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_QUANTUM

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.
        """
        self._light_socket.send(bytearray.fromhex(POWER_ON_HEX))
        if ATTR_HS_COLOR in kwargs:
            _LOGGER.info(f"Turn on with HS Color {kwargs[ATTR_HS_COLOR]}")
        if ATTR_BRIGHTNESS in kwargs:
            desired_brightness = kwargs[ATTR_BRIGHTNESS]
            brightness_hex = calculate_brightness_hex(desired_brightness)
            self._light_socket.send(bytearray.fromhex(BRIGHTNESS_HEX_FIRST + hex(int(brightness_hex))[2:] + BRIGHTNESS_HEX_LAST))
            _LOGGER.info(f"Turn on with Brightness {kwargs[ATTR_BRIGHTNESS]}")
        if ATTR_EFFECT in kwargs:
            self._light_socket.send(bytearray.fromhex(SCENE_HEX))
            time.sleep(1)
            self._light_socket.send(bytearray.fromhex(SCENE_HEX_DICT[kwargs[ATTR_EFFECT]]))
            _LOGGER.info(f"Turn on with SCENE {kwargs[ATTR_EFFECT]}")

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._light_socket.send(bytearray.fromhex(POWER_OFF_HEX))

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = True# self.ping_test()
