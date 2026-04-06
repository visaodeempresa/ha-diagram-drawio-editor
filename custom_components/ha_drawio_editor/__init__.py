"""The Draw.io Editor integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DATA_ACTIVE_ENTRY_ID, DOMAIN
from .panel import async_setup_panel, async_unload_panel
from .storage import provision_bundled_samples
from .websocket_api import async_setup_websocket_api

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration namespace."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Draw.io Editor from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry
    hass.data[DATA_ACTIVE_ENTRY_ID] = entry.entry_id

    await hass.async_add_executor_job(provision_bundled_samples, hass, entry)
    async_setup_websocket_api(hass)
    await async_setup_panel(hass, entry)

    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the Draw.io Editor config entry."""
    await async_unload_panel(hass, entry)

    entries: dict[str, ConfigEntry] = hass.data.get(DOMAIN, {})
    entries.pop(entry.entry_id, None)
    if not entries:
        hass.data.pop(DOMAIN, None)
        hass.data.pop(DATA_ACTIVE_ENTRY_ID, None)
    elif hass.data.get(DATA_ACTIVE_ENTRY_ID) == entry.entry_id:
        hass.data[DATA_ACTIVE_ENTRY_ID] = next(iter(entries))

    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
