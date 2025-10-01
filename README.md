# Minleon Lighting Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/yourusername/minleon-lighting-ha.svg)](https://github.com/yourusername/minleon-lighting-ha/releases)

A complete Home Assistant integration for Minleon Pixel Dancer Christmas lights, providing full control over effects, colors, and lighting parameters.

## Features

### 🎄 Complete Lighting Control
- **39+ Effects**: Chase, Sparkle, Color Wave, Lightning, Snow, Twinkle, and many more
- **Individual Color Control**: Set colors for each of the 5 bulb slots plus background
- **RGBW Support**: Cool white, warm white, pure white, and full RGB color control
- **Advanced Parameters**: Speed, spacing, amount, and trails sliders for fine-tuning effects

### 🎨 Color Presets & Themes
- **Holiday Presets**: Halloween, Christmas, Thanksgiving, Hanukkah, Valentine's Day, and more
- **Sports Teams**: NFL teams, NBA teams (Cleveland Cavaliers included!), soccer teams
- **Country Themes**: Flag colors for various nations
- **Quick Access**: Individual bulb color preset dropdowns for instant color changes

### 🎛️ Separated Controls (Like Pixel Dancer App)
- **Color Preset Selector**: Choose holiday/team colors without changing effects
- **Effect Selector**: Select lighting patterns independently from colors
- **Individual Bulb Controls**: Fine-tune each bulb color separately
- **Parameter Sliders**: Adjust speed (0-100), spacing (1-100), amount (1-100), trails (0-100)

## Installation

### HACS (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add this repository URL
5. Install "Minleon Lighting"
6. Restart Home Assistant

### Manual Installation
1. Download the latest release
2. Extract to `custom_components/minleon_lighting/` in your Home Assistant config directory
3. Restart Home Assistant

## Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Minleon Lighting"
4. Enter your Pixel Dancer controller's IP address
5. The integration will create all entities automatically

## Entities Created

### Main Light Entity
- **Minleon Christmas Lights**: Main control with effects dropdown

### Individual Color Controls
- **Color Bulb 1-5**: Individual bulb color controls
- **Color Background**: Background color control

### Color Preset Selectors
- **Color Preset**: Holiday/team color themes
- **Effect**: Lighting effect patterns
- **Bulb 1-5 Preset**: Individual bulb color presets (Cool White, Warm White, etc.)

### Parameter Controls
- **Speed**: Effect speed (0-100%)
- **Spacing**: Effect spacing (1-100)
- **Amount**: Effect amount (1-100, certain effects only)
- **Trails**: Effect trails (0-100, certain effects only)

## Usage Examples

### Basic Control
```yaml
# Turn on with Christmas colors and chase effect
- service: select.select_option
  target:
    entity_id: select.minleon_pixel_dancer_controller_color_preset
  data:
    option: "Christmas"
- service: select.select_option
  target:
    entity_id: select.minleon_pixel_dancer_controller_effect
  data:
    option: "Chase"
- service: light.turn_on
  target:
    entity_id: light.minleon_christmas_lights
```

### Automation Example
```yaml
- alias: "Halloween Lights at Dusk"
  trigger:
    - platform: sun
      event: sunset
      offset: "-00:30:00"
  condition:
    - condition: template
      value_template: "{{ now().month == 10 }}"
  action:
    - service: select.select_option
      target:
        entity_id: select.minleon_pixel_dancer_controller_color_preset
      data:
        option: "Halloween"
    - service: select.select_option
      target:
        entity_id: select.minleon_pixel_dancer_controller_effect
      data:
        option: "Sparkle"
    - service: light.turn_on
      target:
        entity_id: light.minleon_christmas_lights
      data:
        brightness: 255
```

## Supported Devices

This integration works with Minleon Pixel Dancer controllers that have a web interface accessible via HTTP. The integration communicates directly with the controller on your local network.

### Tested Hardware
- Minleon Pixel Dancer Controller (Web UI version)
- RGBW LED light strings

## Reverse Engineering Credits

This integration was created through reverse engineering of the Pixel Dancer mobile app and web interface using network packet capture analysis. The API commands and color formatting were discovered through careful analysis of HTTP traffic between the app and controller.

## Technical Details

### API Communication
- **Protocol**: HTTP POST requests to `/api/control`
- **Format**: JSON payloads with specific command structure
- **Content-Type**: `text/plain;charset=UTF-8` (critical for compatibility)

### Color Format
- **Individual Colors**: 6-digit hex RGB (`#RRGGBB`)
- **RGBW Presets**: 8-digit hex with white channel (`#RRGGBBWW`)
- **Command Structure**: `{"fxn": 1, "color": {"i": slot, "c": color}}`

### Effect Parameters
- **Effects**: `{"fxn": 1, "fx": "Effect Name"}`
- **Speed**: `{"fxn": 1, "spd": "0-100"}`
- **Brightness**: `{"fxn": 1, "int": "0-100"}`
- **Spacing**: `{"fxn": 1, "spacing": "1-100"}`
- **Amount**: `{"fxn": 1, "amount": "1-100"}`
- **Trails**: `{"fxn": 1, "trails": "0-100"}`

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
1. Clone this repository
2. Copy to your Home Assistant `custom_components/` directory
3. Restart Home Assistant
4. Test your changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not affiliated with or endorsed by Minleon. It is a community-created integration based on reverse engineering of publicly available API endpoints.