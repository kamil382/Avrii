from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Standardowe sensory z definicji
    for s in coordinator.sensors:
        entities.append(AvriiSensor(coordinator, s))

    # Sensory sumujące fazy
    entities.append(AvriiTotalGridPower(coordinator))
    entities.append(AvriiTotalLoadPower(coordinator))
    entities.append(AvriiTotalBACKUPPower(coordinator))
    entities.append(AvriiInverterMode(coordinator))
    entities.append(AvriiSystemWorkStatusDescription(coordinator))
    entities.append(AvriiDailyEnergySensor(coordinator))
    entities.append(AvriiENERGYTotalGridExportEnergy(coordinator))
    entities.append(AvriiENERGYTotalGridInportEnergy(coordinator))
    entities.append(AvriiDziennaProdukcjaEnergiiNew(coordinator))
    
    async_add_entities(entities)


# ==========================================================
# STANDARD SENSOR
# ==========================================================
class AvriiSensor(CoordinatorEntity, SensorEntity):

    _attr_has_entity_name = True

    def __init__(self, coordinator, sdef):
        super().__init__(coordinator)

        self._sensor_key = sdef["name"]

        self._attr_name = self._sensor_key
        self._attr_unique_id = f"{coordinator.host}_{self._sensor_key}"
        self._attr_native_unit_of_measurement = sdef.get("unit_of_measurement")
        self._attr_device_class = sdef.get("device_class")
        self._attr_state_class = sdef.get("state_class", "measurement")
        self._attr_suggested_display_precision = sdef.get("precision")

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._sensor_key)


# ==========================================================
# TOTAL GRID POWER
# ==========================================================
class AvriiTotalGridPower(CoordinatorEntity, SensorEntity):

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "TOTAL watt of grid"
        self._attr_unique_id = f"{coordinator.host}_total_watt_of_grid"
        self._attr_native_unit_of_measurement = "W"
        self._attr_state_class = "measurement"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

        # automatycznie znajdź nazwy faz grid
        self._phase_keys = [
            s["name"]
            for s in coordinator.sensors
            if "watt of grid" in s["name"].lower()
        ]

        _LOGGER.debug("Grid phase keys: %s", self._phase_keys)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        total = 0.0

        for key in self._phase_keys:
            try:
                total += float(data.get(key) or 0)
            except (ValueError, TypeError):
                _LOGGER.debug("Invalid value for %s", key)

        return round(total, 2)


# ==========================================================
# TOTAL LOAD POWER
# ==========================================================
class AvriiTotalLoadPower(CoordinatorEntity, SensorEntity):

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "TOTAL watt of load"
        self._attr_unique_id = f"{coordinator.host}_total_watt_of_load"
        self._attr_native_unit_of_measurement = "W"
        self._attr_state_class = "measurement"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

        # automatycznie znajdź nazwy faz load
        self._phase_keys = [
            s["name"]
            for s in coordinator.sensors
            if "watt of load" in s["name"].lower()
        ]

        _LOGGER.debug("Load phase keys: %s", self._phase_keys)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        total = 0.0

        for key in self._phase_keys:
            try:
                total += float(data.get(key) or 0)
            except (ValueError, TypeError):
                _LOGGER.debug("Invalid value for %s", key)

        return round(total, 2)
# ==========================================================
# TOTAL WATT BACKUP
# ==========================================================
class AvriiTotalBACKUPPower(CoordinatorEntity, SensorEntity):

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "TOTAL watt of backup"
        self._attr_unique_id = f"{coordinator.host}_total_watt_of_backup"
        self._attr_native_unit_of_measurement = "W"
        self._attr_state_class = "measurement"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

        # automatycznie znajdź nazwy faz load
        self._phase_keys = [
            s["name"]
            for s in coordinator.sensors
            if "watt of backup" in s["name"].lower()
        ]

        _LOGGER.debug("Load phase keys: %s", self._phase_keys)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        total = 0.0

        for key in self._phase_keys:
            try:
                total += float(data.get(key) or 0)
            except (ValueError, TypeError):
                _LOGGER.debug("Invalid value for %s", key)

        return round(total, 2)
####################################

class AvriiInverterMode(CoordinatorEntity, SensorEntity):

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "Tryb falownika"
        self._attr_unique_id = f"{coordinator.host}_tryb_falownika"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

        # 🔎 znajdź dokładnie "Stan Inwertera"
        self._mode_key = None
        for s in coordinator.sensors:
            if "stan inwertera" in s["name"].lower():
                self._mode_key = s["name"]
                break

        _LOGGER.debug("Inverter mode key: %s", self._mode_key)

    @property
    def native_value(self):
        data = self.coordinator.data or {}

        if not self._mode_key:
            return "Brak danych"

        try:
            mode = int(data.get(self._mode_key) or 0)
        except (ValueError, TypeError):
            return "Błąd"

        if mode == 0:
            return "Inicjalizacja"
        elif mode == 1:
            return "Tryb czuwania"
        elif mode == 3:
            return "Praca z siecią"
        elif mode == 4:
            return "Praca wyspowa"
        elif mode == 5:
            return "Błąd"
        elif mode == 9:
            return "Wyłączony"
        else:
            return f"Nieznany ({mode})"

    @property
    def icon(self):
        data = self.coordinator.data or {}

        if not self._mode_key:
            return "mdi:help-circle"

        try:
            mode = int(data.get(self._mode_key) or 0)
        except (ValueError, TypeError):
            return "mdi:alert-circle"

        if mode == 3:
            return "mdi:transmission-tower"
        elif mode == 4:
            return "mdi:home-lightning-bolt"
        elif mode == 5:
            return "mdi:alert-circle"
        elif mode == 9:
            return "mdi:power"
        else:
            return "mdi:solar-power"
            
###############################################
class AvriiSystemWorkStatusDescription(CoordinatorEntity, SensorEntity):

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "System Work Status (Opis)"
        self._attr_unique_id = f"{coordinator.host}_system_work_status_opis"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

        # 🔎 znajdź dokładnie sensor zawierający "system work status"
        self._status_key = None
        for s in coordinator.sensors:
            if "system work status" in s["name"].lower():
                self._status_key = s["name"]
                break

        _LOGGER.debug("System Work Status key: %s", self._status_key)

    @property
    def native_value(self):
        data = self.coordinator.data or {}

        if not self._status_key:
            return "Brak danych"

        try:
            raw = int(data.get(self._status_key) or 0)
        except (ValueError, TypeError):
            return "Błąd"

        # --- Dekodowanie bitów ---
        mode = raw % 8
        backup = (raw // 8) % 2
        battery = (raw // 16) % 4
        pv = (raw // 64) % 2
        grid = (raw // 128) % 2
        gen_func = (raw // 512) % 4
        gen_relay = (raw // 2048) % 2

        # --- Working Mode ---
        if mode == 0:
            mode_txt = "Power On"
        elif mode == 1:
            mode_txt = "Standby"
        elif mode == 3:
            mode_txt = "On-Grid"
        elif mode == 4:
            mode_txt = "Off-Grid"
        else:
            mode_txt = f"Nieznany tryb ({mode})"

        # --- Battery ---
        if battery == 0:
            bat_txt = "Reserved"
        elif battery == 1:
            bat_txt = "Ładowanie"
        elif battery == 2:
            bat_txt = "Rozładowanie"
        elif battery == 3:
            bat_txt = "Pełna"
        else:
            bat_txt = "Nieznany"

        # --- PV ---
        pv_txt = "OK" if pv == 0 else "Błąd"

        # --- Grid ---
        grid_txt = "OK" if grid == 0 else "Awaria"

        # --- Backup ---
        backup_txt = "OFF" if backup == 0 else "ON"

        # --- Generator Function ---
        if gen_func == 0:
            gen_txt = "Wyłączony"
        elif gen_func == 1:
            gen_txt = "GEN"
        elif gen_func == 2:
            gen_txt = "Smart Load"
        elif gen_func == 3:
            gen_txt = "Inverter"
        else:
            gen_txt = "Nieznany"

        # --- Generator Relay ---
        gen_relay_txt = "OFF" if gen_relay == 0 else "ON"

        return (
            f"{mode_txt}"
            f" | Bateria: {bat_txt}"
            f" | PV: {pv_txt}"
            f" | Sieć: {grid_txt}"
            f" | Backup: {backup_txt}"
            f" | Generator: {gen_txt}"
            f" | Gen Relay: {gen_relay_txt}"
        )


# ==========================================================
# DAILY ENERGY SENSOR (RESET 00:00) – STABLE VERSION
# ==========================================================
from datetime import datetime
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity


class AvriiDailyEnergySensor(CoordinatorEntity, SensorEntity, RestoreEntity):

    _attr_has_entity_name = True
    _attr_device_class = "energy"
    _attr_state_class = "total"
    _attr_native_unit_of_measurement = "kWh"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._source_key = "ENERGY Total Load Energy"

        self._attr_name = "dzienne zużycie energii"
        self._attr_unique_id = f"{coordinator.host}_dzienne_zuzycie_energii"

        self._midnight_value = None
        self._last_reset_date = None
        self._current_value = 0

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state:
            try:
                self._current_value = float(last_state.state)
                self._midnight_value = float(
                    last_state.attributes.get("midnight_value", 0)
                )
                self._last_reset_date = last_state.attributes.get("last_reset_date")
            except Exception:
                pass

        async_track_time_change(
            self.hass,
            self._reset_midnight,
            hour=0,
            minute=0,
            second=0,
        )

    async def _reset_midnight(self, now):
        current_total = self.coordinator.data.get(self._source_key)
        if current_total is not None:
            self._midnight_value = float(current_total)
            self._last_reset_date = datetime.now().date().isoformat()
            self._current_value = 0
            self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        return {
            "midnight_value": self._midnight_value,
            "last_reset_date": self._last_reset_date,
        }

    @property
    def native_value(self):

        current_total = self.coordinator.data.get(self._source_key)

        if current_total is None:
            return self._current_value

        current_total = float(current_total)
        today = datetime.now().date().isoformat()

        # jeśli HA był wyłączony przez północ
        if self._last_reset_date != today:
            self._midnight_value = current_total
            self._last_reset_date = today
            self._current_value = 0
            return 0

        if self._midnight_value is None:
            self._midnight_value = current_total
            self._last_reset_date = today
            return 0

        self._current_value = round(current_total - self._midnight_value, 3)

        # zabezpieczenie przy restarcie falownika
        if self._current_value < 0:
            self._midnight_value = current_total
            self._current_value = 0

        return self._current_value

# ==========================================================
# GRID EXPORT ENERGY SENSOR (RESET 00:00) – STABLE VERSION
# ==========================================================
from datetime import datetime
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity


class AvriiENERGYTotalGridExportEnergy(CoordinatorEntity, SensorEntity, RestoreEntity):

    _attr_has_entity_name = True
    _attr_device_class = "energy"
    _attr_state_class = "total"
    _attr_native_unit_of_measurement = "kWh"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._source_key = "ENERGY Total Grid Export Energy"

        self._attr_name = "dzienny eksport energii"
        self._attr_unique_id = f"{coordinator.host}_dzienny_eksport_energii"

        self._midnight_value = None
        self._last_reset_date = None
        self._current_value = 0

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state:
            try:
                self._current_value = float(last_state.state)
                self._midnight_value = float(
                    last_state.attributes.get("midnight_value", 0)
                )
                self._last_reset_date = last_state.attributes.get("last_reset_date")
            except Exception:
                pass

        async_track_time_change(
            self.hass,
            self._reset_midnight,
            hour=0,
            minute=0,
            second=0,
        )

    async def _reset_midnight(self, now):
        current_total = self.coordinator.data.get(self._source_key)
        if current_total is not None:
            self._midnight_value = float(current_total)
            self._last_reset_date = datetime.now().date().isoformat()
            self._current_value = 0
            self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        return {
            "midnight_value": self._midnight_value,
            "last_reset_date": self._last_reset_date,
        }

    @property
    def native_value(self):

        current_total = self.coordinator.data.get(self._source_key)

        if current_total is None:
            return self._current_value

        current_total = float(current_total)
        today = datetime.now().date().isoformat()

        # jeśli HA był wyłączony przez północ
        if self._last_reset_date != today:
            self._midnight_value = current_total
            self._last_reset_date = today
            self._current_value = 0
            return 0

        if self._midnight_value is None:
            self._midnight_value = current_total
            self._last_reset_date = today
            return 0

        self._current_value = round(current_total - self._midnight_value, 3)

        # zabezpieczenie przy restarcie falownika / overflow
        if self._current_value < 0:
            self._midnight_value = current_total
            self._current_value = 0

        return self._current_value
        
# ==========================================================
# GRID IMPORT ENERGY SENSOR (RESET 00:00) – STABLE VERSION
# ==========================================================
from datetime import datetime
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity


class AvriiENERGYTotalGridInportEnergy(CoordinatorEntity, SensorEntity, RestoreEntity):

    _attr_has_entity_name = True
    _attr_device_class = "energy"
    _attr_state_class = "total"
    _attr_native_unit_of_measurement = "kWh"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._source_key = "ENERGY Total Grid Import Energy"

        self._attr_name = "dzienny inport energii"
        self._attr_unique_id = f"{coordinator.host}_dzienny_inport_energii"

        self._midnight_value = None
        self._last_reset_date = None
        self._current_value = 0

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state:
            try:
                self._current_value = float(last_state.state)
                self._midnight_value = float(
                    last_state.attributes.get("midnight_value", 0)
                )
                self._last_reset_date = last_state.attributes.get("last_reset_date")
            except Exception:
                pass

        async_track_time_change(
            self.hass,
            self._reset_midnight,
            hour=0,
            minute=0,
            second=0,
        )

    async def _reset_midnight(self, now):
        current_total = self.coordinator.data.get(self._source_key)
        if current_total is not None:
            self._midnight_value = float(current_total)
            self._last_reset_date = datetime.now().date().isoformat()
            self._current_value = 0
            self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        return {
            "midnight_value": self._midnight_value,
            "last_reset_date": self._last_reset_date,
        }

    @property
    def native_value(self):

        current_total = self.coordinator.data.get(self._source_key)

        if current_total is None:
            return self._current_value

        current_total = float(current_total)
        today = datetime.now().date().isoformat()

        # jeśli HA był wyłączony przez północ
        if self._last_reset_date != today:
            self._midnight_value = current_total
            self._last_reset_date = today
            self._current_value = 0
            return 0

        if self._midnight_value is None:
            self._midnight_value = current_total
            self._last_reset_date = today
            return 0

        self._current_value = round(current_total - self._midnight_value, 3)

        # zabezpieczenie przy restarcie falownika / overflow
        if self._current_value < 0:
            self._midnight_value = current_total
            self._current_value = 0

        return self._current_value

# ==========================================================
# PRODUKCJA PANELE DZIENNIE (RESET 00:00) – STABLE VERSION
# ==========================================================
from datetime import datetime
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.restore_state import RestoreEntity


class AvriiDziennaProdukcjaEnergiiNew(CoordinatorEntity, SensorEntity, RestoreEntity):

    _attr_has_entity_name = True
    _attr_device_class = "energy"
    _attr_state_class = "total"
    _attr_native_unit_of_measurement = "Wh"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._source_key = "AVRII Today Energy"

        self._attr_name = "dzienna produkcja energii new"
        self._attr_unique_id = f"{coordinator.host}_dzienna_produkcja_energii_new"

        self._midnight_value = None
        self._last_reset_date = None
        self._current_value = 0

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"AVRII ({coordinator.host})",
            manufacturer="AVRII",
            model="Pro Client Stable",
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state:
            try:
                self._current_value = float(last_state.state)
                self._midnight_value = float(
                    last_state.attributes.get("midnight_value", 0)
                )
                self._last_reset_date = last_state.attributes.get("last_reset_date")
            except Exception:
                pass

        async_track_time_change(
            self.hass,
            self._reset_midnight,
            hour=0,
            minute=0,
            second=0,
        )

    async def _reset_midnight(self, now):
        current_total = self.coordinator.data.get(self._source_key)
        if current_total is not None:
            self._midnight_value = float(current_total)
            self._last_reset_date = datetime.now().date().isoformat()
            self._current_value = 0
            self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        return {
            "midnight_value": self._midnight_value,
            "last_reset_date": self._last_reset_date,
        }

    @property
    def native_value(self):

        current_total = self.coordinator.data.get(self._source_key)

        if current_total is None:
            return self._current_value

        current_total = float(current_total)
        today = datetime.now().date().isoformat()

        # jeśli HA był wyłączony przez północ
        if self._last_reset_date != today:
            self._midnight_value = current_total
            self._last_reset_date = today
            self._current_value = 0
            return 0

        if self._midnight_value is None:
            self._midnight_value = current_total
            self._last_reset_date = today
            return 0

        self._current_value = round(current_total - self._midnight_value, 3)

        # zabezpieczenie przy restarcie falownika / overflow
        if self._current_value < 0:
            self._midnight_value = current_total
            self._current_value = 0

        return self._current_value
        
        
        