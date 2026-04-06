"""Frontend panel registration for the Draw.io Editor integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_PANEL_URL_PATH,
    CONF_SIDEBAR_ICON,
    CONF_SIDEBAR_TITLE,
    DATA_STATIC_REGISTERED,
    INTEGRATION_VERSION,
    STATIC_MODULE_FILENAME,
    STATIC_URL_BASE,
    WEBCOMPONENT_NAME,
)
from .settings import get_feature_flags


async def async_setup_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register or update the custom panel when the feature is enabled."""
    await _async_register_static_assets(hass)

    frontend_url_path = entry.data[CONF_PANEL_URL_PATH]
    if not get_feature_flags(entry)["enable_panel"]:
        frontend.async_remove_panel(hass, frontend_url_path, warn_if_unknown=False)
        return

    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=entry.data[CONF_SIDEBAR_TITLE],
        sidebar_icon=entry.data[CONF_SIDEBAR_ICON],
        frontend_url_path=frontend_url_path,
        config={
            "_panel_custom": {
                "name": WEBCOMPONENT_NAME,
                "embed_iframe": False,
                "trust_external": False,
                "module_url": (
                    f"{STATIC_URL_BASE}/{STATIC_MODULE_FILENAME}"
                    f"?v={INTEGRATION_VERSION}"
                ),
            }
        },
        require_admin=True,
        update=True,
    )


async def async_unload_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove the custom panel."""
    frontend.async_remove_panel(
        hass,
        entry.data[CONF_PANEL_URL_PATH],
        warn_if_unknown=False,
    )


async def _async_register_static_assets(hass: HomeAssistant) -> None:
    """Register the compiled frontend bundle once."""
    if hass.data.get(DATA_STATIC_REGISTERED):
        return

    static_directory = Path(__file__).parent / "static"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                STATIC_URL_BASE,
                str(static_directory),
                cache_headers=False,
            )
        ]
    )
    hass.data[DATA_STATIC_REGISTERED] = True

