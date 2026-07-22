"""Sensor platform for the KUNI integration."""

from __future__ import annotations

from datetime import datetime, timezone
import time

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import KuniDataUpdateCoordinator
from .entity import KuniEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KUNI sensor entities."""
    coordinator: KuniDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            KuniTimerEndSensor(
                coordinator=coordinator,
                config_entry=entry,
            ),
            KuniTimerRemainingSensor(
                coordinator=coordinator,
                config_entry=entry,
            ),
        ]
    )


class KuniTimerEndSensor(KuniEntity, SensorEntity):
    """Show when the current KUNI timer will end."""

    _attr_name = "Timer end"
    _attr_icon = "mdi:timer-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the KUNI timer end sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_key="timer_end",
        )

    @property
    def native_value(self) -> datetime | None:
        """Return the timer end as a timezone-aware datetime."""
        timer = self.coordinator.data.get("timer", {})
        reported = timer.get("reported", 0)

        try:
            timestamp = int(reported)
        except (TypeError, ValueError):
            return None

        if timestamp <= 0:
            return None

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )


class KuniTimerRemainingSensor(KuniEntity, SensorEntity):
    """Show how many seconds remain on the KUNI timer."""

    _attr_name = "Timer remaining"
    _attr_icon = "mdi:timer-sand"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the KUNI timer remaining sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_key="timer_remaining",
        )

    @property
    def native_value(self) -> int:
        """Return the remaining timer duration in seconds."""
        timer = self.coordinator.data.get("timer", {})
        reported = timer.get("reported", 0)

        try:
            timestamp = int(reported)
        except (TypeError, ValueError):
            return 0

        if timestamp <= 0:
            return 0

        return max(
            0,
            timestamp - int(time.time()),
        )