"""Base entity for the KUNI integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import KuniDataUpdateCoordinator


class KuniEntity(CoordinatorEntity[KuniDataUpdateCoordinator]):
    """Base class for all KUNI entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_key: str,
    ) -> None:
        """Initialize a KUNI entity."""
        super().__init__(coordinator)

        device_id = config_entry.data[CONF_DEVICE_ID]

        self._attr_unique_id = f"{device_id}_{entity_key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="KUNI Diffuser",
            manufacturer="KUNI",
            model="Wi-Fi Scent Diffuser",
        )