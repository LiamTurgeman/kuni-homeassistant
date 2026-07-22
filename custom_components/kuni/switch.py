"""Switch platform for the KUNI integration."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import KuniDataUpdateCoordinator
from .entity import KuniEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KUNI switch."""
    coordinator: KuniDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            KuniPowerSwitch(
                coordinator=coordinator,
                config_entry=entry,
            )
        ]
    )


class KuniPowerSwitch(KuniEntity, SwitchEntity):
    """Switch controlling the KUNI diffuser power."""

    _attr_name = None
    _attr_icon = "mdi:air-filter"

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the KUNI power switch."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_key="power",
        )

    @property
    def is_on(self) -> bool:
        """Return whether the diffuser is on."""
        power = self.coordinator.data.get("power", {})
        reported = power.get("reported", 0)

        try:
            return int(reported) > 0
        except (TypeError, ValueError):
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the diffuser on."""
        await self.coordinator.async_set_value(
            "power",
            1,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the diffuser off."""
        await self.coordinator.async_set_value(
            "power",
            0,
        )