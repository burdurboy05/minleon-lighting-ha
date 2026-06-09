"""Number platform for minleon-lighting."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import LOGGER, DOMAIN
from .api import MinleonLightingApiClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Setup number platform"""
    api = hass.data[DOMAIN][entry.entry_id]
    numbers = [
        MinleonSpeedControl(api, entry),
        MinleonSpacingControl(api, entry),
        MinleonAmountControl(api, entry),
        MinleonTrailsControl(api, entry),
    ]
    async_add_entities(numbers)


class MinleonSpeedControl(CoordinatorEntity, NumberEntity):
    """Speed control for Minleon lighting."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_icon = "mdi:speedometer"
    _attr_has_entity_name = True

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(api.coordinator)
        self.api = api
        self._config_entry = entry
        self._attr_unique_id = f"minleon_speed_{entry.entry_id}"
        self._attr_name = "Speed"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Minleon Pixel Dancer Controller",
            "manufacturer": "Minleon",
            "model": "Pixel Dancer",
            "sw_version": "1.0",
        }

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def native_value(self) -> float:
        """Return the current speed value."""
        return self.api.speed

    async def async_set_native_value(self, value: float) -> None:
        """Set new speed value."""
        speed = int(value)
        LOGGER.debug("Setting Minleon speed to %s", speed)

        await self.api.async_set_speed(speed)
        self.async_write_ha_state()


class MinleonSpacingControl(CoordinatorEntity, NumberEntity):
    """Spacing control for Minleon lighting effects."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_icon = "mdi:arrow-expand-horizontal"
    _attr_has_entity_name = True

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(api.coordinator)
        self.api = api
        self._config_entry = entry
        self._attr_unique_id = f"minleon_spacing_{entry.entry_id}"
        self._attr_name = "Spacing"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Minleon Pixel Dancer Controller",
            "manufacturer": "Minleon",
            "model": "Pixel Dancer",
            "sw_version": "1.0",
        }

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def native_value(self) -> float:
        """Return the current spacing value."""
        return self.api.spacing

    async def async_set_native_value(self, value: float) -> None:
        """Set new spacing value."""
        spacing = int(value)
        LOGGER.debug("Setting Minleon spacing to %s", spacing)

        result = await self.api._send_command({"fxn": 1, "spacing": str(spacing)})
        if result:
            self.api._spacing = spacing
        self.async_write_ha_state()


class MinleonAmountControl(CoordinatorEntity, NumberEntity):
    """Amount control for Minleon lighting effects."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_icon = "mdi:numeric"
    _attr_has_entity_name = True

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(api.coordinator)
        self.api = api
        self._config_entry = entry
        self._attr_unique_id = f"minleon_amount_{entry.entry_id}"
        self._attr_name = "Amount"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Minleon Pixel Dancer Controller",
            "manufacturer": "Minleon",
            "model": "Pixel Dancer",
            "sw_version": "1.0",
        }

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def native_value(self) -> float:
        """Return the current amount value."""
        return self.api.amount

    async def async_set_native_value(self, value: float) -> None:
        """Set new amount value."""
        amount = int(value)
        LOGGER.debug("Setting Minleon amount to %s", amount)

        result = await self.api._send_command({"fxn": 1, "amount": str(amount)})
        if result:
            self.api._amount = amount
        self.async_write_ha_state()


class MinleonTrailsControl(CoordinatorEntity, NumberEntity):
    """Trails control for Minleon lighting effects."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_icon = "mdi:trail"
    _attr_has_entity_name = True

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(api.coordinator)
        self.api = api
        self._config_entry = entry
        self._attr_unique_id = f"minleon_trails_{entry.entry_id}"
        self._attr_name = "Trails"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Minleon Pixel Dancer Controller",
            "manufacturer": "Minleon",
            "model": "Pixel Dancer",
            "sw_version": "1.0",
        }

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def native_value(self) -> float:
        """Return the current trails value."""
        return self.api.trails

    async def async_set_native_value(self, value: float) -> None:
        """Set new trails value."""
        trails = int(value)
        LOGGER.debug("Setting Minleon trails to %s", trails)

        result = await self.api._send_command({"fxn": 1, "trails": str(trails)})
        if result:
            self.api._trails = trails
        self.async_write_ha_state()