from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Event
from .coordinator import LightCoordinator

from .const import *
import logging

LOGGER = logging.getLogger(__name__)
PLATFORMS = ["light"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    LOGGER.debug("Config Entry Setup started")

    hass.data.setdefault(DOMAIN, {})
    # setup a since coordinator for the device
    hass.data[DOMAIN][entry.entry_id] = LightCoordinator(hass, entry.entry_id, entry.data)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    instance = hass.data[DOMAIN][entry.entry_id]
    if entry.title != instance.name:
        await hass.config_entries.async_reload(entry.entry_id)