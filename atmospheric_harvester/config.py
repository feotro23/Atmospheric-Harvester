import os

# Window Settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 60
TITLE = "Atmospheric Harvester"

# API Settings
# Replace with your actual key or set via environment variable
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
USE_MOCK_DATA = True  # Set to False when you have a valid API key

# Game Settings
DEFAULT_LAT = 40.7128  # New York
DEFAULT_LON = -74.0060
POLL_INTERVAL = 600  # Seconds (10 minutes)
