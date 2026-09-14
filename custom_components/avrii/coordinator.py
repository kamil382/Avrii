import logging
import asyncio
import yaml
from pathlib import Path
from datetime import timedelta, datetime
from functools import partial

from pymodbus.client import ModbusTcpClient
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import *

_LOGGER = logging.getLogger(__name__)


class AvriiCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, host):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="avrii",
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

        self.hass = hass
        self.host = host

        self._client = ModbusTcpClient(
            host,
            port=DEFAULT_PORT,
            timeout=MODBUS_TIMEOUT,
            retries=MODBUS_RETRIES,
        )

        self._lock = asyncio.Lock()

        self._connected = False
        self._error_count = 0
        self._last_update = datetime.utcnow()
        self._last_socket_reset = datetime.utcnow()

        self._watchdog_task = None

        self.sensors = []
        self.switches = []
        self._read_blocks = []

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    async def async_initialize(self):
        self.sensors = await self.hass.async_add_executor_job(
            self._load_yaml, INTEGRATION_SENSORS_FILE
        )
        self.switches = await self.hass.async_add_executor_job(
            self._load_yaml, INTEGRATION_SWITCHES_FILE
        )

        self._read_blocks = self._build_read_blocks()
        self._watchdog_task = asyncio.create_task(self._watchdog_loop())

    def _load_yaml(self, filename):
        path = Path(self.hass.config.path(f"custom_components/avrii/{filename}"))
        if path.exists():
            with open(path, "r") as f:
                return yaml.safe_load(f) or []
        return []

    # ==========================================================
    # BUILD BLOCKS
    # ==========================================================

    def _build_read_blocks(self):

        addresses = set()

        # --- sensory ---
        for s in self.sensors:
            addr = int(s["address"])
            addresses.add(addr)

            if "32" in s.get("data_type", ""):
                addresses.add(addr + 1)

        # --- number encje ---
        addresses.update([8472, 8475, 12473, 12474])

        # --- switch verify ---
        for sw in self.switches:
            verify = sw.get("verify")
            if verify:
                addresses.add(int(verify["address"]))

        addresses = sorted(addresses)

        if not addresses:
            return []

        blocks = []
        start = addresses[0]
        prev = start

        for addr in addresses[1:]:
            if addr == prev + 1:
                prev = addr
            else:
                blocks.append((start, prev))
                start = addr
                prev = addr

        blocks.append((start, prev))
        return blocks

    # ==========================================================
    # CONNECTION
    # ==========================================================

    async def async_close(self):
        if self._watchdog_task:
            self._watchdog_task.cancel()

        async with self._lock:
            try:
                self._client.close()
            except Exception:
                pass

    async def _ensure_connection(self):

        if not self._client.connected:
            try:
                await self.hass.async_add_executor_job(self._client.close)
            except Exception:
                pass

            self._connected = await self.hass.async_add_executor_job(
                self._client.connect
            )

            if self._connected:
                self._error_count = 0
            else:
                _LOGGER.error("Reconnect failed")

    async def _force_socket_reset(self):
        try:
            await self.hass.async_add_executor_job(self._client.close)
        except Exception:
            pass

        self._connected = False
        self._last_socket_reset = datetime.utcnow()

    # ==========================================================
    # WATCHDOG
    # ==========================================================

    async def _watchdog_loop(self):
        while True:
            await asyncio.sleep(WATCHDOG_INTERVAL)

            now = datetime.utcnow()

            if (now - self._last_update).total_seconds() > WATCHDOG_MAX_NO_UPDATE:
                await self._force_socket_reset()

            if (now - self._last_socket_reset).total_seconds() > AUTO_SOCKET_RESET_HOURS * 3600:
                await self._force_socket_reset()

    # ==========================================================
    # UPDATE LOOP
    # ==========================================================

    async def _async_update_data(self):

        async with self._lock:

            await self._ensure_connection()

            data = dict(self.data) if self.data else {}

            try:

                raw_registers = {}

                # 1️⃣ odczyt bloków
                for start, end in self._read_blocks:

                    count = end - start + 1

                    result = await self.hass.async_add_executor_job(
                        partial(
                            self._client.read_holding_registers,
                            address=start,
                            count=count,
                            device_id=DEFAULT_SLAVE,
                        )
                    )

                    if not result or result.isError():
                        raise Exception("Block read error")

                    for i, val in enumerate(result.registers):
                        raw_registers[start + i] = val

                # 2️⃣ sensory
                for s in self.sensors:

                    addr = int(s["address"])
                    dtype = s.get("data_type", "uint16")

                    if addr not in raw_registers:
                        continue

                    if "32" not in dtype:
                        value = self._decode(
                            [raw_registers[addr]],
                            dtype,
                        )
                    else:
                        if addr + 1 not in raw_registers:
                            continue

                        regs = [
                            raw_registers[addr],
                            raw_registers[addr + 1],
                        ]
                        value = self._decode(regs, dtype)

                    data[s["name"]] = value * s.get("scale", 1)

                # 3️⃣ number encje
                if 8472 in raw_registers:
                    data["reg_8472"] = raw_registers[8472]

                if 8475 in raw_registers:
                    data["reg_8475"] = raw_registers[8475]

                if 12473 in raw_registers and 12474 in raw_registers:
                    high = raw_registers[12473]
                    low = raw_registers[12474]
                    data["reg_12473"] = (high << 16) + low

                # 4️⃣ switch verify
                for sw in self.switches:

                    verify = sw.get("verify")
                    if not verify:
                        continue

                    vaddr = int(verify["address"])

                    if vaddr in raw_registers:
                        data[sw["name"]] = (
                            raw_registers[vaddr] == verify["state_on"]
                        )

                self._last_update = datetime.utcnow()
                self._error_count = 0

            except Exception as e:
                _LOGGER.error("Update failed: %s", e)
                self._error_count += 1
                await self._force_socket_reset()

            return data

    # ==========================================================
    # WRITE
    # ==========================================================

    async def async_write(self, address, value):

        async with self._lock:

            await self._ensure_connection()

            try:

                if int(address) == 12473:

                    low = value & 0xFFFF
                    high = (value >> 16) & 0xFFFF

                    result = await self.hass.async_add_executor_job(
                        partial(
                            self._client.write_registers,
                            address=12473,
                            values=[high, low],
                            device_id=DEFAULT_SLAVE,
                        )
                    )

                else:
                    result = await self.hass.async_add_executor_job(
                        partial(
                            self._client.write_register,
                            address=int(address),
                            value=value,
                            device_id=DEFAULT_SLAVE,
                        )
                    )

                if not result or result.isError():
                    raise Exception("Write error")

            except Exception as e:
                _LOGGER.error("Write failed: %s", e)
                self._error_count += 1
                await self._force_socket_reset()

        await self.async_request_refresh()

    # ==========================================================
    # DECODE
    # ==========================================================

    def _decode(self, regs, dtype):

        if dtype == "uint16":
            return regs[0]

        if dtype == "int16":
            return regs[0] if regs[0] < 32768 else regs[0] - 65536

        if dtype == "uint32":
            return (regs[0] << 16) + regs[1]

        if dtype == "int32":
            val = (regs[0] << 16) + regs[1]
            return val if val < 0x80000000 else val - 0x100000000

        return regs[0]