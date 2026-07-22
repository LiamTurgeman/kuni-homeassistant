"""Number platform for the KUNI integration."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    MAX_RUN_DURATION_MINUTES,
    MIN_RUN_DURATION_MINUTES,
)
from .coordinator import KuniDataUpdateCoordinator
from .entity import KuniEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KUNI number entities."""
    coordinator: KuniDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            KuniIntensityNumber(
                coordinator=coordinator,
                config_entry=entry,
            ),
            KuniRunDurationNumber(
                coordinator=coordinator,
                config_entry=entry,
            ),
        ]
    )


class KuniIntensityNumber(KuniEntity, NumberEntity):
    """Control the KUNI diffuser intensity."""

    _attr_name = "Intensity"
    _attr_icon = "mdi:gauge"
    _attr_native_min_value = 0
    _attr_native_max_value = 6
    _attr_native_step = 1

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the KUNI intensity control."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_key="intensity",
        )

    @property
    def native_value(self) -> float | None:
        """Return the currently reported intensity."""
        intensity = self.coordinator.data.get("intensity", {})
        reported = intensity.get("reported")

        try:
            return float(reported)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(
        self,
        value: float,
    ) -> None:
        """Set the KUNI diffuser intensity."""
        await self.coordinator.async_set_value(
            "intensity",
            int(value),
        )


class KuniRunDurationNumber(KuniEntity, NumberEntity):
    """Select the duration used by the timed-run button."""

    _attr_name = "Run duration"
    _attr_icon = "mdi:timer-cog-outline"
    _attr_native_min_value = MIN_RUN_DURATION_MINUTES
    _attr_native_max_value = MAX_RUN_DURATION_MINUTES
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the KUNI run-duration control."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_key="run_duration",
        )

    @property
    def native_value(self) -> float:
        """Return the selected run duration in minutes."""
        return float(self.coordinator.run_duration_minutes)

    async def async_set_native_value(
        self,
        value: float,
    ) -> None:
        """Store the selected run duration locally."""
        self.coordinator.run_duration_minutes = int(value)
        self.async_write_ha_state()