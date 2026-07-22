"""Config flow for the KUNI integration."""

from __future__ import annotations

import logging
from typing import Any, Mapping

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import KuniApiClient, KuniApiError, KuniAuthError
from .const import (
    CONF_CLIENT_ID,
    CONF_DEVICE_ID,
    CONF_ORGANIZATION_ID,
    CONF_REFRESH_TOKEN,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Required(CONF_REFRESH_TOKEN): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD,
                autocomplete="current-password",
            )
        ),
        vol.Required(CONF_ORGANIZATION_ID): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Required(CONF_DEVICE_ID): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REFRESH_TOKEN): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD,
                autocomplete="current-password",
            )
        )
    }
)


class KuniConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for KUNI."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = KuniApiClient(
                client_id=user_input[CONF_CLIENT_ID],
                refresh_token=user_input[CONF_REFRESH_TOKEN],
                organization_id=user_input[CONF_ORGANIZATION_ID],
                device_id=user_input[CONF_DEVICE_ID],
            )

            try:
                await self.hass.async_add_executor_job(client.get_status)

            except KuniAuthError:
                errors["base"] = "invalid_auth"

            except KuniApiError:
                errors["base"] = "cannot_connect"

            except Exception:
                _LOGGER.exception(
                    "Unexpected error while connecting to KUNI"
                )
                errors["base"] = "unknown"

            else:
                await self.async_set_unique_id(
                    user_input[CONF_DEVICE_ID]
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="KUNI Diffuser",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, Any],
    ) -> FlowResult:
        """Start reauthentication after an authentication failure."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Validate and save a replacement refresh token."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            refresh_token = user_input[CONF_REFRESH_TOKEN]

            client = KuniApiClient(
                client_id=entry.data[CONF_CLIENT_ID],
                refresh_token=refresh_token,
                organization_id=entry.data[CONF_ORGANIZATION_ID],
                device_id=entry.data[CONF_DEVICE_ID],
            )

            try:
                await self.hass.async_add_executor_job(client.get_status)

            except KuniAuthError:
                errors["base"] = "invalid_auth"

            except KuniApiError:
                errors["base"] = "cannot_connect"

            except Exception:
                _LOGGER.exception(
                    "Unexpected error while reauthenticating KUNI"
                )
                errors["base"] = "unknown"

            else:
                await self.async_set_unique_id(
                    entry.data[CONF_DEVICE_ID]
                )
                self._abort_if_unique_id_mismatch()

                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_REFRESH_TOKEN: refresh_token,
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            errors=errors,
        )
