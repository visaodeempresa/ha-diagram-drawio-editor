"""Config flow for the Draw.io Editor integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlowWithReload

from .const import (
    CONF_EDITOR_URL,
    CONF_PANEL_URL_PATH,
    CONF_SIDEBAR_ICON,
    CONF_SIDEBAR_TITLE,
    CONF_STORAGE_PATH,
    DOMAIN,
    ENTRY_TITLE,
    OPT_ENABLE_OPEN_FILE,
    OPT_ENABLE_PANEL,
    OPT_ENABLE_PNG_EXPORT,
    OPT_ENABLE_QUERY_OPEN,
    OPT_ENABLE_SAVE,
)
from .settings import build_entry_data, build_options, get_default_form_values, get_feature_flags


def _build_user_schema(values: dict[str, Any]) -> vol.Schema:
    """Build the initial config flow form schema."""
    return vol.Schema(
        {
            vol.Required(CONF_STORAGE_PATH, default=values[CONF_STORAGE_PATH]): str,
            vol.Required(CONF_PANEL_URL_PATH, default=values[CONF_PANEL_URL_PATH]): str,
            vol.Required(CONF_SIDEBAR_TITLE, default=values[CONF_SIDEBAR_TITLE]): str,
            vol.Required(CONF_SIDEBAR_ICON, default=values[CONF_SIDEBAR_ICON]): str,
            vol.Required(CONF_EDITOR_URL, default=values[CONF_EDITOR_URL]): str,
            vol.Required(OPT_ENABLE_PANEL, default=values[OPT_ENABLE_PANEL]): bool,
            vol.Required(
                OPT_ENABLE_OPEN_FILE, default=values[OPT_ENABLE_OPEN_FILE]
            ): bool,
            vol.Required(
                OPT_ENABLE_QUERY_OPEN, default=values[OPT_ENABLE_QUERY_OPEN]
            ): bool,
            vol.Required(OPT_ENABLE_SAVE, default=values[OPT_ENABLE_SAVE]): bool,
            vol.Required(
                OPT_ENABLE_PNG_EXPORT, default=values[OPT_ENABLE_PNG_EXPORT]
            ): bool,
        }
    )


def _build_options_schema(values: dict[str, Any]) -> vol.Schema:
    """Build the options flow form schema."""
    return vol.Schema(
        {
            vol.Required(OPT_ENABLE_PANEL, default=values[OPT_ENABLE_PANEL]): bool,
            vol.Required(
                OPT_ENABLE_OPEN_FILE, default=values[OPT_ENABLE_OPEN_FILE]
            ): bool,
            vol.Required(
                OPT_ENABLE_QUERY_OPEN, default=values[OPT_ENABLE_QUERY_OPEN]
            ): bool,
            vol.Required(OPT_ENABLE_SAVE, default=values[OPT_ENABLE_SAVE]): bool,
            vol.Required(
                OPT_ENABLE_PNG_EXPORT, default=values[OPT_ENABLE_PNG_EXPORT]
            ): bool,
        }
    )


class DrawioEditorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Draw.io Editor integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        values = get_default_form_values()
        if user_input is not None:
            values = values | user_input
            try:
                entry_data = build_entry_data(user_input)
                entry_options = build_options(user_input)
            except ValueError as err:
                errors["base"] = str(err)
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=ENTRY_TITLE,
                    data=entry_data,
                    options=entry_options,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_user_schema(values),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return DrawioEditorOptionsFlow(config_entry)


class DrawioEditorOptionsFlow(OptionsFlowWithReload):
    """Handle Draw.io Editor options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage feature flag updates."""
        errors: dict[str, str] = {}
        values = get_feature_flags(self.config_entry)

        if user_input is not None:
            values = values | user_input
            try:
                options = build_options(user_input)
            except ValueError as err:
                errors["base"] = str(err)
            else:
                return self.async_create_entry(data=options)

        return self.async_show_form(
            step_id="init",
            data_schema=_build_options_schema(values),
            errors=errors,
        )

