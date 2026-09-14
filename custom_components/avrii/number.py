from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        AvriiRegisterNumber(
            coordinator,
            name="Maksymalna moc ładowania akumulatora",
            unique="reg_8472",
            address=8472,
            min_value=0,
            max_value=10000,
            step=100,
            unit="W",
        ),
        AvriiRegisterNumber(
            coordinator,
            name="Pojemność końcowa rozładowania akumulatora",
            unique="reg_8475",
            address=8475,
            min_value=10,
            max_value=100,
            step=1,
            unit="%",
        ),
        AvriiRegisterNumber(
            coordinator,
            name="Maksymalna moc oddawania do sieci",
            unique="reg_12473",
            address=12473,
            min_value=0,
            max_value=10000,
            step=100,
            unit="W",
        ),
    ]

    async_add_entities(entities)


class AvriiRegisterNumber(CoordinatorEntity, NumberEntity):

    def __init__(self, coordinator, name, unique, address, min_value, max_value, step, unit):
        super().__init__(coordinator)

        self._attr_name = name
        self._attr_unique_id = f"{coordinator.host}_{unique}"

        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_mode = "slider"

        self._address = address
        self._data_key = unique

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable"
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._data_key)

    async def async_set_native_value(self, value: float):
        await self.coordinator.async_write(self._address, int(value))
        self.coordinator.data[self._data_key] = int(value)
        self.async_write_ha_state()