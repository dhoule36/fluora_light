"""Base entity class for iLink Light integration."""
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LightCoordinator


class FluoraLightBaseEntity(CoordinatorEntity[LightCoordinator]):
    """Fluora Light base entity class."""

    def __init__(self, coordinator: LightCoordinator, description: EntityDescription):
        super().__init__(coordinator)

        self._attr_name = f"{self.coordinator.name} {description.name}"
        self._attr_unique_id = f"{self.coordinator.hostname}-{self.coordinator.name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.coordinator.hostname)},
        }