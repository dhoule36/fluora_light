"""Config flow for wiz_light."""
import logging

import voluptuous as vol

from homeassistant.core import callback
from homeassistant import config_entries

from .const import *




class FluoraFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WiZ Light."""

    VERSION = 1

    def __init__(self) -> None:
        self.port = None
        self.name = None
        self.hostname = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            self.port = user_input[CONF_PORT]
            self.name = user_input[CONF_NAME]
            self.hostname = user_input[CONF_HOSTNAME]

            await self.async_set_unique_id(self.hostname, raise_on_progress=False)

            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_HOSTNAME): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
                }
            ),
            errors={})