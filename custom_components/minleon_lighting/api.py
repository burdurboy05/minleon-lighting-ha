"""Minleon Pixel Dancer API Client."""

import asyncio
import aiohttp
import json
import os
from typing import List, Tuple, Dict, Optional
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigEntry

from .const import LOGGER, KNOWN_EFFECTS, HOLIDAY_PRESETS, NFL_PRESETS, NATION_PRESETS, SOCCER_PRESETS, AUSTRALIAN_FOOTBALL_PRESETS, NBA_PRESETS


class MinleonLightingApiClient:
    """API Client for Minleon Pixel Dancer Lighting"""

    def __init__(self, address: str, config_entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize API client."""
        self.address = address
        self._config_entry = config_entry
        self._hass = hass
        self._session = None
        self._base_url = f"http://{address}/api/control"

        # Current state
        self._is_on = False
        self._current_effect = "Off"
        self._brightness = 75
        self._speed = 50
        self._colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0)]  # Default colors
        self._background_color = (0, 0, 0)

        # Last selected preset and effect (persisted when lights are off)
        self._last_color_preset = "None"
        self._last_effect = "Off"

        # Persistent state file path (will be set later)
        self._state_file = None
        self._hass_ready = False

    @property
    def session(self):
        """Get aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

    def _ensure_state_file(self):
        """Ensure state file path is initialized."""
        if self._state_file is None and self._hass is not None:
            try:
                self._state_file = f"{self._hass.config.config_dir}/minleon_lighting_state_{self._config_entry.entry_id}.json"
                self._load_persistent_state()
                self._hass_ready = True
            except Exception as ex:
                LOGGER.warning("Failed to initialize state file: %s", ex)

    def _load_persistent_state(self):
        """Load last preset and effect from persistent storage."""
        try:
            if self._state_file and os.path.exists(self._state_file):
                with open(self._state_file, 'r') as f:
                    state = json.load(f)
                    self._last_color_preset = state.get('last_color_preset', 'None')
                    self._last_effect = state.get('last_effect', 'Off')
                    LOGGER.debug("Loaded persistent state: preset=%s, effect=%s",
                               self._last_color_preset, self._last_effect)
        except Exception as ex:
            LOGGER.warning("Failed to load persistent state: %s", ex)

    def _save_persistent_state(self):
        """Save last preset and effect to persistent storage."""
        try:
            self._ensure_state_file()
            if self._state_file and self._hass_ready:
                state = {
                    'last_color_preset': self._last_color_preset,
                    'last_effect': self._last_effect
                }
                with open(self._state_file, 'w') as f:
                    json.dump(state, f)
                LOGGER.debug("Saved persistent state: preset=%s, effect=%s",
                           self._last_color_preset, self._last_effect)
        except Exception as ex:
            LOGGER.warning("Failed to save persistent state: %s", ex)

    async def _send_command(self, payload: dict) -> bool:
        """Send command to Minleon controller."""
        try:
            LOGGER.debug("Sending command to %s: %s", self._base_url, payload)

            async with self.session.post(
                self._base_url,
                data=json.dumps(payload),
                headers={"Content-Type": "text/plain;charset=UTF-8"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.text()
                    LOGGER.debug("Command successful: %s", result)
                    # Accept any 200 response, including "200 OK" HTML responses
                    return True
                else:
                    LOGGER.error("Command failed with status %s", response.status)
                    return False

        except asyncio.TimeoutError:
            LOGGER.error("Timeout sending command to Minleon controller")
            return False
        except Exception as ex:
            LOGGER.error("Error sending command to Minleon controller: %s", ex)
            return False

    async def async_test_connection(self) -> bool:
        """Test connection to the controller."""
        try:
            # Try to turn off the lights as a connection test
            result = await self._send_command({"fxn": 1, "fx": "Off"})
            return result
        except Exception as ex:
            LOGGER.error("Connection test failed: %s", ex)
            return False

    async def async_turn_on(self) -> bool:
        """Turn on the lights with current effect."""
        # Restore the last effect if currently off
        if self._current_effect == "Off":
            if self._last_effect != "Off":
                self._current_effect = self._last_effect
            else:
                # Default to Fixed Colors when turning on for the first time
                self._current_effect = "Fixed Colors"

        result = await self._send_command({"fxn": 1, "fx": self._current_effect})
        if result:
            self._is_on = True
            # Apply current brightness and speed
            await self._send_command({"fxn": 1, "int": self._brightness})
            await self._send_command({"fxn": 1, "spd": self._speed})
        return result

    async def async_turn_off(self) -> bool:
        """Turn off the lights."""
        result = await self._send_command({"fxn": 1, "fx": "Off"})
        if result:
            self._is_on = False
            self._current_effect = "Off"
        return result

    async def async_set_effect(self, effect: str) -> bool:
        """Set the lighting effect."""
        if effect not in KNOWN_EFFECTS:
            LOGGER.warning("Unknown effect: %s", effect)
            return False

        result = await self._send_command({"fxn": 1, "fx": effect})
        if result:
            self._current_effect = effect
            self._is_on = effect != "Off"
            # Remember the last effect if it's not "Off"
            if effect != "Off":
                self._last_effect = effect
                self._save_persistent_state()  # Save to file
        return result

    async def async_set_brightness(self, brightness: int) -> bool:
        """Set brightness (0-100)."""
        if not 0 <= brightness <= 100:
            LOGGER.error("Brightness must be between 0-100, got %s", brightness)
            return False

        result = await self._send_command({"fxn": 1, "int": str(brightness)})
        if result:
            self._brightness = brightness
        return result

    async def async_set_speed(self, speed: int) -> bool:
        """Set effect speed (0-100)."""
        if not 0 <= speed <= 100:
            LOGGER.error("Speed must be between 0-100, got %s", speed)
            return False

        result = await self._send_command({"fxn": 1, "spd": str(speed)})
        if result:
            self._speed = speed
        return result

    async def async_set_color(self, slot: int, color: Tuple[int, int, int]) -> bool:
        """Set color for a specific slot (1-5) or background (6)."""
        if not 1 <= slot <= 6:
            LOGGER.error("Color slot must be between 1-6, got %s", slot)
            return False

        hex_color = "#{:02x}{:02x}{:02x}".format(*color).upper()
        result = await self._send_command({
            "fxn": 1,
            "color": {"i": slot, "c": hex_color}
        })

        if result:
            if slot == 6:
                self._background_color = color
            else:
                self._colors[slot - 1] = color

        return result

    async def async_set_rgb_color(self, color: Tuple[int, int, int]) -> bool:
        """Set the primary color (slot 1)."""
        return await self.async_set_color(1, color)

    async def async_apply_holiday_preset(self, preset_name: str) -> bool:
        """Apply a color preset (colors only, no effects)."""
        LOGGER.info("Applying color preset: %s", preset_name)

        # Check all preset categories
        preset = None
        if preset_name in HOLIDAY_PRESETS:
            preset = HOLIDAY_PRESETS[preset_name]
        elif preset_name in NFL_PRESETS:
            preset = NFL_PRESETS[preset_name]
        elif preset_name in NATION_PRESETS:
            preset = NATION_PRESETS[preset_name]
        elif preset_name in SOCCER_PRESETS:
            preset = SOCCER_PRESETS[preset_name]
        elif preset_name in AUSTRALIAN_FOOTBALL_PRESETS:
            preset = AUSTRALIAN_FOOTBALL_PRESETS[preset_name]
        elif preset_name in NBA_PRESETS:
            preset = NBA_PRESETS[preset_name]

        if preset is None:
            LOGGER.error("Unknown preset: %s", preset_name)
            return False

        LOGGER.info("Color preset data: %s", preset)

        # Apply colors only - no effect, speed, or brightness changes
        LOGGER.info("Setting colors: %s", preset["colors"])
        
        # Clear all 5 bulb slots first, then apply preset colors
        for i in range(1, 6):  # Slots 1-5
            if i - 1 < len(preset["colors"]):
                # Apply preset color to this slot
                hex_color = preset["colors"][i - 1].lstrip('#')
                rgb = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))
                LOGGER.info("Setting color slot %d to %s (RGB: %s)", i, hex_color, rgb)
                await self.async_set_color(i, rgb)
            else:
                # Clear unused slots (set to black/off)
                LOGGER.info("Clearing unused color slot %d", i)
                await self.async_set_color(i, (0, 0, 0))

        LOGGER.info("Color preset %s applied successfully", preset_name)
        # Remember the last preset
        self._last_color_preset = preset_name
        self._save_persistent_state()  # Save to file
        return True

    # Properties for state tracking
    @property
    def is_on(self) -> bool:
        """Return if lights are on."""
        return self._is_on

    @property
    def current_effect(self) -> str:
        """Return current effect."""
        return self._current_effect

    @property
    def brightness(self) -> int:
        """Return current brightness (0-100)."""
        return self._brightness

    @property
    def speed(self) -> int:
        """Return current speed (0-100)."""
        return self._speed

    @property
    def rgb_color(self) -> Tuple[int, int, int]:
        """Return current primary color."""
        return self._colors[0]

    @property
    def available_effects(self) -> List[str]:
        """Return list of available effects."""
        return KNOWN_EFFECTS.copy()

    @property
    def last_color_preset(self) -> str:
        """Return the last selected color preset."""
        return self._last_color_preset

    @property
    def last_effect(self) -> str:
        """Return the last selected effect."""
        return self._last_effect

    @property
    def available_presets(self) -> List[str]:
        """Return list of available presets from all categories."""
        all_presets = []
        all_presets.extend(list(HOLIDAY_PRESETS.keys()))
        all_presets.extend(list(NFL_PRESETS.keys()))
        all_presets.extend(list(NATION_PRESETS.keys()))
        all_presets.extend(list(SOCCER_PRESETS.keys()))
        all_presets.extend(list(AUSTRALIAN_FOOTBALL_PRESETS.keys()))
        all_presets.extend(list(NBA_PRESETS.keys()))
        return all_presets


class MinleonLightingZoneData:
    """Simple class to store the state of the Minleon lights"""

    def __init__(
        self,
        is_on: bool = False,
        effect: str = "Off",
        brightness: int = 75,
        speed: int = 50,
        color: tuple[int, int, int] = (255, 0, 0),
    ):
        self.is_on = is_on
        self.effect = effect
        self.brightness = brightness
        self.speed = speed
        self.color = color

    def __repr__(self) -> str:
        return str(vars(self))
