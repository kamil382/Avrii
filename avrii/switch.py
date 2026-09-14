from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [AvriiSwitch(coordinator, sw) for sw in coordinator.switches]
    )

class AvriiSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, swdef):
        super().__init__(coordinator)

        self._def = swdef
        self._attr_name = swdef["name"]
        self._attr_unique_id = f"{coordinator.host}_{swdef['name']}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable"
        )

    @property
    def is_on(self):
        return self.coordinator.data.get(self._def["name"], False)

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_write(
            self._def["address"],
            self._def["command_on"]
        )

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_write(
            self._def["address"],
            self._def["command_off"]
        )