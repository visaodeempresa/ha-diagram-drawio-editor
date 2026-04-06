"""WebSocket API for the Draw.io Editor integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DATA_WEBSOCKET_REGISTERED,
    OPT_ENABLE_OPEN_FILE,
    OPT_ENABLE_PNG_EXPORT,
    OPT_ENABLE_SAVE,
    WS_TYPE_GET_CONFIG,
    WS_TYPE_LOAD_DIAGRAM,
    WS_TYPE_SAVE_DIAGRAM,
)
from .settings import build_runtime_config, get_active_entry, get_feature_flags
from .storage import read_diagram, save_diagram


def async_setup_websocket_api(hass: HomeAssistant) -> None:
    """Register the integration WebSocket API once."""
    if hass.data.get(DATA_WEBSOCKET_REGISTERED):
        return

    websocket_api.async_register_command(hass, websocket_get_config)
    websocket_api.async_register_command(hass, websocket_load_diagram)
    websocket_api.async_register_command(hass, websocket_save_diagram)

    hass.data[DATA_WEBSOCKET_REGISTERED] = True


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): WS_TYPE_GET_CONFIG})
def websocket_get_config(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the runtime configuration used by the frontend."""
    try:
        entry = get_active_entry(hass)
    except LookupError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Draw.io Editor is not configured.",
        )
        return

    connection.send_result(msg["id"], build_runtime_config(entry))


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_LOAD_DIAGRAM,
        vol.Required("path"): str,
    }
)
@websocket_api.async_response
async def websocket_load_diagram(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Load a diagram from the configured storage root."""
    try:
        entry = get_active_entry(hass)
        _assert_feature_enabled(entry, OPT_ENABLE_OPEN_FILE)
        payload = await hass.async_add_executor_job(
            read_diagram,
            hass,
            entry,
            msg["path"],
        )
    except LookupError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Draw.io Editor is not configured.",
        )
    except FileNotFoundError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Diagram file not found.",
        )
    except ValueError as err:
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, str(err))
    except PermissionError as err:
        connection.send_error(msg["id"], websocket_api.ERR_UNKNOWN_ERROR, str(err))
    else:
        connection.send_result(msg["id"], payload)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_SAVE_DIAGRAM,
        vol.Required("path"): str,
        vol.Required("xml"): str,
        vol.Optional("png_data_uri"): vol.Any(None, str),
    }
)
@websocket_api.async_response
async def websocket_save_diagram(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Save a diagram and its sibling PNG export."""
    try:
        entry = get_active_entry(hass)
        feature_flags = get_feature_flags(entry)
        _assert_feature_enabled(entry, OPT_ENABLE_SAVE)

        png_data_uri = msg.get("png_data_uri")
        if feature_flags[OPT_ENABLE_PNG_EXPORT] and not png_data_uri:
            raise ValueError("missing_png_export")

        if not feature_flags[OPT_ENABLE_PNG_EXPORT]:
            png_data_uri = None

        payload = await hass.async_add_executor_job(
            save_diagram,
            hass,
            entry,
            msg["path"],
            msg["xml"],
            png_data_uri,
        )
    except LookupError:
        connection.send_error(
            msg["id"],
            websocket_api.ERR_NOT_FOUND,
            "Draw.io Editor is not configured.",
        )
    except ValueError as err:
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, str(err))
    except PermissionError as err:
        connection.send_error(msg["id"], websocket_api.ERR_UNKNOWN_ERROR, str(err))
    else:
        connection.send_result(msg["id"], payload)


def _assert_feature_enabled(entry: ConfigEntry, option_name: str) -> None:
    """Raise an error when the requested feature is disabled."""
    if not get_feature_flags(entry)[option_name]:
        raise ValueError(f"{option_name}_disabled")
