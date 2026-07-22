"""Button platform for the KUNI integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up the KUNI button entities."""
    coordinator: KuniDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            KuniStartTimedRunButton(
                coordinator=coordinator,
                config_entry=entry,
            )
        ]
    )


class KuniStartTimedRunButton(KuniEntity, ButtonEntity):
    """Start a timed KUNI diffuser run."""

    _attr_name = "Start timed run"
    _attr_icon = "mdi:timer-play-outline"

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the timed-run button."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_key="start_timed_run",
        )

    async def async_press(self) -> None:
        """Start KUNI for the selected duration."""
        await self.coordinator.async_start_timed_run()