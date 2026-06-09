# Minleon Lighting Integration

Control your Minleon Pixel Dancer Christmas lights directly from Home Assistant!

## ✨ New in 1.5.0

- **Live state sync** — entities reflect the controller's real effect, brightness, and colors, including changes made in the Pixel Dancer app (polls every 30s).
- **Clean restarts** — Home Assistant no longer overrides your lights on startup.
- **Real availability** — entities go *unavailable* when the controller is unreachable.
- **More reliable** — async (non-blocking) storage, shared HTTP session, and serialized requests to the controller.
- **No duplicate setups** + stricter connection test; brightness rounding fix.

## Key Features

- **Complete Effect Control**: 39+ lighting effects including Chase, Sparkle, Color Wave, Lightning, Snow, and more
- **Individual Color Management**: Control each of the 5 bulb slots plus background independently
- **Holiday & Team Presets**: Pre-configured color schemes for holidays, NFL/NBA teams, and countries
- **RGBW Support**: Full color control plus dedicated white channel options
- **Advanced Parameters**: Fine-tune effects with speed, spacing, amount, and trails controls
- **Separated Controls**: Choose colors and effects independently, just like the Pixel Dancer app

## What You Get

This integration creates multiple entities for complete control:
- Main light entity with effect selection
- Individual color controls for each bulb slot
- Color preset selector for themes
- Parameter sliders for effect customization
- Individual bulb preset dropdowns for quick color access

Perfect for creating automated holiday lighting, team color displays, and synchronized light shows!