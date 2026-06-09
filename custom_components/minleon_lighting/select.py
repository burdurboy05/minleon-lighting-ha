"""Select platform for minleon-lighting RGBW presets."""

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import LOGGER, DOMAIN
from .api import MinleonLightingApiClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Setup select platform for color presets and effects"""
    api = hass.data[DOMAIN][entry.entry_id]

    selects = []
    
    # Create the main color preset selector
    selects.append(MinleonColorPresetSelector(api, entry))

    # Create the effect selector
    selects.append(MinleonEffectSelector(api, entry))

    # Create the overlay effect selector
    selects.append(MinleonOverlayEffectSelector(api, entry))

    async_add_entities(selects)


class MinleonColorPresetSelector(CoordinatorEntity, SelectEntity):
    """Color preset selector for holiday/team colors."""

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
        self._attr_unique_id = f"minleon_color_preset_selector_{entry.entry_id}"
        self._attr_name = "Color Preset"
        self._attr_icon = "mdi:palette-swatch"
        self._attr_options = ["None"] + self.api.available_presets
        self._attr_current_option = "None"
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
    def current_option(self) -> str:
        """Return the current preset."""
        return self.api.last_color_preset

    async def async_select_option(self, option: str) -> None:
        """Handle color preset selection."""
        if option == "None":
            # Clear the active preset tracking without changing colors on the controller
            self.api._last_color_preset = "None"
            self.api._save_persistent_state()
            self.async_write_ha_state()
            return

        LOGGER.debug("Applying color preset %s", option)
        await self.api.async_apply_holiday_preset(option)
        self.async_write_ha_state()


class MinleonEffectSelector(CoordinatorEntity, SelectEntity):
    """Effect selector for lighting effects."""

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
        self._attr_unique_id = f"minleon_effect_selector_{entry.entry_id}"
        self._attr_name = "Effect"
        self._attr_icon = "mdi:auto-fix"
        self._attr_options = self.api.available_effects
        self._attr_current_option = "Off"
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
    def current_option(self) -> str:
        """Return the current effect."""
        # If lights are off, show the last effect instead of "Off"
        if not self.api.is_on and self.api.last_effect != "Off":
            return self.api.last_effect
        return self.api.current_effect

    async def async_select_option(self, option: str) -> None:
        """Handle effect selection."""
        LOGGER.debug("Setting effect to %s", option)
        await self.api.async_set_effect(option)
        self.async_write_ha_state()


class MinleonOverlayEffectSelector(CoordinatorEntity, SelectEntity):
    """Overlay effect selector for lighting overlay effects."""

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
        self._attr_unique_id = f"minleon_overlay_effect_selector_{entry.entry_id}"
        self._attr_name = "Overlay Effect"
        self._attr_icon = "mdi:layers-triple"
        self._attr_options = ["Off", "Lightning", "Fader"]
        self._attr_current_option = "Off"
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
    def current_option(self) -> str:
        """Return the current overlay effect."""
        return self.api.overlay_effect

    async def async_select_option(self, option: str) -> None:
        """Handle overlay effect selection."""
        LOGGER.debug("Setting overlay effect to %s", option)
        await self.api.async_set_overlay_effect(option)
        self.async_write_ha_state()
