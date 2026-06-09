"""Light platform for minleon-lighting."""

import re
from typing import Any
from homeassistant.config_entries import ConfigEntry
import colorsys
from homeassistant.components.light import (
    LightEntity,
    LightEntityFeature,
    ColorMode,
    ATTR_EFFECT,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ATTR_HS_COLOR,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
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


class MinleonLightingLight(CoordinatorEntity, LightEntity):
    """minleon-lighting light class."""

    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_supported_color_modes = {ColorMode.HS}
    _attr_color_mode = ColorMode.HS
    _attr_icon = "mdi:led-strip-variant"
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
    def hs_color(self) -> tuple[float, float] | None:
        """Return hue/saturation from the current RGB color."""
        rgb = self.api.rgb_color
        if rgb is None:
            return None
        r, g, b = (v / 255.0 for v in rgb)
        h, s, _ = colorsys.rgb_to_hsv(r, g, b)
        return (h * 360, s * 100)

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        # Convert from 0-100 to 0-255 (round to avoid drift on round-trips)
        return round(self.api.brightness * 255 / 100)

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

        hs_color = kwargs.get(ATTR_HS_COLOR)

        if effect:
            # Set the effect directly
            await self.api.async_set_effect(effect)
            await self.api.async_set_brightness(self.api.brightness)
        else:
            await self.api.async_turn_on()

        if brightness is not None:
            brightness_pct = round(brightness * 100 / 255)
            await self.api.async_set_brightness(brightness_pct)

        if hs_color is not None:
            h, s = hs_color
            r, g, b = colorsys.hsv_to_rgb(h / 360, s / 100, 1.0)
            rgb = (int(r * 255), int(g * 255), int(b * 255))
            await self.api.async_set_rgb_color(rgb)
        elif rgb_color is not None:
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


class MinleonColorSlot(CoordinatorEntity, LightEntity):
    """Individual color slot control with RGB color picker."""

    def __init__(
        self,
        api: MinleonLightingApiClient,
        entry: ConfigEntry,
        slot: int,
        slot_name: str,
    ) -> None:
        """Initialize."""
        super().__init__(api.coordinator)
        self.api = api
        self._config_entry = entry
        self._slot = slot
        self._slot_name = slot_name
        self._attr_unique_id = f"minleon_bulb_{slot}_{entry.entry_id}"
        self._attr_name = f"Color {slot_name}"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:palette" if slot <= 5 else "mdi:wallpaper"
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Minleon Pixel Dancer Controller",
            "manufacturer": "Minleon",
            "model": "Pixel Dancer",
            "sw_version": "1.0",
        }
        # Track last non-black color so turn_on can restore it after a blackout
        self._last_color: tuple[int, int, int] = (255, 0, 0)

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return self._attr_unique_id

    @property
    def is_on(self) -> bool:
        """Return True if the slot has a non-black color (i.e. is contributing to the pattern)."""
        color = self.rgb_color
        return color != (0, 0, 0) if color else False

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
        """Set the color for this slot, or restore the last color if none provided."""
        rgb_color = kwargs.get(ATTR_RGB_COLOR)

        if rgb_color is not None:
            LOGGER.debug("Setting color slot %s to %s", self._slot, rgb_color)
            await self.api.async_set_color(self._slot, rgb_color)
            self._last_color = rgb_color
        else:
            # No color specified — restore the last non-black color
            LOGGER.debug("Restoring color slot %s to %s", self._slot, self._last_color)
            await self.api.async_set_color(self._slot, self._last_color)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Black out this slot so it does not contribute to the pattern."""
        LOGGER.debug("Blacking out color slot %s", self._slot)
        # Save the current color before blacking out so we can restore it
        current = self.rgb_color
        if current and current != (0, 0, 0):
            self._last_color = current
        await self.api.async_set_color(self._slot, (0, 0, 0))
        self.async_write_ha_state()
