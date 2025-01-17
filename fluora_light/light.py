"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA,
                                            LightEntity)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]
    username = config[CONF_USERNAME]
    password = config.get(CONF_PASSWORD)

    # TODO add check that light is connected by pinging
    # Setup connection with devices/cloud
    #hub = awesomelights.Hub(host, username, password)

    # Add devices
    # TODO figure out what a "light" object is for messaging, maybe socket?
    add_entities(FluoraLight())


class FluoraLight(LightEntity):
    """Representation of a Fluora Light."""

    def __init__(self) -> None:
        """Initialize a FluoraLight."""
        self._light = "light"
        self._name = "fluora light"
        self._state = None
        self._brightness = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        # TODO for now just return test name
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        # TODO return the ping result to see if it is connected
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.
        """
        # TODO add socket message to turn the light on
        pass
        # self._light.brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        # self._light.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        # TODO add socket command to turn the light off
        pass
        #self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # TODO add a request for update from fluora here and decode
        pass