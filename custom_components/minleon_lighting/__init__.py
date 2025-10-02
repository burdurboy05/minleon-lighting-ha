"""The minleon-lighting integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import MinleonLightingApiClient
from .const import DOMAIN, LOGGER

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.NUMBER, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up minleon-lighting from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API client
    api = MinleonLightingApiClient(
        address=entry.data["host"],
        config_entry=entry,
        hass=hass
    )

    # Test connection
    if not await api.async_test_connection():
        return False

    # Initialize state file and load persistent state
    api._ensure_state_file()

    # Restore physical light state if lights were on before reboot
    if api.is_on and api.current_effect != "Off":
        LOGGER.info("Restoring lights to ON state with effect: %s", api.current_effect)
        await api.async_turn_on()

    hass.data[DOMAIN][entry.entry_id] = api

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        api = hass.data[DOMAIN].pop(entry.entry_id)
        await api.async_close()

    return unload_ok
