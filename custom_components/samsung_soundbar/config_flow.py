import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
  NumberSelector,
  NumberSelectorConfig,
  NumberSelectorMode,
)

from .const import (
  DOMAIN,
  DEFAULT_NAME,
  DEFAULT_PORT,
  DEFAULT_MAX_VOLUME,
  DEFAULT_POWER_OPTIONS,
  CONF_PORT,
  CONF_MAX_VOLUME,
  CONF_POWER_OPTIONS,
)
from .media_player import MultiRoomApi


class SamsungSoundbarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  """Handle a config flow for Samsung Soundbar."""

  VERSION = 1

  async def async_step_user(self, user_input=None):
    """Handle the initial step."""
    errors = {}

    if user_input is not None:
      host = user_input[CONF_HOST]
      port = user_input.get(CONF_PORT, DEFAULT_PORT)
      session = async_get_clientsession(self.hass)
      api = MultiRoomApi(host, port, session, self.hass)

      # Basic connectivity test
      speaker_name = await api.get_speaker_name()

      if speaker_name:
        await self.async_set_unique_id(f"{host}:{port}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
          title=user_input.get(CONF_NAME, DEFAULT_NAME),
          data=user_input,
        )
      errors["base"] = "cannot_connect"

    return self.async_show_form(
      step_id="user",
      data_schema=vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string,
        vol.Required(CONF_MAX_VOLUME, default=int(DEFAULT_MAX_VOLUME)): NumberSelector(
          NumberSelectorConfig(min=0, max=100, step=1, mode=NumberSelectorMode.SLIDER)
        ),
        vol.Required(CONF_POWER_OPTIONS, default=DEFAULT_POWER_OPTIONS): cv.boolean,
      }),
      errors=errors,
    )
