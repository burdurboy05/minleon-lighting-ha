"""DataUpdateCoordinator for the minleon-lighting integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MinleonLightingApiClient
from .const import DOMAIN, LOGGER, SCAN_INTERVAL


class MinleonDataUpdateCoordinator(DataUpdateCoordinator):
    """Poll the Minleon controller for its live state.

    The controller exposes its full state via ``GET /api/control`` (effect,
    brightness, speed, trails, amount, spacing and all six color slots,
    including colors set from the Pixel Dancer app). This coordinator reads
    that endpoint on ``SCAN_INTERVAL`` and refreshes the API client's
    in-memory state so every entity reflects what the device is actually
    doing rather than only what Home Assistant last sent.
    """

    def __init__(self, hass: HomeAssistant, api: MinleonLightingApiClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch the latest state from the controller."""
        try:
            return await self.api.async_fetch_state()
        except Exception as ex:  # noqa: BLE001 - surfaced as UpdateFailed
            raise UpdateFailed(f"Error fetching Minleon state: {ex}") from ex
