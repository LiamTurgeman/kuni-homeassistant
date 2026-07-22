"""Select platform for the KUNI integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import KuniDataUpdateCoordinator
from .entity import KuniEntity


CAPSULE_OPTIONS = [
    "Capsule 1",
    "Capsule 2",
    "Capsule 3",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KUNI select entities."""
    coordinator: KuniDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            KuniCapsuleSelect(
                coordinator=coordinator,
                config_entry=entry,
            )
        ]
    )


class KuniCapsuleSelect(KuniEntity, SelectEntity):
    """Select the active KUNI capsule."""

    _attr_name = "Capsule"
    _attr_icon = "mdi:scent"
    _attr_options = CAPSULE_OPTIONS

    def __init__(
        self,
        coordinator: KuniDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the KUNI capsule selector."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            entity_key="position",
        )

    @property
    def current_option(self) -> str | None:
        """Return the currently reported capsule."""
        position = self.coordinator.data.get("position", {})
        reported = position.get("reported")

        try:
            position_number = int(reported)
        except (TypeError, ValueError):
            return None

        if not 0 <= position_number < len(CAPSULE_OPTIONS):
            return None

        return CAPSULE_OPTIONS[position_number]

    async def async_select_option(
        self,
        option: str,
    ) -> None:
        """Select a KUNI capsule."""
        try:
            position = CAPSULE_OPTIONS.index(option)
        except ValueError as exc:
            raise ValueError(
                f"Unsupported capsule option: {option}"
            ) from exc

        await self.coordinator.async_set_value(
            "position",
            position,
        )