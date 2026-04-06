"""Configuration helpers for the Draw.io Editor integration."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlparse

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_EDITOR_URL,
    CONF_PANEL_URL_PATH,
    CONF_SIDEBAR_ICON,
    CONF_SIDEBAR_TITLE,
    CONF_STORAGE_PATH,
    DEFAULT_DEFAULT_DIAGRAM_PATH,
    DATA_ACTIVE_ENTRY_ID,
    DEFAULT_EDITOR_URL,
    DEFAULT_OPTIONS,
    DEFAULT_PANEL_URL_PATH,
    DEFAULT_SIDEBAR_ICON,
    DEFAULT_SIDEBAR_TITLE,
    DEFAULT_STORAGE_PATH,
    DOMAIN,
    ALLOWED_DIAGRAM_SUFFIXES,
    OPT_ENABLE_OPEN_FILE,
    OPT_ENABLE_PANEL,
    OPT_ENABLE_PNG_EXPORT,
    OPT_ENABLE_QUERY_OPEN,
    OPT_ENABLE_SAVE,
    OPT_DEFAULT_DIAGRAM_PATH,
    PNG_EXPORT_SCOPE_CURRENT_PAGE,
)


def normalize_storage_path(value: str) -> str:
    """Validate and normalize the configured storage path."""
    raw_value = value.strip().replace("\\", "/").strip("/")
    if not raw_value:
        raise ValueError("invalid_storage_path")

    normalized = PurePosixPath(raw_value)
    if normalized.is_absolute() or any(part in {"", ".", ".."} for part in normalized.parts):
        raise ValueError("invalid_storage_path")

    return normalized.as_posix()


def normalize_default_diagram_path(value: str) -> str:
    """Validate and normalize the optional default diagram path."""
    raw_value = value.strip().replace("\\", "/").strip("/")
    if not raw_value:
        return ""

    normalized = PurePosixPath(raw_value)
    if normalized.is_absolute() or any(part in {"", ".", ".."} for part in normalized.parts):
        raise ValueError("invalid_default_diagram_path")

    if normalized.suffix.lower() not in ALLOWED_DIAGRAM_SUFFIXES:
        raise ValueError("unsupported_default_extension")

    return normalized.as_posix()


def normalize_panel_url_path(value: str) -> str:
    """Validate and normalize the frontend URL path."""
    cleaned = value.strip().strip("/")
    if not cleaned or any(char in cleaned for char in ("/", "?", "#", " ")):
        raise ValueError("invalid_panel_url_path")
    return cleaned


def normalize_editor_url(value: str) -> str:
    """Validate the configured editor URL."""
    cleaned = value.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("invalid_editor_url")
    return cleaned


def normalize_sidebar_title(value: str) -> str:
    """Normalize the sidebar title."""
    cleaned = value.strip()
    return cleaned or DEFAULT_SIDEBAR_TITLE


def normalize_sidebar_icon(value: str) -> str:
    """Normalize the sidebar icon value."""
    cleaned = value.strip()
    return cleaned or DEFAULT_SIDEBAR_ICON


def build_entry_data(user_input: dict[str, Any]) -> dict[str, str]:
    """Build sanitized config entry data."""
    return {
        CONF_STORAGE_PATH: normalize_storage_path(
            str(user_input.get(CONF_STORAGE_PATH, DEFAULT_STORAGE_PATH))
        ),
        CONF_PANEL_URL_PATH: normalize_panel_url_path(
            str(user_input.get(CONF_PANEL_URL_PATH, DEFAULT_PANEL_URL_PATH))
        ),
        CONF_SIDEBAR_TITLE: normalize_sidebar_title(
            str(user_input.get(CONF_SIDEBAR_TITLE, DEFAULT_SIDEBAR_TITLE))
        ),
        CONF_SIDEBAR_ICON: normalize_sidebar_icon(
            str(user_input.get(CONF_SIDEBAR_ICON, DEFAULT_SIDEBAR_ICON))
        ),
        CONF_EDITOR_URL: normalize_editor_url(
            str(user_input.get(CONF_EDITOR_URL, DEFAULT_EDITOR_URL))
        ),
    }


def build_options(user_input: dict[str, Any]) -> dict[str, bool]:
    """Build validated feature flags."""
    options: dict[str, Any] = {
        key: bool(user_input.get(key, default_value))
        for key, default_value in DEFAULT_OPTIONS.items()
    }
    options[OPT_DEFAULT_DIAGRAM_PATH] = normalize_default_diagram_path(
        str(user_input.get(OPT_DEFAULT_DIAGRAM_PATH, DEFAULT_DEFAULT_DIAGRAM_PATH))
    )

    if options[OPT_ENABLE_SAVE] and not options[OPT_ENABLE_OPEN_FILE]:
        raise ValueError("save_requires_open")

    if options[OPT_ENABLE_QUERY_OPEN] and not options[OPT_ENABLE_OPEN_FILE]:
        raise ValueError("query_requires_open")

    if options[OPT_ENABLE_PNG_EXPORT] and not options[OPT_ENABLE_SAVE]:
        raise ValueError("png_requires_save")

    if options[OPT_DEFAULT_DIAGRAM_PATH] and not options[OPT_ENABLE_OPEN_FILE]:
        raise ValueError("default_requires_open")

    return options


def get_feature_flags(entry: ConfigEntry) -> dict[str, bool]:
    """Return the effective feature flags for an entry."""
    return {
        key: bool(entry.options.get(key, default_value))
        for key, default_value in DEFAULT_OPTIONS.items()
    }


def get_active_entry(hass: HomeAssistant) -> ConfigEntry:
    """Return the active config entry for the integration."""
    entries: dict[str, ConfigEntry] = hass.data.get(DOMAIN, {})
    active_entry_id = hass.data.get(DATA_ACTIVE_ENTRY_ID)

    if active_entry_id and active_entry_id in entries:
        return entries[active_entry_id]

    if not entries:
        raise LookupError("no_active_entry")

    return next(iter(entries.values()))


def build_runtime_config(entry: ConfigEntry) -> dict[str, Any]:
    """Build the runtime configuration returned to the frontend."""
    editor_url = entry.data[CONF_EDITOR_URL]
    parsed_editor_url = urlparse(editor_url)

    return {
        "domain": DOMAIN,
        "editor_url": editor_url,
        "editor_origin": f"{parsed_editor_url.scheme}://{parsed_editor_url.netloc}",
        "panel_url_path": entry.data[CONF_PANEL_URL_PATH],
        "sidebar_title": entry.data[CONF_SIDEBAR_TITLE],
        "sidebar_icon": entry.data[CONF_SIDEBAR_ICON],
        "storage_path": entry.data[CONF_STORAGE_PATH],
        "default_diagram_path": str(
            entry.options.get(OPT_DEFAULT_DIAGRAM_PATH, DEFAULT_DEFAULT_DIAGRAM_PATH)
        ),
        "allowed_extensions": [".drawio", ".xml"],
        "feature_flags": get_feature_flags(entry),
        "png_export": {
            "scope": PNG_EXPORT_SCOPE_CURRENT_PAGE,
            "transparent": False,
            "scale": 1,
        },
    }


def get_default_form_values() -> dict[str, Any]:
    """Return the default values shown during initial setup."""
    return {
        CONF_STORAGE_PATH: DEFAULT_STORAGE_PATH,
        CONF_PANEL_URL_PATH: DEFAULT_PANEL_URL_PATH,
        CONF_SIDEBAR_TITLE: DEFAULT_SIDEBAR_TITLE,
        CONF_SIDEBAR_ICON: DEFAULT_SIDEBAR_ICON,
        CONF_EDITOR_URL: DEFAULT_EDITOR_URL,
        OPT_DEFAULT_DIAGRAM_PATH: DEFAULT_DEFAULT_DIAGRAM_PATH,
        **DEFAULT_OPTIONS,
    }


def get_default_options_form_values(entry: ConfigEntry) -> dict[str, Any]:
    """Return the default values shown in the options flow."""
    return get_feature_flags(entry) | {
        OPT_ENABLE_PANEL: get_feature_flags(entry)[OPT_ENABLE_PANEL],
        OPT_DEFAULT_DIAGRAM_PATH: str(
            entry.options.get(OPT_DEFAULT_DIAGRAM_PATH, DEFAULT_DEFAULT_DIAGRAM_PATH)
        ),
    }
