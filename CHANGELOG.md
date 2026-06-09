# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-06-09

Makes the integration aware of the controller's **real state** instead of only
tracking what Home Assistant last sent it.

### Added
- **Live state readback** via a `DataUpdateCoordinator` that polls
  `GET /api/control` every 30 seconds. Entities now reflect the controller's
  actual effect, brightness, speed, and colors — **including colors set from
  the Pixel Dancer app**, which were previously invisible to Home Assistant.
- **Real availability**: entities report *Unavailable* when the controller
  cannot be reached (driven by the coordinator), instead of always appearing online.
- Unique ID from the controller's UUID, preventing the same device from being
  added twice.

### Changed
- Persistence moved to Home Assistant's async `Store` (no more blocking file
  I/O on the event loop). Existing state migrates automatically from the legacy
  JSON file on first start.
- The integration no longer pushes state to the controller on startup; an HA
  restart no longer overrides the device's current scene.
- Uses Home Assistant's shared aiohttp client session
  (`async_get_clientsession`) instead of a self-managed session.
- All light/number/select entities are now `CoordinatorEntity`-based.
- Serialized device requests with an `asyncio.Lock` so commands and polls never
  overlap on the single-threaded controller.
- Stricter setup connection test (verifies `/api/status` rather than accepting
  any HTTP response below 500).

### Fixed
- Brightness no longer drifts on round-trips (rounds instead of truncating).

### Removed
- Dead code: the unused per-slot RGBW preset selector (which had a white-channel
  bug) and an unused internal helper class. Leftover config-flow auth scaffolding.

## [1.4.0] - 2025-10-04

### Added
- RGB color pickers and overlay effects.
- NBA, MLB, and NHL team color presets (joining the existing NFL, soccer, and
  nation presets).

## [1.3.1] - 2025-10-02

### Fixed
- Physical light state restoration on Home Assistant reboot.

## [1.3.0] - 2025-10-02

### Added
- On/off state restoration across reboots.

## [1.2.2] - 2025-10-01

### Fixed
- Persistent state initialization.

## [1.2.0] - 2025-10-01

### Added
- Persistent state storage for last-used preset/effect.

## [1.1.0] - 2025-10-01

### Added
- State persistence.

## [1.0.0] - 2025-10-01

- Initial release of the Minleon Lighting integration: effects, individual
  color slots, holiday/team color presets, and effect parameter controls.

[1.5.0]: https://github.com/burdurboy05/minleon-lighting-ha/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/burdurboy05/minleon-lighting-ha/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/burdurboy05/minleon-lighting-ha/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/burdurboy05/minleon-lighting-ha/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/burdurboy05/minleon-lighting-ha/compare/v1.2.0...v1.2.2
[1.2.0]: https://github.com/burdurboy05/minleon-lighting-ha/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/burdurboy05/minleon-lighting-ha/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/burdurboy05/minleon-lighting-ha/releases/tag/v1.0.0
