"""Select platform for minleon-lighting RGBW presets."""

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import LOGGER, DOMAIN
from .api import MinleonLightingApiClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Setup select platform for color presets and effects"""
    api = hass.data[DOMAIN][entry.entry_id]

    selects = []
    
    # Create color preset selectors for each slot
    for slot in range(1, 7):  # Slots 1-6
        slot_name = f"Bulb {slot}" if slot <= 5 else "Background"
        selects.append(MinleonColorPreset(api, entry, slot, slot_name))
    
    # Create the main color preset selector
    selects.append(MinleonColorPresetSelector(api, entry))

    # Create the effect selector
    selects.append(MinleonEffectSelector(api, entry))

    async_add_entities(selects)


class MinleonColorPreset(SelectEntity):
    """Color preset selector for RGBW combinations."""

    _attr_has_entity_name = True

    # RGBW color presets matching Pixel Dancer app
    _color_presets = {
        "Custom": None,  # No preset - custom color
        "Cool White": "#0080FFFF",  # Cool white with white channel
        "Warm White": "#FFE1A8FF",  # Warm white tint with white channel
        "Pure White": "#000000FF",  # Pure white channel only
        "Red": "#FF000000",         # Pure red
        "Green": "#00FF0000",       # Pure green
        "Blue": "#0000FF00",        # Pure blue
        "Yellow": "#FFFF0000",      # Red + Green
        "Cyan": "#00FFFF00",        # Green + Blue
        "Magenta": "#FF00FF00",     # Red + Blue
        "Orange": "#FF800000",      # Red + some green
        "Purple": "#8000FF00",      # Red + Blue tint
        "Dark": "#00000000",        # Off/Dark
    }

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
        slot: int,
        slot_name: str,
    ) -> None:
        """Initialize."""
        self.api = api
        self._config_entry = entry
        self._slot = slot
        self._slot_name = slot_name
        self._attr_unique_id = f"minleon_color_preset_{slot}_{entry.entry_id}"
        self._attr_name = f"{slot_name} Preset"
        self._attr_icon = "mdi:palette" if slot <= 5 else "mdi:wallpaper"
        self._attr_options = list(self._color_presets.keys())
        self._attr_current_option = "Custom"
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
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        # Return Custom to avoid confusing auto-detection
        # RGBW presets don't reliably match back to RGB values
        return "Custom"

    def _get_current_color_hex(self) -> str:
        """Get current color as 8-digit hex string."""
        if self._slot == 6:
            rgb = self.api._background_color
        else:
            if self._slot - 1 < len(self.api._colors):
                rgb = self.api._colors[self._slot - 1]
            else:
                rgb = (0, 0, 0)

        # Convert RGB to RRGGBB00 format (no white channel info available)
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}00"

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert 8-digit hex to RGB tuple (ignoring white channel for now)."""
        hex_color = hex_color.lstrip('#')
        return (
            int(hex_color[0:2], 16),  # Red
            int(hex_color[2:4], 16),  # Green
            int(hex_color[4:6], 16),  # Blue
        )

    async def async_select_option(self, option: str) -> None:
        """Handle option selection."""
        if option == "Custom":
            return  # Do nothing for custom

        preset_color = self._color_presets.get(option)
        if preset_color:
            LOGGER.debug("Setting slot %s to preset %s (%s)", self._slot, option, preset_color)

            # Convert 8-digit RGBW hex to RGB tuple and use the proper API method
            rgb = self._hex_to_rgb(preset_color)
            await self.api.async_set_color(self._slot, rgb)
            
            self.async_write_ha_state()



class MinleonColorPresetSelector(SelectEntity):
    """Color preset selector for holiday/team colors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
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
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def current_option(self) -> str:
        """Return the current preset."""
        return self.api.last_color_preset

    async def async_select_option(self, option: str) -> None:
        """Handle color preset selection."""
        if option == "None":
            return  # Do nothing
            
        LOGGER.debug("Applying color preset %s", option)
        await self.api.async_apply_holiday_preset(option)
        self.async_write_ha_state()


class MinleonEffectSelector(SelectEntity):
    """Effect selector for lighting effects."""

    _attr_has_entity_name = True

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
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
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

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
