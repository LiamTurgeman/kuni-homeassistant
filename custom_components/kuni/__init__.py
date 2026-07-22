"""KUNI diffuser integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import KuniApiClient
from .const import (
    CONF_CLIENT_ID,
    CONF_DEVICE_ID,
    CONF_ORGANIZATION_ID,
    CONF_REFRESH_TOKEN,
    PLATFORMS,
)
from .coordinator import KuniDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up KUNI from a config entry."""
    client = KuniApiClient(
        client_id=entry.data[CONF_CLIENT_ID],
        refresh_token=entry.data[CONF_REFRESH_TOKEN],
        organization_id=entry.data[CONF_ORGANIZATION_ID],
        device_id=entry.data[CONF_DEVICE_ID],
    )

    coordinator = KuniDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
        client=client,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a KUNI config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )