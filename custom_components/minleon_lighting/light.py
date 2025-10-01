"""Light platform for minleon-lighting."""

import re
from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.light import (
    LightEntity,
    LightEntityFeature,
    ColorMode,
    ATTR_EFFECT,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
)
from .const import (
    LOGGER,
    DOMAIN,
    DEFAULT_BRIGHTNESS,
    DEFAULT_COLOR,
    KNOWN_EFFECTS,
)
from .api import MinleonLightingApiClient


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup light platform"""
    api = hass.data[DOMAIN][entry.entry_id]

    # Main light entity
    lights = [MinleonLightingLight(api, entry)]

    # Individual color slot entities (5 bulbs + 1 background)
    for slot in range(1, 6):
        lights.append(MinleonColorSlot(api, entry, slot, f"Bulb {slot}"))

    # Background color (slot 6)
    lights.append(MinleonColorSlot(api, entry, 6, "Background"))

    async_add_entities(lights)


class MinleonLightingLight(LightEntity):
    """minleon-lighting light class."""

    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_icon = "mdi:led-strip-variant"
    _attr_has_entity_name = True

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.api = api
        self._config_entry = entry
        self._attr_unique_id = f"minleon_{entry.entry_id}"
        self._attr_name = "Minleon Christmas Lights"
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
        return True  # We'll assume it's available if configured

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        # Only return actual effects, not color presets
        return self.api.available_effects.copy()

    @property
    def is_on(self) -> bool:
        """Return the state of the light."""
        return self.api.is_on

    @property
    def effect(self) -> str | None:
        """Return the current effect of the light."""
        return self.api.current_effect

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the color value."""
        return self.api.rgb_color

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        # Convert from 0-100 to 0-255
        return int(self.api.brightness / 100 * 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        effect = kwargs.get(ATTR_EFFECT)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        LOGGER.debug(
            "Turning on Minleon lights (effect: %s, color: %s, brightness: %s)",
            effect,
            rgb_color,
            brightness,
        )

        if effect:
            # Set the effect directly
            await self.api.async_set_effect(effect)
            # Ensure speed and brightness are set for effect visibility
            await self.api.async_set_speed(50)  # Default speed
            await self.api.async_set_brightness(self.api.brightness)  # Keep current brightness  # Keep current brightness
        else:
            # Just turn on with current settings
            await self.api.async_turn_on()

        if brightness is not None:
            # Convert brightness from 0-255 to 0-100
            brightness_pct = int(brightness / 255 * 100)
            await self.api.async_set_brightness(brightness_pct)

        if rgb_color is not None:
            await self.api.async_set_rgb_color(rgb_color)

        # Update state
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        LOGGER.debug("Turning off Minleon lights")
        await self.api.async_turn_off()
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the light state."""
        # For now, we'll rely on our internal state tracking
        # In a more advanced version, we could poll the controller for state
        pass


class MinleonColorSlot(LightEntity):
    """Individual color slot control."""

    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = 0  # No brightness, no on/off
    _attr_has_entity_name = True

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
        self._attr_unique_id = f"minleon_color_slot_{slot}_{entry.entry_id}"
        self._attr_name = f"Color {slot_name}"
        self._attr_icon = "mdi:palette" if slot <= 5 else "mdi:wallpaper"
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
    def is_on(self) -> bool:
        """Always return True - no on/off control."""
        return True

    @property
    def brightness(self) -> None:
        """Return None to disable brightness control."""
        return None

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the RGB color value for this slot."""
        if self._slot == 6:
            return self.api._background_color
        else:
            if self._slot - 1 < len(self.api._colors):
                return self.api._colors[self._slot - 1]
        return (0, 0, 0)

    async def async_turn_on(self, **kwargs) -> None:
        """Set the color for this slot."""
        rgb_color = kwargs.get(ATTR_RGB_COLOR)

        if rgb_color is not None:
            LOGGER.debug("Setting color slot %s to %s", self._slot, rgb_color)
            await self.api.async_set_color(self._slot, rgb_color)
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Ignore turn off commands."""
        # Do nothing - no on/off control for individual slots
        pass