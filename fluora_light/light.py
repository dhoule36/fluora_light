from typing import Any

from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA,
                                            LightEntity, LightEntityFeature, LightEntityDescription, SUPPORT_BRIGHTNESS, SUPPORT_COLOR, SUPPORT_EFFECT, ATTR_EFFECT, ColorMode)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant import config_entries

from .coordinator import LightCoordinator, LightState
from .entity import FluoraLightBaseEntity
from .const import *

light_description = LightEntityDescription(
    key="light",
    name="Light",
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.info('Setting up Fluora Light entry')
    # Add device
    async_add_entities([FluoraLightEntity(hass.data[DOMAIN][config_entry.entry_id], light_description)], True)


class FluoraLightEntity(FluoraLightBaseEntity, LightEntity):
    """Representation of a Fluora Light."""

    _attr_has_entity_name = True
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.EFFECT
    def __init__(self, coordinator: LightCoordinator, description: LightEntityDescription) -> None:
        """Initialize a FluoraLight."""
        super().__init__(coordinator, description)
        self.coordinator = coordinator
        self._attr_effect_list = EFFECT_LIST

    @property
    def brightness(self):
        return self.coordinator.state[LightState.BRIGHTNESS]

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        return self.coordinator.state[LightState.EFFECT]

    @property
    def is_on(self) -> bool:
        return self.coordinator.state[LightState.POWER]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """turn on"""
        if not self.is_on:
            self.coordinator.state[LightState.POWER] = True
            self.async_write_ha_state()
            await self.coordinator.async_update_state(LightState.POWER, True)

        if ATTR_BRIGHTNESS in kwargs:
            await self.coordinator.async_update_state(
                LightState.BRIGHTNESS, kwargs[ATTR_BRIGHTNESS]
            )
        if ATTR_EFFECT in kwargs:
            await self.coordinator.async_update_state(
                LightState.EFFECT, kwargs[ATTR_EFFECT]
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """turn off"""
        if self.is_on:
            self.coordinator.state[LightState.POWER] = False
            self.async_write_ha_state()
        await self.coordinator.async_update_state(LightState.POWER, False)