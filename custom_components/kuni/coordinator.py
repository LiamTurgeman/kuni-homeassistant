"""Data coordinator for the KUNI integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import KuniApiClient, KuniApiError, KuniAuthError
from .const import (
    DEFAULT_RUN_DURATION_MINUTES,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class KuniDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, dict[str, Any]]]
):
    """Coordinate updates from the KUNI cloud API."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: KuniApiClient,
    ) -> None:
        """Initialize the KUNI coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=DEFAULT_SCAN_INTERVAL,
            always_update=False,
        )

        self.client = client

        # Local Home Assistant setting used by the timed-run button.
        self.run_duration_minutes = DEFAULT_RUN_DURATION_MINUTES

    async def _async_update_data(
        self,
    ) -> dict[str, dict[str, Any]]:
        """Fetch the latest KUNI device state."""
        try:
            return await self.hass.async_add_executor_job(
                self.client.get_status
            )

        except KuniAuthError as exc:
            raise ConfigEntryAuthFailed(
                "KUNI authentication failed"
            ) from exc

        except KuniApiError as exc:
            raise UpdateFailed(
                f"Could not update KUNI data: {exc}"
            ) from exc

    async def async_set_value(
        self,
        name: str,
        value: Any,
    ) -> None:
        """Update a KUNI property and refresh its state."""
        try:
            await self.hass.async_add_executor_job(
                self.client.set_value,
                name,
                value,
            )

        except KuniAuthError as exc:
            raise ConfigEntryAuthFailed(
                "KUNI authentication failed"
            ) from exc

        except KuniApiError as exc:
            raise UpdateFailed(
                f"Could not update KUNI property {name}: {exc}"
            ) from exc

        await self.async_request_refresh()

    async def async_start_timed_run(self) -> None:
        """Start KUNI for the selected duration."""
        seconds = int(self.run_duration_minutes * 60)

        await self.async_set_value(
            "power",
            seconds,
        )