"""Constants for minleon-lighting integration."""

from datetime import timedelta
import logging

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=30)

# Base component constants
NAME = "Minleon Pixel Dancer Lighting"
DEVICE = "Minleon Controller"
DOMAIN = "minleon_lighting"
DOMAIN_DATA = f"{DOMAIN}_data"

# Icons
ICON = "mdi:led-strip-variant"

# Platforms
LIGHT = "light"

# Configuration and options
CONF_ADDRESS = "host"
CONF_NAME = "name"
DEFAULT_BRIGHTNESS = 75
DEFAULT_COLOR = (255, 0, 0)  # Red

# Known working effects from your testing
KNOWN_EFFECTS = [
    "Off",
    "Fixed Colors",
    "Chase",
    "Sparkle",
    "Color Wave",
    "Lightning",
    "Glow",
    "Pulsate",
    "Ping Pong",
    "Snow",
    "Blend",
    "Paint",
    "Expand",
    "Shift",
    "Show",
    "Twist",
    "Worms",
    "Bands",
    "Bars",
    "Circles",
    "Fader",
    "Markers",
    "Test",
    # Newly discovered effects
    "Rainbow",
    "Theater",
    "Strobe",
    "Meteor",
    "Fire",
    "Twinkle",
    "Fade",
    "Breathe",
    "Scanner",
    "Comet",
    "Fireworks",
    "Rain",
    "Christmas Tree",
    "Candy Cane",
    "Icicle",
    "Stars"
]

# Holiday presets from Pixel Dancer app
HOLIDAY_PRESETS = {
    "New Year": {"colors": ["#FFD700", "#FEFFFF"]},
    "Valentines Day": {"colors": ["#E63B7A", "#F4A4C0"]},
    "St Patricks Day": {"colors": ["#008000", "#FEFFFF"]},
    "Mardi Gras": {"colors": ["#008000", "#800080", "#FFFF00"]},
    "Easter": {"colors": ["#FFC0CB", "#800080", "#FFFF00"]},
    "Earth Day": {"colors": ["#00FF00", "#0000FF"]},
    "Independence Day": {"colors": ["#FF0000", "#FEFFFF", "#0000FF"]},
    "Halloween": {"colors": ["#FF7F00", "#800080", "#008000"]},
    "Thanksgiving": {"colors": ["#FF0000", "#FFA500", "#FFFF00"]},
    "Christmas": {"colors": ["#FF0000", "#00FF00", "#FEFFFF"]},
    "Hanukkah": {"colors": ["#FEFFFF", "#0000FF"]},
    "Kwanzaa": {"colors": ["#FF0000", "#FEDF00"]}
}

# NFL Team presets
NFL_PRESETS = {
    "Arizona Cardinals": {"colors": ["#EFCA15", "#FF0000", "#002868", "#CE5C17"]},
    "Atlanta Falcons": {"colors": ["#FF0000", "#002868", "#FFFFFE"]},
    "Baltimore Ravens": {"colors": ["#000000", "#EFCA15", "#FF0000"]},
    "Buffalo Bills": {"colors": ["#002A86", "#F3CC1B", "#4E9DD2", "#C6762F"]},
    "Carolina Panthers": {"colors": ["#4E9DD2"]},
    "Chicago Bears": {"colors": ["#FF0000", "#000000", "#FFFFFE"]},
    "Cincinnati Bengals": {"colors": ["#DA251D", "#000000"]},
    "Cleveland Browns": {"colors": ["#EFCA15", "#DA251D", "#002A86"]},
    "Dallas Cowboys": {"colors": ["#0000EC", "#815300"]},
    "Denver Broncos": {"colors": ["#FF7F00", "#FFFFFE"]},
    "Detroit Lions": {"colors": ["#002673", "#C70E2E", "#F5DC0F", "#FFFFFE"]},
    "Green Bay Packers": {"colors": ["#002A86", "#FFFFFE", "#01633C"]},
    "Houston Texans": {"colors": ["#FF0000"]},
    "Indianapolis Colts": {"colors": ["#010E5D", "#F5DC0F"]},
    "Jacksonville Jaguars": {"colors": ["#FF0000", "#F5DC0F"]},
    "Kansas City Chiefs": {"colors": ["#F5DC0F", "#00450E"]},
    "Miami Dolphins": {"colors": ["#C70F2E", "#000000"]},
    "Minnesota Vikings": {"colors": ["#FFFFFE", "#3D68C9"]},
    "New Orleans Saints": {"colors": ["#F5DC0F", "#FF0000", "#3D68C9"]},
    "New York Giants": {"colors": ["#BE8225", "#FFFFFE", "#592B20", "#7B7B7B"]},
    "Oakland Raiders": {"colors": ["#592B20"]},
    "Philadelphia Eagles": {"colors": ["#010E5D", "#F5DC0F"]},
    "Pittsburgh Steelers": {"colors": ["#042A57", "#CEBC72", "#D4DDE1", "#FFFFFE"]},
    "San Diego Chargers": {"colors": ["#AA0000", "#FFCC00", "#FFFFFE"]},
    "San Francisco 49ers": {"colors": ["#FFCC00"]},
    "Seattle Seahawks": {"colors": ["#009E3C"]},
    "St Louis Rams": {"colors": ["#F3E6B3", "#0094DE", "#006E2B", "#A51C15"]},
    "Tampa Bay Buccaneers": {"colors": ["#002655", "#FFFFFE"]},
    "Tennessee Titans": {"colors": ["#CC0000", "#002D65", "#FFFFFE"]},
    "Washington Commanders": {"colors": ["#008457", "#FFD520", "#34C2DE", "#000000"]}
}

# Country Flag presets
NATION_PRESETS = {
    "Argentina": {"colors": ["#F5EC00", "#FFFFFE", "#52D6FC"]},
    "Australia": {"colors": ["#FF0000", "#FFFFFE", "#0000FF"]},
    "Belgium": {"colors": ["#000000", "#FFFF00", "#FF0000"]},
    "Brazil": {"colors": ["#00FF00", "#FEDF00", "#0000FF"]},
    "Canada": {"colors": ["#FF0000", "#FFFFFE"]},
    "Chile": {"colors": ["#FE0000", "#0100CF", "#FFFFFE"]},
    "China": {"colors": ["#FF0000", "#FFFF00"]},
    "Colombia": {"colors": ["#FF0000", "#013893", "#FDD116"]},
    "Finland": {"colors": ["#0024C7", "#FFFFFE"]},
    "France": {"colors": ["#0000FF", "#FFFFFE", "#FF0000"]},
    "Germany": {"colors": ["#FECE00", "#DC0000", "#000000"]},
    "Greece": {"colors": ["#029FE8", "#FEFEFC"]},
    "Indonesia": {"colors": ["#FE0000", "#FFFFFE"]},
    "Iran": {"colors": ["#00FF00", "#FFFFFE", "#DA0000"]},
    "Italy": {"colors": ["#00FF00", "#FFFFFE", "#FF0000"]},
    "Japan": {"colors": ["#FF0000", "#FFFFFE"]},
    "Lebanon": {"colors": ["#FF0000", "#FEFEFE", "#00FF00"]},
    "Malaysia": {"colors": ["#FF0000", "#08399C", "#FFDE00", "#FFFFFE"]},
    "Mexico": {"colors": ["#006847", "#FFFFFE", "#FF0000"]},
    "Netherlands": {"colors": ["#FF0000", "#FFFFFE", "#00329B"]},
    "New Zealand": {"colors": ["#00247D", "#FF0000", "#FFFFFE"]},
    "Norway": {"colors": ["#FF0000", "#FFFFFE", "#0000FF"]},
    "Peru": {"colors": ["#FE0000", "#FFFFFE"]},
    "Russia": {"colors": ["#FFFFFE", "#0000FE", "#FE0000"]},
    "Saudi Arabia": {"colors": ["#00FF00", "#8FC3AF"]},
    "Singapore": {"colors": ["#FF0000", "#F3F3F7"]},
    "South Africa": {"colors": ["#FFAB01", "#00FF00", "#FFFFFE", "#FF0000", "#0000FF"]},
    "Spain": {"colors": ["#DB000D", "#FBEA0E"]},
    "Sweden": {"colors": ["#0983F0", "#FFFF00"]},
    "Thailand": {"colors": ["#FD0102", "#FFFFFE", "#000097"]},
    "United Kingdom": {"colors": ["#0000FF", "#FF0000", "#FFFFFE"]},
    "United States": {"colors": ["#FF0000", "#FFFFFE", "#0000FF"]}
}

# Soccer Team presets
SOCCER_PRESETS = {
    "Arsenal": {"colors": ["#FF0000", "#FFFFFE"]},
    "Aston Villa": {"colors": ["#FFD520", "#FF0000", "#6D76B3"]},
    "Cardiff City": {"colors": ["#FF0000", "#EFD413", "#FFFFFE", "#0000FF"]},
    "Chelsea": {"colors": ["#0000FF", "#FFFFFE"]},
    "Crystal Palace": {"colors": ["#013BD0", "#FFFFFE", "#AEAEAE", "#FF0000"]},
    "Everton": {"colors": ["#0000FF", "#FFFFFE"]},
    "Fulham": {"colors": ["#FF0000", "#FFFFFE"]},
    "Hull City": {"colors": ["#FAA619", "#FFFFFE"]},
    "Liverpool": {"colors": ["#E1040D", "#0000EC", "#FFFFFE"]},
    "Manchester City": {"colors": ["#B9B810", "#115D9B", "#FFFFFE", "#000000"]},
    "Manchester United": {"colors": ["#FF0000", "#FFFF00"]},
    "Newcastle United": {"colors": ["#D6D7D9", "#12B2DE", "#EBCD7C"]},
    "Norwich City": {"colors": ["#FFF300", "#00FF00"]},
    "Southampton": {"colors": ["#FF0700", "#FFFFFE", "#FDEC2E", "#00FF00"]},
    "Stoke City": {"colors": ["#F90103", "#10127F", "#FFFFFE"]},
    "Sunderland": {"colors": ["#000000", "#F10400", "#C4BC00"]},
    "Swansea City": {"colors": ["#000000", "#FFFFFE"]},
    "Tottenham Hotspur": {"colors": ["#FFFFFE", "#00015F"]},
    "West Bromwich Albion": {"colors": ["#38377F", "#8B5F37"]},
    "West Ham United": {"colors": ["#FAD31D", "#901F4E"]}
}

# Australian Football presets
AUSTRALIAN_FOOTBALL_PRESETS = {
    "Brisbane Broncos": {"colors": ["#650038", "#FCCC3B"]},
    "Canberra Raiders": {"colors": ["#01A750", "#5F707C"]},
    "Canterbury-Bankstown Bulldogs": {"colors": ["#00458C", "#FFFFFE"]},
    "Cronulla-Sutherland Sharks": {"colors": ["#008FC5", "#000000", "#FFFFFE"]},
    "Gold Coast Titans": {"colors": ["#FFAB01", "#00A9E7", "#FFFFFE"]},
    "Manly-Warringah Sea Eagles": {"colors": ["#69143B", "#FCFCFC"]},
    "Melbourne Storm": {"colors": ["#64027B", "#E9C01A", "#070D51"]},
    "New Zealand Warriors": {"colors": ["#008752", "#FFFFFE", "#000000"]},
    "Newcastle Knights": {"colors": ["#EE3124", "#000000", "#0055A5", "#FFFFFE"]},
    "North Queensland Cowboys": {"colors": ["#FFDE00", "#001949"]},
    "Parramatta Eels": {"colors": ["#012C92", "#FFD001", "#FFFFFE"]},
    "Penrith Panthers": {"colors": ["#231F20", "#006F83", "#A82D45"]},
    "South Sydney Rabbitohs": {"colors": ["#00582D", "#CB1B22", "#FFFFFE"]},
    "St. George Illawarra Dragons": {"colors": ["#000000", "#D92B1C", "#FFFDFE"]},
    "Sydney Roosters": {"colors": ["#EE3124", "#003A74", "#FFFFFE", "#F8CE50"]},
    "Wests Tigers": {"colors": ["#F6831F", "#EEEFEF"]}
}

# NBA Team presets
NBA_PRESETS = {
    "Cleveland Cavaliers": {"colors": ["#6F263D", "#FFB81C"]}
}

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Custom integration for Minleon Pixel Dancer Christmas lights
Based on reverse engineering of the Pixel Dancer mobile app
-------------------------------------------------------------------
"""