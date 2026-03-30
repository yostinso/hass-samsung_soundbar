"""Tests for Samsung Soundbar config flow."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResultType

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.samsung_soundbar.const import (
  DOMAIN,
  DEFAULT_NAME,
  DEFAULT_PORT,
  DEFAULT_MAX_VOLUME,
  DEFAULT_POWER_OPTIONS,
  CONF_PORT,
  CONF_MAX_VOLUME,
  CONF_POWER_OPTIONS,
)


USER_INPUT = {
  CONF_HOST: "192.168.1.100",
  CONF_NAME: "Living Room Soundbar",
  CONF_PORT: DEFAULT_PORT,
  CONF_MAX_VOLUME: int(DEFAULT_MAX_VOLUME),
  CONF_POWER_OPTIONS: DEFAULT_POWER_OPTIONS,
}


async def test_user_flow_shows_form(hass):
  """Test that the user flow shows a form on first step."""
  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={"source": config_entries.SOURCE_USER}
  )
  assert result["type"] == FlowResultType.FORM
  assert result["step_id"] == "user"
  assert result["errors"] == {}


async def test_user_flow_success(hass):
  """Test a successful user setup flow creates a config entry."""
  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={"source": config_entries.SOURCE_USER}
  )

  with patch(
    "custom_components.samsung_soundbar.config_flow.MultiRoomApi.get_speaker_name",
    new_callable=AsyncMock,
    return_value=["My Soundbar"],
  ):
    result = await hass.config_entries.flow.async_configure(
      result["flow_id"], USER_INPUT
    )

  assert result["type"] == FlowResultType.CREATE_ENTRY
  assert result["title"] == USER_INPUT[CONF_NAME]
  assert result["data"][CONF_HOST] == USER_INPUT[CONF_HOST]
  assert result["data"][CONF_PORT] == USER_INPUT[CONF_PORT]
  assert result["data"][CONF_MAX_VOLUME] == USER_INPUT[CONF_MAX_VOLUME]
  assert result["data"][CONF_POWER_OPTIONS] == USER_INPUT[CONF_POWER_OPTIONS]


async def test_user_flow_cannot_connect(hass):
  """Test that a connection failure shows an error and re-displays the form."""
  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={"source": config_entries.SOURCE_USER}
  )

  with patch(
    "custom_components.samsung_soundbar.config_flow.MultiRoomApi.get_speaker_name",
    new_callable=AsyncMock,
    return_value=None,
  ):
    result = await hass.config_entries.flow.async_configure(
      result["flow_id"], USER_INPUT
    )

  assert result["type"] == FlowResultType.FORM
  assert result["step_id"] == "user"
  assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_duplicate_device(hass):
  """Test that configuring a duplicate host aborts with already_configured."""
  entry = MockConfigEntry(
    domain=DOMAIN,
    unique_id=USER_INPUT[CONF_HOST],
    data={CONF_HOST: USER_INPUT[CONF_HOST]},
  )
  entry.add_to_hass(hass)

  result = await hass.config_entries.flow.async_init(
    DOMAIN, context={"source": config_entries.SOURCE_USER}
  )

  with patch(
    "custom_components.samsung_soundbar.config_flow.MultiRoomApi.get_speaker_name",
    new_callable=AsyncMock,
    return_value=["My Soundbar"],
  ):
    result = await hass.config_entries.flow.async_configure(
      result["flow_id"], USER_INPUT
    )

  assert result["type"] == FlowResultType.ABORT
  assert result["reason"] == "already_configured"
