"""Minleon Pixel Dancer API Client."""

import asyncio
import aiohttp
import json
import os
from typing import List, Tuple, Dict, Optional
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store

from .const import DOMAIN, LOGGER, KNOWN_EFFECTS, HOLIDAY_PRESETS, NFL_PRESETS, NATION_PRESETS, SOCCER_PRESETS, AUSTRALIAN_FOOTBALL_PRESETS, NBA_PRESETS, MLB_PRESETS, NHL_PRESETS

STORAGE_VERSION = 1


class MinleonLightingApiClient:
    """API Client for Minleon Pixel Dancer Lighting"""

    def __init__(self, address: str, config_entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize API client."""
        self.address = address
        self._config_entry = config_entry
        self._hass = hass
        self._base_url = f"http://{address}/api/control"

        # Serialize HTTP requests to the (single-threaded) controller so
        # commands and polls never overlap on the device.
        self._command_lock = asyncio.Lock()

        # Current state
        self._is_on = False
        self._current_effect = "Off"
        self._brightness = 75
        self._speed = 50
        self._colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0)]  # Default colors
        self._background_color = (0, 0, 0)
        self._overlay_effect = "Off"

        # Effect parameters mirrored from the controller on each poll
        self._trails = 0
        self._amount = 50
        self._spacing = 16

        # Data update coordinator (assigned in async_setup_entry)
        self.coordinator = None

        # Last selected preset and effect (persisted when lights are off)
        self._last_color_preset = "None"
        self._last_effect = "Off"

        # Async persistent storage (.storage/minleon_lighting_<entry_id>).
        # config_entry is None during the config-flow connection test, where
        # no persistence is needed.
        if config_entry is not None:
            self._store = Store(
                hass, STORAGE_VERSION, f"{DOMAIN}_{config_entry.entry_id}"
            )
        else:
            self._store = None

    @property
    def session(self):
        """Return Home Assistant's shared aiohttp session."""
        return async_get_clientsession(self._hass)

    async def async_close(self):
        """No-op: the shared HA client session is managed by Home Assistant."""
        return

    def _apply_persistent_state(self, state: dict) -> None:
        """Populate in-memory state from a loaded persistence dict."""
        self._last_color_preset = state.get('last_color_preset', 'None')
        self._last_effect = state.get('last_effect', 'Off')
        self._is_on = state.get('is_on', False)
        # Restore color slots so animated effects have the correct colors
        saved_colors = state.get('colors')
        if saved_colors and len(saved_colors) == 5:
            self._colors = [tuple(c) for c in saved_colors]
        saved_bg = state.get('background_color')
        if saved_bg and len(saved_bg) == 3:
            self._background_color = tuple(saved_bg)
        # Restore current effect if lights were on
        if self._is_on and self._last_effect != 'Off':
            self._current_effect = self._last_effect

    def _read_legacy_state_file(self) -> Optional[dict]:
        """Read the pre-1.5 JSON state file (runs in an executor thread)."""
        legacy = (
            f"{self._hass.config.config_dir}"
            f"/minleon_lighting_state_{self._config_entry.entry_id}.json"
        )
        try:
            if os.path.exists(legacy):
                with open(legacy, 'r') as f:
                    return json.load(f)
        except Exception as ex:  # noqa: BLE001
            LOGGER.warning("Failed to read legacy state file: %s", ex)
        return None

    async def async_load_persistent_state(self) -> None:
        """Load persisted state from the async Store (migrating the old file once)."""
        if self._store is None:
            return
        try:
            state = await self._store.async_load()
            if state is None:
                # One-time migration from the legacy blocking JSON file
                state = await self._hass.async_add_executor_job(
                    self._read_legacy_state_file
                )
                if state:
                    LOGGER.info("Migrated Minleon state from legacy JSON file to Store")
                    self._apply_persistent_state(state)
                    await self._store.async_save(self._persistent_data())
                    return
            if state:
                self._apply_persistent_state(state)
                LOGGER.debug(
                    "Loaded persistent state: preset=%s, effect=%s, is_on=%s",
                    self._last_color_preset, self._last_effect, self._is_on,
                )
        except Exception as ex:  # noqa: BLE001
            LOGGER.warning("Failed to load persistent state: %s", ex)

    def _persistent_data(self) -> dict:
        """Return the data to persist (callback for delayed save)."""
        return {
            'last_color_preset': self._last_color_preset,
            'last_effect': self._last_effect,
            'is_on': self._is_on,
            'colors': [list(c) for c in self._colors],
            'background_color': list(self._background_color),
        }

    def _save_persistent_state(self):
        """Schedule a debounced async save of the current state (non-blocking)."""
        if self._store is not None:
            # async_delay_save is loop-safe and coalesces rapid updates
            self._store.async_delay_save(self._persistent_data, 1.0)

    async def _send_command(self, payload: dict) -> bool:
        """Send command to Minleon controller."""
        try:
            LOGGER.debug("Sending command to %s: %s", self._base_url, payload)

            async with self._command_lock:
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
        """Verify the host is a reachable Minleon controller.

        Reads /api/status and confirms it returns a 200 with the expected
        JSON shape, so pointing at the wrong device (which may answer with a
        404/other 2xx-4xx) is rejected.
        """
        try:
            async with self.session.get(
                f"http://{self.address}/api/status",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    LOGGER.error("Connection test got HTTP %s", response.status)
                    return False
                data = json.loads(await response.text())
                LOGGER.debug("Connection test status payload: %s", data)
                return "status" in data
        except Exception as ex:
            LOGGER.error("Connection test failed: %s", ex)
            return False

    async def async_get_device_info(self) -> Optional[dict]:
        """Return the controller's /api/status payload (mac, uuid, firmware)."""
        try:
            async with self._command_lock:
                async with self.session.get(
                    f"http://{self.address}/api/status",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status != 200:
                        return None
                    data = json.loads(await response.text())
            return data.get("status", data)
        except Exception as ex:  # noqa: BLE001
            LOGGER.warning("Failed to read device info: %s", ex)
            return None

    @staticmethod
    def _parse_color(value) -> Tuple[int, int, int]:
        """Parse a controller color value (e.g. '#c69740' or 'none') to RGB."""
        if not value or value == "none":
            return (0, 0, 0)
        hex_color = value.lstrip("#")
        try:
            return (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16),
            )
        except (ValueError, IndexError):
            return (0, 0, 0)

    async def async_fetch_state(self) -> dict:
        """Read the live state from the controller (GET /api/control).

        Updates the in-memory state so all entities reflect the device,
        including colors set from the Pixel Dancer app. Returns the parsed
        state dict for the coordinator.
        """
        async with self._command_lock:
            async with self.session.get(
                self._base_url,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                payload = await response.text()

        data = json.loads(payload)
        engines = data.get("e", [])
        # The integration always controls engine fxn=1
        engine = next(
            (e for e in engines if e.get("fxn") == 1),
            engines[0] if engines else {},
        )

        # Parse the six color slots (1-5 + background); pad if short
        parsed_colors = [self._parse_color(c.get("c")) for c in engine.get("colors", [])]
        while len(parsed_colors) < 6:
            parsed_colors.append((0, 0, 0))

        effect = engine.get("fx", "Off")
        self._current_effect = effect
        self._is_on = effect != "Off"
        if effect != "Off":
            self._last_effect = effect
        if "int" in engine:
            self._brightness = int(engine["int"])
        if "spd" in engine:
            self._speed = int(engine["spd"])
        self._colors = parsed_colors[:5]
        self._background_color = parsed_colors[5]
        self._trails = int(engine.get("trails", self._trails))
        self._amount = int(engine.get("amount", self._amount))
        self._spacing = int(engine.get("spacing", self._spacing))

        LOGGER.debug(
            "Fetched controller state: effect=%s is_on=%s int=%s spd=%s colors=%s bg=%s",
            self._current_effect, self._is_on, self._brightness, self._speed,
            self._colors, self._background_color,
        )
        return {
            "effect": self._current_effect,
            "is_on": self._is_on,
            "brightness": self._brightness,
            "speed": self._speed,
            "trails": self._trails,
            "amount": self._amount,
            "spacing": self._spacing,
            "colors": self._colors,
            "background_color": self._background_color,
        }

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
            self._save_persistent_state()  # Save on/off state
            # Apply current brightness and speed
            await self._send_command({"fxn": 1, "int": str(self._brightness)})
            await self._send_command({"fxn": 1, "spd": str(self._speed)})
        return result

    async def async_turn_off(self) -> bool:
        """Turn off the lights."""
        result = await self._send_command({"fxn": 1, "fx": "Off"})
        if result:
            self._is_on = False
            self._current_effect = "Off"
            self._save_persistent_state()  # Save on/off state
        return result

    async def async_set_effect(self, effect: str) -> bool:
        """Set the lighting effect."""
        if effect not in KNOWN_EFFECTS:
            LOGGER.warning("Unknown effect: %s", effect)
            return False

        # For animated effects, always sync color slots to the controller so animation is visible
        if effect not in ["Off", "Fixed Colors"]:
            if all(c == (0, 0, 0) for c in self._colors):
                LOGGER.info("All color slots black, restoring warm white before animated effect: %s", effect)
                for i in range(1, 6):
                    await self.async_set_color(i, (198, 151, 64))
            else:
                LOGGER.debug("Syncing color slots to controller for animated effect: %s", effect)
                for i, color in enumerate(self._colors, 1):
                    await self.async_set_color(i, color)

        result = await self._send_command({"fxn": 1, "fx": effect})
        if result:
            self._current_effect = effect
            self._is_on = effect != "Off"
            # Remember the last effect if it's not "Off"
            if effect != "Off":
                self._last_effect = effect
                self._save_persistent_state()  # Save to file
            # Always send speed after setting effect so animation runs at visible speed
            if effect != "Off":
                await self._send_command({"fxn": 1, "spd": str(self._speed)})
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

        if color == (0, 0, 0):
            color_str = "none"
        else:
            color_str = "#{:02x}{:02x}{:02x}".format(*color).upper()
        result = await self._send_command({
            "fxn": 1,
            "color": {"i": slot, "c": color_str}
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
        elif preset_name in MLB_PRESETS:
            preset = MLB_PRESETS[preset_name]
        elif preset_name in NHL_PRESETS:
            preset = NHL_PRESETS[preset_name]

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

        # Set background color (slot 6) - use preset value or reset to black so effects are visible
        if "background" in preset:
            hex_bg = preset["background"].lstrip("#")
            bg_rgb = tuple(int(hex_bg[j:j+2], 16) for j in (0, 2, 4))
            LOGGER.info("Setting background color to %s (RGB: %s)", hex_bg, bg_rgb)
            await self.async_set_color(6, bg_rgb)
        else:
            LOGGER.info("No background specified in preset - resetting to black for animation visibility")
            await self.async_set_color(6, (0, 0, 0))

        # Apply effect if specified in the preset
        if "effect" in preset:
            LOGGER.info("Applying preset effect: %s", preset["effect"])
            await self.async_set_effect(preset["effect"])

        LOGGER.info("Color preset %s applied successfully", preset_name)
        # Remember the last preset
        self._last_color_preset = preset_name
        self._save_persistent_state()  # Save to file
        return True


    async def async_set_overlay_effect(self, overlay: str) -> bool:
        """Set the overlay effect (Lightning, Fader, or Off)."""
        LOGGER.debug("Setting overlay effect to %s", overlay)
        result = await self._send_command({"fxn": 1, "overlay": overlay})
        if result:
            self._overlay_effect = overlay
        return result

    @property
    def overlay_effect(self) -> str:
        """Return the current overlay effect."""
        return getattr(self, '_overlay_effect', 'Off')

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
    def trails(self) -> int:
        """Return current trails value."""
        return self._trails

    @property
    def amount(self) -> int:
        """Return current amount value."""
        return self._amount

    @property
    def spacing(self) -> int:
        """Return current spacing value."""
        return self._spacing

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
        all_presets.extend(list(MLB_PRESETS.keys()))
        all_presets.extend(list(NHL_PRESETS.keys()))
        return all_presets
