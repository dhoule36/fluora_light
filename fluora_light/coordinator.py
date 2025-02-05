import asyncio
import datetime as dt
from enum import StrEnum
import socket

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT
)
from homeassistant.helpers import device_registry, event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import *


def scale_number(value, old_min, old_max, new_min, new_max):
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min


def calculate_brightness_hex(desired_brightness):
    return scale_number((desired_brightness ** 0.1) - 1, 0, 100 ** 0.1 - 1, 3932160, 4160442)


class LightState(StrEnum):
    """dim of the light 0-100%"""
    BRIGHTNESS = ATTR_BRIGHTNESS
    """power true or false"""
    POWER = "power"
    """set the effect"""
    EFFECT = ATTR_EFFECT


class LightCoordinator(DataUpdateCoordinator):
    _fast_poll_count = 0
    _normal_poll_interval = 60
    _fast_poll_interval = 10
    _initialized = False
    _request_status_update = True
    _unsub_update_state: event.CALLBACK_TYPE | None = None
    _concurent_update_state = 0

    def __init__(self, hass, device_id, conf):
        self.name = conf[CONF_NAME]
        self.device_name = self.name
        self.device_id = device_id
        self.hostname = conf[CONF_HOSTNAME]
        self.port = conf[CONF_PORT]
        self._normal_poll_interval = 300
        self._fast_poll_interval = 5

        """Initialize coordinator parent"""
        super().__init__(
            hass,
            LOGGER,
            name="Fluora Light: " + self.name,
            # let's give at least 30 seconds for initial connect to device
            update_interval=dt.timedelta(seconds=30),
            update_method=self.async_update,
        )
        self.ip_address = "0.0.0.0"
        self.light_socket = None

        # Initialize state in case of new integration
        self.data = dict()
        # init to 255 since that's HA's representation of it
        self.data[LightState.BRIGHTNESS] = 255
        self.data[LightState.POWER] = True
        self.data[LightState.EFFECT] = EFFECT_AUTO

    def _set_poll_mode(self, fast: bool):
        self._fast_poll_count = 0 if fast else -1
        interval = self._fast_poll_interval if fast else self._normal_poll_interval
        self.update_interval = dt.timedelta(seconds=interval)
        self._schedule_refresh()

    def _update_poll(self):
        if self._fast_poll_count > -1:
            self._fast_poll_count += 1
            if self._fast_poll_count > 1:
                self._set_poll_mode(fast=False)

    async def _disconnect(self):
        await self.light_socket.close()

    async def async_update(self):
        if not self._initialized:
            await self._initialize()
        return self.data

    async def _initialize(self):
        try:
            # resolve the ip address from the hostname if possible
            self.ip_address = socket.gethostbyname(self.hostname)

            # setup and connect the socket for communication with the light
            self.light_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.light_socket.settimeout(5)
            self.light_socket.connect((self.ip_address, self.port))
            self.light_socket.settimeout(None)
            self._initialized = True

            # set mode to auto when initializing
            self.light_socket.send(bytearray.fromhex(AUTO_HEX))
            self.state[LightState.EFFECT] = EFFECT_AUTO

            LOGGER.info("async_update_state: %s - %s", LightState.EFFECT, EFFECT_AUTO)

            self.async_set_updated_data(self.state)
            self._set_poll_mode(fast=True)

            reg = device_registry.async_get(self.hass)
            reg.async_update_device(
                self.hostname,
                name=self.name,
                manufacturer="Fluora",
                hw_version="1",
            )
        except Exception as e:
            LOGGER.warning("Failed to initialize %s: %s", self.ip_address, str(e))

    @property
    def state(self) -> dict:
        return self.data

    async def async_update_state(self, key: LightState, value) -> bool:
        return await self._async_update_state(key, value)

    async def _async_update_state_debounced(self, date, key: LightState, value) -> bool:
        self._unsub_update_state = None
        self._concurent_update_state = 0
        LOGGER.debug(
            "_async_update_state_debounced date:%s, %s - %s", date, key, value
        )
        return await self._async_update_state(key, value)

    async def _async_update_state(self, key: LightState, value) -> bool:
        self._request_status_update = True

        if not self._initialized:
            await self._initialize()

        # Write data back
        if key == LightState.BRIGHTNESS:
            # convert brightness from HA's 0-255 interpretation to our 0-100
            desired_brightness = round(value * 100 / 255)
            brightness_hex = calculate_brightness_hex(desired_brightness)
            self.light_socket.send(bytearray.fromhex(BRIGHTNESS_HEX_FIRST + hex(int(brightness_hex))[2:] + BRIGHTNESS_HEX_LAST))
            LOGGER.info(f"Setting Brightness {desired_brightness}")
        # compiled all color, scene, and mode changing into the EFFECT to make it easier
        elif key == LightState.EFFECT:
            # check if it is a scene effect. If so, set the mode to scene and then set the specific scene
            if value in SCENE_EFFECTS:
                self.light_socket.send(bytearray.fromhex(SCENE_HEX))
                await asyncio.sleep(0.1)
                self.light_socket.send(bytearray.fromhex(SCENE_HEX_DICT[value]))
                LOGGER.info(f"Setting SCENE: {value}")
            # check if it is 'auto' effect, and then change to auto mode
            elif value == EFFECT_AUTO:
                self.light_socket.send(bytearray.fromhex(AUTO_HEX))
                LOGGER.info(f"Setting MODE: {value}")
            # if "White" is chosen, we need to set the saturation to 0, but don't need to change colors, also set to manual mode
            elif value == EFFECT_WHITE:
                self.light_socket.send(bytearray.fromhex(MANUAL_HEX))
                await asyncio.sleep(0.1)
                self.light_socket.send(bytearray.fromhex(MIN_SATURATION_HEX))
                LOGGER.info(f"Setting light to white")
            # finally check for color effects, where we need to set manual mode, set saturation to 100 and then set color
            elif value in COLOR_EFFECTS:
                self.light_socket.send(bytearray.fromhex(MANUAL_HEX))
                await asyncio.sleep(0.1)
                self.light_socket.send(bytearray.fromhex(MAX_SATURATION_HEX))
                await asyncio.sleep(0.1)
                self.light_socket.send(bytearray.fromhex(SCENE_HEX_DICT[value]))
                LOGGER.info(f"Setting color: {value}")
        elif key == LightState.POWER:
            if value:
                self.light_socket.send(bytearray.fromhex(POWER_ON_HEX))
            else:
                self.light_socket.send(bytearray.fromhex(POWER_OFF_HEX))
        else:
            return False

        self.state[key] = value

        LOGGER.info("async_update_state: %s - %s", key, value)

        self.async_set_updated_data(self.state)
        self._set_poll_mode(fast=True)

        return True